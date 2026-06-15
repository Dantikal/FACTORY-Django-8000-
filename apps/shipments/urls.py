from django.urls import path
from .views import ShipmentListCreateView, ShipmentDetailView, ShipmentStatusUpdateView

urlpatterns = [
    path('', ShipmentListCreateView.as_view()),
    path('<uuid:id>/', ShipmentDetailView.as_view()),
    path('<uuid:id>/status', ShipmentStatusUpdateView)
]