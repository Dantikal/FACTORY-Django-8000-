from rest_framework import serializers

from .models import Invoice, InvoiceItem


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ['id', 'product_id', 'qty', 'price', 'total']
        read_only_fields = ['id', 'product_id', 'qty', 'price', 'total']


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id',
            'dispatch_id',
            'driver_id',
            'warehouse_id',
            'total_amount',
            'created_at',
            'updated_at',
            'items',
        ]
        read_only_fields = fields
