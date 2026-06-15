from rest_framework import generics
from rest_framework.exceptions import NotFound
from .models import Product
from .serializers import ProductSerializer
from shared.permissions import IsFactory

class ProductListCreateView(generics.ListAPIView):
    queryset = Product.objects.filter(status='active')
    serializer_class = ProductSerializer
    permission_classes = [IsFactory]
    filterset_fields = ['name', 'barcode']
    search_fields = ['name', 'barcode']

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsFactory]
    def perform_destroy(self, instance):
        instance.status = 'inactive'
        instance.save()

class ProductByBarcodeView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsFactory]
    def get_object(self):
        barcode = self.kwargs['barcode']
        try:
            return Product.objects.get(barcode=barcode, status='active')
        except Product.DoesNotExist:
            raise NotFound('Product not found')