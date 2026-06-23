from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(title='FactoryAPI', default_version='v1'),
    public=True,
    permission_classes=[]
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/factory/auth/', include('apps.users.urls')),
    path('api/factory/products/', include('apps.products.urls')),
    path('api/factory/shipments/', include('apps.shipments.urls')),
    path('api/factory/warehouse-orders/', include('apps.warehouse_orders.urls')),
    path('api/factory/reception/', include('apps.reception.urls')),
    path('api/factory/payments/', include('apps.payments.urls')),
    path('api/factory/invoices/', include('apps.invoices.urls')),
    path('api/factory/stats/', include('apps.statistics.urls')),
    path('api/factory/reports/', include('apps.reports.urls')),
    path('api/factory/sync/', include('apps.sync.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0)),
]
