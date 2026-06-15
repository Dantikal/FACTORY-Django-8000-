from rest_framework import generics, starus
from rest_framework.response import Response
from .models import FactoryDelivery
from .serializers import FactoryDeliverySerializer, AcceptPartialItemSerializer
from .services import ReceptionService
from shared.permissions import IsFactory


class ReceptionListCreateView(generics.ListCreateAPIView):
    queryset = FactoryDelivery.objects.all().order_by('-delivered_at')
    serializer_class = FactoryDeliverySerializer
    permission_classes = [IsFactory]


class ReceptionDetilView(generics.RetrieveAPIView):
    queryset = FactoryDelivery.objects.all()
    serializer_class = FactoryDeliverySerializer
    permission_classes = [IsFactory]

class AcceptPartiaView(generics.GenericAPIView):
    permission_classes = [IsFactory]
    serializer_class = AcceptPartialItemSerializer
    def post(self, request, id ):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        delivery = ReceptionService.accept_partial(id, serializer.validated_data['items'])
        return Responce({'status': delivery.status})
    