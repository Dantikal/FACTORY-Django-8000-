from rest_framework import generics
from .models import FactoryPayment
# from .serializers import FactoryPaymentSerializer # Assuming it will be created
from shared.permissions import IsAccountant

class PaymentListCreateView(generics.ListCreateAPIView):
    queryset = FactoryPayment.objects.all()
    # serializer_class = FactoryPaymentSerializer
    permission_classes = [IsAccountant]
