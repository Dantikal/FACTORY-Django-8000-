from rest_framework import generics, status  # Исправлено: starus → status
from rest_framework.response import Response  # Исправлено: Responce → Response
from .models import FactoryDelivery
from .serializers import FactoryDeliverySerializer, AcceptPartialItemSerializer  # Исправлено: AcceptPartialItemSerializer (было AcceptPartialItemSerializer)
from .services import ReceptionService
from shared.permissions import IsFactory


class ReceptionListCreateView(generics.ListCreateAPIView):
    queryset = FactoryDelivery.objects.all().order_by('-delivered_at')
    serializer_class = FactoryDeliverySerializer
    permission_classes = [IsFactory]


class ReceptionDetailView(generics.RetrieveAPIView):  # Исправлено: DetilView → DetailView
    queryset = FactoryDelivery.objects.all()
    serializer_class = FactoryDeliverySerializer
    permission_classes = [IsFactory]

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