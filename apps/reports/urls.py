from django.urls import path

from .views import (
    CashboxReportView,
    DispatchReportView,
    DriverDebtReportView,
    InventoryReportView,
    LowStockReportView,
    MovementReportView,
    ProductRatingReportView,
    ReceptionReportView,
    RegionalSalesReportView,
    ReturnReportView,
    ShipmentReportView,
    WarehouseDebtReportView,
)

urlpatterns = [
    path('shipments/', ShipmentReportView.as_view()),
    path('receptions/', ReceptionReportView.as_view()),
    path('inventory/', InventoryReportView.as_view()),
    path('regional-sales/', RegionalSalesReportView.as_view()),
    path('warehouse-debts/', WarehouseDebtReportView.as_view()),
    path('product-rating/', ProductRatingReportView.as_view()),
    path('movements/', MovementReportView.as_view()),
    path('driver-debts/', DriverDebtReportView.as_view()),
    path('cashbox/', CashboxReportView.as_view()),
    path('dispatches/', DispatchReportView.as_view()),
    path('returns/', ReturnReportView.as_view()),
    path('low-stock/', LowStockReportView.as_view()),
]
