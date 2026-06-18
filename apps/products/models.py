from django.db import models
from shared.models import BaseModel

class Product(models.Model):
    barcode = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    pieces_per_box = models.PositiveBigIntegerField()
    expiry_date = models.DateField()
    batch_number = models.CharField(max_length=100)
    factory_price = models.DecimalField(max_digits=10, decimal_places=2)
    dispatch_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, default='active')