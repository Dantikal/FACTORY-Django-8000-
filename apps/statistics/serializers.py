from rest_framework import serializers


class CountryStatsSerializer(serializers.Serializer):
    total_shipments = serializers.IntegerField()
    total_deliveries = serializers.IntegerField()
    accepted_deliveries = serializers.IntegerField()
    pending_deliveries = serializers.IntegerField()
    total_payments = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_debt = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_sales = serializers.DecimalField(max_digits=14, decimal_places=2)
    active_products = serializers.IntegerField()


class WarehouseStatsSerializer(serializers.Serializer):
    warehouse_id = serializers.UUIDField()
    total_shipments = serializers.IntegerField()
    total_deliveries = serializers.IntegerField()
    accepted_deliveries = serializers.IntegerField()
    pending_deliveries = serializers.IntegerField()
    total_payments = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_debt = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_sales = serializers.DecimalField(max_digits=14, decimal_places=2)


class TopProductSerializer(serializers.Serializer):
    product_id = serializers.CharField()
    name = serializers.CharField()
    barcode = serializers.CharField()
    quantity = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=14, decimal_places=2)
