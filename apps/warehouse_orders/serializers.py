from rest_framework import serializers

from apps.products.models import Product
from .models import WarehouseOrder, WarehouseOrderItem, WarehouseOrderStatus


class WarehouseOrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.CharField(read_only=True)
    productId = serializers.CharField(source='product_id', read_only=True)

    class Meta:
        model = WarehouseOrderItem
        fields = ['id', 'product_id', 'productId', 'qty', 'created_at']
        read_only_fields = fields


class WarehouseOrderSerializer(serializers.ModelSerializer):
    items = WarehouseOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = WarehouseOrder
        fields = [
            'id',
            'warehouse_id',
            'status',
            'comment',
            'created_by',
            'created_at',
            'updated_at',
            'items',
        ]
        read_only_fields = fields


class WarehouseOrderCreateItemSerializer(serializers.Serializer):
    productId = serializers.CharField(required=False, write_only=True)
    product_id = serializers.CharField(required=False, write_only=True)
    qty = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        product_id = attrs.get('productId') or attrs.get('product_id')
        if not product_id:
            raise serializers.ValidationError({'productId': 'This field is required.'})

        try:
            product = Product.objects.get(id=product_id)
        except (Product.DoesNotExist, TypeError, ValueError):
            raise serializers.ValidationError({'productId': 'Product not found.'})

        return {
            'product': product,
            'qty': attrs['qty'],
        }


class WarehouseOrderCreateSerializer(serializers.Serializer):
    items = WarehouseOrderCreateItemSerializer(many=True, allow_empty=False)
    comment = serializers.CharField(required=False, allow_blank=True, default='')


class WarehouseOrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=WarehouseOrderStatus.choices)
