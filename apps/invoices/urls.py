from django.urls import path

from .views import InvoiceDetailView, InvoiceExcelView, InvoiceListView, InvoicePdfView

urlpatterns = [
    path('', InvoiceListView.as_view()),
    path('<uuid:id>/', InvoiceDetailView.as_view()),
    path('<uuid:id>/pdf/', InvoicePdfView.as_view()),
    path('<uuid:id>/excel/', InvoiceExcelView.as_view()),
]
