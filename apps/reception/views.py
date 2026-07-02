from rest_framework import generics, status  # Исправлено: starus → status
from rest_framework.permissions import BasePermission
from rest_framework.response import Response  # Исправлено: Responce → Response
from .models import FactoryDelivery
from .serializers import (
    FactoryDeliverySerializer,
    AcceptPartialItemSerializer,
    OfflineReceptionSerializer,
)
from .services import ReceptionService
from shared.permissions import IsFactory


class IsFactoryOrWarehouseManager(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ('admin', 'factory', 'warehouse_manager')
        )


class ReceptionListCreateView(generics.ListCreateAPIView):
    queryset = FactoryDelivery.objects.all().order_by('-delivered_at')
    serializer_class = FactoryDeliverySerializer
    permission_classes = [IsFactory]


class ReceptionDetailView(generics.RetrieveAPIView):  # Исправлено: DetilView → DetailView
    queryset = FactoryDelivery.objects.all()
    serializer_class = FactoryDeliverySerializer
    permission_classes = [IsFactory]


class OfflineReceptionView(generics.GenericAPIView):
    permission_classes = [IsFactoryOrWarehouseManager]
    serializer_class = OfflineReceptionSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        delivery, created = ReceptionService.create_offline(serializer.validated_data, request.user)
        response_serializer = FactoryDeliverySerializer(delivery)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class AcceptFullView(generics.GenericAPIView):
    permission_classes = [IsFactory]
    def post(self, request, id):
        delivery = ReceptionService.accept_full(id)
        return Response({'status': delivery.status})

class AcceptPartialView(generics.GenericAPIView):  # Исправлено: AcceptPartiaView → AcceptPartialView
    permission_classes = [IsFactory]
    serializer_class = AcceptPartialItemSerializer
    def post(self, request, id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        delivery = ReceptionService.accept_partial(id, serializer.validated_data['items'])
        return Response({'status': delivery.status})  # Исправлено: Responce → Response
