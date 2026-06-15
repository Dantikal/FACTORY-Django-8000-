from django.urls import path
from .views import ProductListCreateView, ProductDetailView, ProductByBarcodeView


urlpatterns = [
    path('', ProductListCreateView.as_view()),
    path('<uuid:id>/', ProductDetailView.as_view()),
    path('barcode/<str:barcode>/', ProductByBarcodeView.as_view())
]

