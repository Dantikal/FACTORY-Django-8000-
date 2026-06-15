from rest_framework import serializers
from .models import Shipment, ShipmentItem

class ShipmentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = ['id', 'product_id', 'qty_boxes', 'qty_pieces', 'price', 'total']
        read_only_fields = ['price', 'total']

class ShipmentSerializer(serializers.ModelSerializer):
    items = ShipmentItemSerializer(many=True, read_only = True)
    class Meta:
        model = Shipment
        fields = '__all__'
        read_only_fields = ['id', 'create_at', 'updated_at', 'total_amout']

class ShipmentStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=ShipmentStatus.choices)