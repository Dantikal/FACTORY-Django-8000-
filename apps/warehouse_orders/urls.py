from django.urls import path

from .views import (
    WarehouseOrderDetailView,
    WarehouseOrderListCreateView,
    WarehouseOrderStatusUpdateView,
)

urlpatterns = [
    path('', WarehouseOrderListCreateView.as_view()),
    path('<uuid:id>/', WarehouseOrderDetailView.as_view()),
    path('<uuid:id>/status', WarehouseOrderStatusUpdateView.as_view()),
]
