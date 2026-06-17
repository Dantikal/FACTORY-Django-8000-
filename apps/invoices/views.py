from rest_framework import generics
from .models import Invoice
# from .serializers import InvoiceSerializer # Assuming it will be created
from shared.permissions import IsFactory

class InvoiceListView(generics.ListAPIView):
    queryset = Invoice.objects.all()
    # serializer_class = InvoiceSerializer
    permission_classes = [IsFactory]
