from rest_framework import serializers

from .models import FactoryPayment, WarehouseDebt


class FactoryPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactoryPayment
        fields = '__all__'
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')


class WarehouseDebtSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarehouseDebt
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
