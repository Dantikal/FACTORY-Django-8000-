from rest_framework import serializers
from .models import Shipment, ShipmentItem, ShipmentStatus  # добавлен импорт ShipmentStatus

class ShipmentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentItem  # ИСПРАВЛЕНО: было Shipment, должно быть ShipmentItem
        fields = ['id', 'product_id', 'qty_boxes', 'qty_pieces', 'price', 'total']
        read_only_fields = ['price', 'total']

class ShipmentSerializer(serializers.ModelSerializer):
    items = ShipmentItemSerializer(many=True, read_only=True)  # убраны пробелы
    class Meta:
        model = Shipment
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_amount']  # ИСПРАВЛЕНО: total_amount (было total_amout), created_at (было create_at)

class ShipmentStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=ShipmentStatus.choices)  # теперь ShipmentStatus определен