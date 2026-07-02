from decimal import Decimal

from rest_framework import serializers
from django.db import transaction
from .models import FactoryDelivery, DeliveryItem, DeliveryStatus, DiscrepancyType
from apps.shipments.models import Shipment
from apps.products.models import Product
from shared.exceptions import AppException


class DeliveryItemSerializer(serializers.ModelSerializer):
    """
    Сериализатор для позиций приёмки (ожидаемые vs фактические количества)
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_barcode = serializers.CharField(source='product.barcode', read_only=True)
    discrepancy_type_display = serializers.CharField(source='get_discrepancy_type_display', read_only=True)

    class Meta:
        model = DeliveryItem
        fields = [
            'id', 'delivery_id', 'product_id', 'product_name', 'product_barcode',
            'expected_qty', 'actual_qty', 'discrepancy_type', 'discrepancy_type_display',
            'discrepancy_qty', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'discrepancy_type', 'discrepancy_qty']


class OfflineReceptionItemSerializer(serializers.Serializer):
    barcode = serializers.CharField(max_length=100)
    actualQty = serializers.IntegerField(min_value=0)
    factoryPrice = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0'))


class OfflineReceptionSerializer(serializers.Serializer):
    warehouseId = serializers.UUIDField()
    createdAt = serializers.DateTimeField()
    clientId = serializers.UUIDField()
    items = OfflineReceptionItemSerializer(many=True, allow_empty=False)


class FactoryDeliverySerializer(serializers.ModelSerializer):
    """
    Сериализатор для поставки (приёмки) от завода
    """
    items = DeliveryItemSerializer(many=True, read_only=True)
    shipment_number = serializers.CharField(source='shipment.id', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    warehouse_name = serializers.SerializerMethodField()
    
    class Meta:
        model = FactoryDelivery
        fields = [
            'id', 'shipment_id', 'shipment_number', 'warehouse_id', 'warehouse_name',
            'delivery_number', 'delivered_at', 'status', 'status_display',
            'total_amount', 'created_by', 'created_at', 'updated_at', 'items'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_amount']
    
    def get_warehouse_name(self, obj):
        """
        Получение названия склада (можно из отдельной таблицы Warehouse,
        пока возвращаем ID)
        """
        # В будущем: Warehouse.objects.get(id=obj.warehouse_id).name
        return str(obj.warehouse_id)


class CreateDeliverySerializer(serializers.Serializer):
    """
    Сериализатор для создания новой поставки (привязка к отгрузке)
    Используется при POST /api/factory/reception
    """
    shipment_id = serializers.UUIDField(required=True)
    warehouse_id = serializers.UUIDField(required=True)
    delivery_number = serializers.CharField(max_length=100, required=True)
    delivered_at = serializers.DateTimeField(required=True)
    
    def validate_shipment_id(self, value):
        """Проверяем, что отгрузка существует и ещё не принята"""
        try:
            shipment = Shipment.objects.get(id=value)
            if shipment.status in ['accepted', 'accepted_with_discrepancy']:
                raise serializers.ValidationError("Эта отгрузка уже была принята")
            return value
        except Shipment.DoesNotExist:
            raise AppException(
                status_code=404,
                error_code="shipment_not_found",
                message=f"Shipment with ID '{value}' not found"
            )
    
    def validate_delivery_number(self, value):
        """Проверяем уникальность номера поставки"""
        if FactoryDelivery.objects.filter(delivery_number=value).exists():
            raise serializers.ValidationError("Поставка с таким номером уже существует")
        return value
    
    def validate(self, data):
        """Дополнительная валидация: warehouse_id должен совпадать с отгрузкой"""
        try:
            shipment = Shipment.objects.get(id=data['shipment_id'])
        except Shipment.DoesNotExist:
            raise AppException(
                status_code=404,
                error_code="shipment_not_found",
                message=f"Shipment with ID '{data['shipment_id']}' not found"
            )
        if str(shipment.warehouse_id) != str(data['warehouse_id']):
            raise serializers.ValidationError(
                "Склад-получатель не совпадает со складом в отгрузке"
            )
        return data
    
    def create(self, validated_data):
        """Создаём поставку и автоматически создаём позиции из отгрузки"""
        shipment = Shipment.objects.get(id=validated_data['shipment_id'])
        
        # Создаём поставку
        delivery = FactoryDelivery.objects.create(
            shipment=shipment,
            warehouse_id=validated_data['warehouse_id'],
            delivery_number=validated_data['delivery_number'],
            delivered_at=validated_data['delivered_at'],
            status=DeliveryStatus.PENDING,
            total_amount=shipment.total_amount,  # пока полная сумма, при приёмке пересчитается
            created_by=self.context['request'].user
        )
        
        # Создаём позиции поставки на основе позиций отгрузки
        for shipment_item in shipment.items.all():
            DeliveryItem.objects.create(
                delivery=delivery,
                product=shipment_item.product,
                expected_qty=shipment_item.qty_boxes * shipment_item.product.pieces_per_box + shipment_item.qty_pieces,
                actual_qty=None,  # пока не принято
                discrepancy_type=DiscrepancyType.NONE,
                discrepancy_qty=0
            )
        
        return delivery


class AcceptFullSerializer(serializers.Serializer):
    """
    Сериализатор для полной приёмки (без расхождений)
    """
    comment = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate(self, data):
        """Проверяем, что поставка ещё не принята"""
        delivery_id = self.context.get('delivery_id')
        try:
            delivery = FactoryDelivery.objects.get(id=delivery_id)
            if delivery.status != DeliveryStatus.PENDING:
                raise serializers.ValidationError(
                    f"Поставка уже обработана, текущий статус: {delivery.status}"
                )
        except FactoryDelivery.DoesNotExist:
            raise AppException(
                status_code=404,
                error_code="delivery_not_found",
                message=f"Delivery with ID '{delivery_id}' not found"
            )
        return data


class AcceptPartialItemSerializer(serializers.Serializer):
    """
    Сериализатор для одной позиции при частичной приёмке
    """
    id = serializers.UUIDField(required=True)
    actual_qty = serializers.IntegerField(min_value=0, required=True)


class AcceptPartialSerializer(serializers.Serializer):
    """
    Сериализатор для частичной приёмки (с расхождениями)
    Ожидает список позиций с фактическими количествами
    """
    items = AcceptPartialItemSerializer(many=True, required=True)
    comment = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate_items(self, value):
        """Проверяем, что все ID позиций существуют и принадлежат этой поставке"""
        delivery_id = self.context.get('delivery_id')
        item_ids = [item['id'] for item in value]
        
        # Проверяем существование позиций
        existing_items = DeliveryItem.objects.filter(
            id__in=item_ids, 
            delivery_id=delivery_id
        )
        existing_ids = set(str(item.id) for item in existing_items)
        
        missing_ids = set(str(id_) for id_ in item_ids) - existing_ids
        if missing_ids:
            raise serializers.ValidationError(
                f"Позиции с ID {missing_ids} не найдены в этой поставке"
            )
        
        # Проверяем, что фактическое количество не превышает ожидаемое (опционально)
        for item_data in value:
            delivery_item = DeliveryItem.objects.get(id=item_data['id'])
            if item_data['actual_qty'] > delivery_item.expected_qty:
                # Можно разрешить излишек, но предупредить
                pass
        
        return value


class DeliveryStatusSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления статуса поставки (обычно не используется напрямую,
    статус меняется через accept/accept-partial)
    """
    class Meta:
        model = FactoryDelivery
        fields = ['id', 'status', 'status_display']
        read_only_fields = ['id']
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)


class DeliveryDiscrepancySerializer(serializers.Serializer):
    """
    Сериализатор для отображения расхождений по поставке (для отчётов)
    """
    delivery_id = serializers.UUIDField()
    delivery_number = serializers.CharField()
    total_expected = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_actual = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_shortage = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_surplus = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_defect = serializers.DecimalField(max_digits=14, decimal_places=2)
    items = DeliveryItemSerializer(many=True)
