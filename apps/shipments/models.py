from django.db import models
from shared.models import BaseModel

class ShipmentStatus(models.TextChoices):
    IN_TRANSIT = 'in_transit'
    ACCEPTED = 'accepted'
    ACCEPTED_WITH_DISCREPANCY = 'accepted_with_discrepancy'

class Shipment(BaseModel):
    warehouse_id = models.UUIDField()
    shipment_date = models.DateField()
    truck_number = models.CharField(max_length=50)
    truck_driver = models.CharField(max_length=255)
    status = models.CharField(max_length=30, choices=ShipmentStatus.choices, default=ShipmentStatus.IN_TRANSIT)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    created_by = models.ForeignKey('users.User', on_delete=models.PROTECT, related_name="shipments")

class ShipmentItem(BaseModel):
    shipment = models.ForeignKey(
        Shipment,
        on_delete=models.CASCADE,
        related_name='items',
        null=True,
        blank=True,
    )
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)
    qty_boxes = models.PositiveBigIntegerField()
    qty_pieces = models.PositiveBigIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
