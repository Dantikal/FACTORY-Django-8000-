from django.db import models
from shared.models import BaseModel

class Invoice(BaseModel):
    dispatch_id = models.UUIDField(unique=True)
    driver_id = models.UUIDField()
    warehouse_id = models.UUIDField()
    total_amount = models.DecimalField(max_digits=14, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'factory_invoices'
        verbose_name = 'Накладная'
        verbose_name_plural = 'Накладные'

class InvoiceItem(BaseModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    product_id = models.UUIDField()
    qty = models.IntegerField()
    price = models.DecimalField(max_digits=14, decimal_places=2)
    total = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        db_table = 'factory_invoice_items'
