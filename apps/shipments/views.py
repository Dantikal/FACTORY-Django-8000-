from rest_framework import generics, status
from rest_framework.response import Response
from .models import Shipment
from .serializers import ShipmentSerializer, ShipmentStatusUpdateSerializer
from .services import ShipmentService
from shared.permissions import IsFactory

class ShipmentListCreateView(generics.ListCreateAPIView):
    queryset = Shipment.objects.all().order_by('-shipment_date')
    serializer_class = ShipmentSerializer
    permission_classes = [IsFactory]
    filter_fields = ['warehouse_id', 'status']
    def create(self, request, *args, **kwargs):
        data = request.data
        shipment = ShipmentService.create_shipment(
            warehouse_id=data['warehouse_id'],
            shipment_date=data['shipment_date'],
            truck_number=data['truck_number'],
            truck_driver=data['truck_driver'],
            items=data['items'],
            created_by=request.user
        )
        serializer = self.get_serializer(shipment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class ShipmentDetailView(generics.RetrieveAPIView):
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer
    permission_classes = [IsFactory]

class ShipmentStatusUpdateView(generics.UpdateAPIView):
    queryset = Shipment.objects.all()
    serializer_class = ShipmentStatusUpdateSerializer
    permission_classes = [IsFactory]
    def update(self, request, *args, **kwargs):
        shipment = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data['status']
        updated = ShipmentService.update_status(shipment.id, new_status)
        return Response({'status': updated.status})
    