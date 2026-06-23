from rest_framework import generics, status
from rest_framework.response import Response

from shared.permissions import IsFactory
from .models import WarehouseOrder
from .permissions import WarehouseOrderPermission
from .serializers import (
    WarehouseOrderCreateSerializer,
    WarehouseOrderSerializer,
    WarehouseOrderStatusUpdateSerializer,
)
from .services import WarehouseOrderService


class WarehouseOrderListCreateView(generics.ListCreateAPIView):
    serializer_class = WarehouseOrderSerializer
    permission_classes = [WarehouseOrderPermission]
    filterset_fields = ['warehouse_id', 'status']

    def get_queryset(self):
        queryset = (
            WarehouseOrder.objects
            .select_related('created_by')
            .prefetch_related('items__product')
            .order_by('-created_at')
        )

        if self.request.user.role == 'warehouse_manager':
            if not self.request.user.warehouse_id:
                return queryset.none()
            return queryset.filter(warehouse_id=self.request.user.warehouse_id)

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = WarehouseOrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = WarehouseOrderService.create_order(
            items=serializer.validated_data['items'],
            comment=serializer.validated_data.get('comment', ''),
            created_by=request.user,
        )
        response_serializer = self.get_serializer(order)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class WarehouseOrderDetailView(generics.RetrieveAPIView):
    serializer_class = WarehouseOrderSerializer
    permission_classes = [WarehouseOrderPermission]
    lookup_field = 'id'

    def get_queryset(self):
        queryset = (
            WarehouseOrder.objects
            .select_related('created_by')
            .prefetch_related('items__product')
        )

        if self.request.user.role == 'warehouse_manager':
            if not self.request.user.warehouse_id:
                return queryset.none()
            return queryset.filter(warehouse_id=self.request.user.warehouse_id)

        return queryset


class WarehouseOrderStatusUpdateView(generics.GenericAPIView):
    serializer_class = WarehouseOrderStatusUpdateSerializer
    permission_classes = [IsFactory]
    lookup_field = 'id'

    def put(self, request, *args, **kwargs):
        order_id = kwargs['id']
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order, shipment = WarehouseOrderService.update_status(
            order_id=order_id,
            new_status=serializer.validated_data['status'],
            updated_by=request.user,
        )

        response = {'status': order.status}
        if shipment:
            response['shipment_id'] = str(shipment.id)
        return Response(response)
