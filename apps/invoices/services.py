from django.db import transaction
from .models import Invoice, InvoiceItem

class InvoiceService:
    @staticmethod
    @transaction.atomic
    def create_from_dispatch(dispatch_data):
        """
        Создает накладную на основе данных о выдаче со склада.
        """
        invoice = Invoice.objects.create(
            dispatch_id=dispatch_data['dispatch_id'],
            driver_id=dispatch_data['driver_id'],
            warehouse_id=dispatch_data['warehouse_id'],
            total_amount=dispatch_data['total_amount']
        )

        for item in dispatch_data['items']:
            InvoiceItem.objects.create(
                invoice=invoice,
                product_id=item['product_id'],
                qty=item['qty'],
                price=item['price'],
                total=item['total']
            )
        
        return invoice
