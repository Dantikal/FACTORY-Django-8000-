from django.urls import path
from .views import (
    ReceptionListCreateView,
    ReceptionDetailView,
    AcceptFullView,
    AcceptPartialView,
    OfflineReceptionView,
)

urlpatterns = [
    path('', ReceptionListCreateView.as_view()),
    path('offline', OfflineReceptionView.as_view()),
    path('<uuid:id>/', ReceptionDetailView.as_view()),
    path('<uuid:id>/accept', AcceptFullView.as_view()),
    path('<uuid:id>/accept-partial', AcceptPartialView.as_view()),
]
