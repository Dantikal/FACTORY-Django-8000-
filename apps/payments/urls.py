from django.urls import path

from .views import FactoryPaymentListView, WarehouseDebtAllView, WarehouseDebtView

urlpatterns = [
    path('', FactoryPaymentListView.as_view()),
    path('debt/', WarehouseDebtView.as_view()),
    path('debts/all/', WarehouseDebtAllView.as_view()),
]
