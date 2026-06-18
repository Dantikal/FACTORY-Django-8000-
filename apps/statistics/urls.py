from django.urls import path

from .views import (
    CountryStatsView,
    RegionalSalesView,
    TopProductsView,
    WarehouseStatsView,
    WarehousesStatsView,
    WeakProductsView,
)

urlpatterns = [
    path('country/', CountryStatsView.as_view()),
    path('warehouses/', WarehousesStatsView.as_view()),
    path('warehouses/<uuid:id>/', WarehouseStatsView.as_view()),
    path('top-products/', TopProductsView.as_view()),
    path('weak-products/', WeakProductsView.as_view()),
    path('regional-sales/', RegionalSalesView.as_view()),
]
