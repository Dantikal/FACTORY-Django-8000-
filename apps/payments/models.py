from django.db import models
from shared.models import BaseModel


class WarehouseDebt(BaseModel):
    warehouse_id = models.IntegerField(unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = 'warehouse_debts'
        verbose_name = 'Warehouse Debt'
        verbose_name_plural = 'Warehouse Debts'

    def __str__(self):
        return f"Warehouse {self.warehouse_id} - Debt: {self.amount}"
