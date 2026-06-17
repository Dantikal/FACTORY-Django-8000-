from django.db import models
from shared.models import BaseModel

class PaymentMethod(models.TextChoices):
    CASH = 'cash', 'Наличные'
    TRANSFER = 'transfer', 'Перевод'
    CARD = 'card', 'Карта'

class FactoryPayment(BaseModel):
    warehouse_id = models.UUIDField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH
    )
    comment = models.TextField(blank=True, null=True)
    paid_at = models.DateTimeField()
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.PROTECT,
        related_name='payments'
    )
    client_id = models.CharField(max_length=36, unique=True)
    operation_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'factory_payments'
        verbose_name = 'Платеж от завода'
        verbose_name_plural = 'Платежи от завода'

class WarehouseDebt(BaseModel):
    warehouse_id = models.UUIDField(unique=True) # Changed from IntegerField to UUIDField for consistency
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = 'warehouse_debts'
        verbose_name = 'Warehouse Debt'
        verbose_name_plural = 'Warehouse Debts'

    def __str__(self):
        return f"Warehouse {self.warehouse_id} - Debt: {self.amount}"
