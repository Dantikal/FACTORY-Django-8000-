import uuid

from django.db import models


class WarehouseOrderStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'


class WarehouseOrder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    warehouse_id = models.UUIDField()
    status = models.CharField(
        max_length=20,
        choices=WarehouseOrderStatus.choices,
        default=WarehouseOrderStatus.PENDING,
    )
    comment = models.TextField(blank=True, default='')
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.PROTECT,
        related_name='warehouse_orders',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'warehouse_orders'
        ordering = ['-created_at']


class WarehouseOrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        WarehouseOrder,
        on_delete=models.CASCADE,
        related_name='items',
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='warehouse_order_items',
    )
    qty = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'warehouse_order_items'
