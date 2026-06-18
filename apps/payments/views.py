from uuid import UUID

from rest_framework import generics
from rest_framework.exceptions import NotFound, ValidationError

from .models import FactoryPayment, WarehouseDebt
from .serializers import FactoryPaymentSerializer, WarehouseDebtSerializer
from shared.permissions import IsAccountant


class FactoryPaymentListView(generics.ListCreateAPIView):
    queryset = FactoryPayment.objects.all().order_by('-paid_at')
    serializer_class = FactoryPaymentSerializer
    permission_classes = [IsAccountant]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class WarehouseDebtView(generics.RetrieveAPIView):
    serializer_class = WarehouseDebtSerializer
    permission_classes = [IsAccountant]

    def get_object(self):
        warehouse_id = self.request.query_params.get('warehouse_id')

        if not warehouse_id:
            raise ValidationError({'warehouse_id': 'This query parameter is required.'})

        try:
            warehouse_uuid = UUID(warehouse_id)
        except ValueError:
            raise ValidationError({'warehouse_id': 'Invalid UUID.'})

        try:
            return WarehouseDebt.objects.get(warehouse_id=warehouse_uuid)
        except WarehouseDebt.DoesNotExist:
            raise NotFound('Warehouse debt not found.')


class WarehouseDebtAllView(generics.ListAPIView):
    queryset = WarehouseDebt.objects.all().order_by('-amount')
    serializer_class = WarehouseDebtSerializer
    permission_classes = [IsAccountant]
    pagination_class = None
