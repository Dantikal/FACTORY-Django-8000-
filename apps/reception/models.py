from django.db import models
from shared.models import BaseModel


class DeliveryStatus(models.TextChoices):
    """Статус приемки товара от завода"""
    PENDING = 'pending', 'Ожидает приемки'
    ACCEPTED = 'accepted', 'Принято полностью'
    ACCEPTED_WITH_DISCREPANCY = 'accepted_with_discrepancy', 'Принято с расхождениями'
    CANCELLED = 'cancelled', 'Отменено'


class DiscrepancyType(models.TextChoices):
    """Тип расхождения при приемке"""
    NONE = 'none', 'Нет расхождений'
    SHORTAGE = 'shortage', 'Недостача'
    SURPLUS = 'surplus', 'Излишек'
    DEFECT = 'defect', 'Брак'


class FactoryDelivery(BaseModel):
    """Поставка от завода на склад"""
    shipment = models.ForeignKey(
        'shipments.Shipment',  # исправлено: shipments (множественное число)
        on_delete=models.PROTECT,
        related_name='deliveries'
    )
    warehouse_id = models.UUIDField(help_text='ID склада получателя')
    delivery_number = models.CharField(max_length=100, unique=True, help_text='Номер поставки')
    delivered_at = models.DateTimeField(help_text='Дата и время доставки')
    status = models.CharField(
        max_length=30,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.PENDING
    )
    total_amount = models.DecimalField(  # исправлено: total_amount (было total_amout)
        max_digits=14,
        decimal_places=2,
        default=0,
        help_text='Общая сумма принятого товара'
    )
    warehouse_comment = models.TextField(
        blank=True,
        help_text='Комментарий заведующего складом'
    )
    created_by = models.ForeignKey(  # исправлено: добавил created_by (было пропущено)
        'users.User',
        on_delete=models.PROTECT,
        related_name='created_deliveries'
    )

    class Meta:
        verbose_name = 'Поставка от завода'
        verbose_name_plural = 'Поставки от завода'
        ordering = ['-delivered_at']

    def __str__(self):
        return f'{self.delivery_number} - {self.shipment.truck_driver}'


class DeliveryItem(BaseModel):
    """Товар в поставке"""
    delivery = models.ForeignKey(
        FactoryDelivery,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'products.Product',  # исправлено: products (множественное число)
        on_delete=models.PROTECT,
        related_name='delivery_items'
    )
    expected_qty = models.PositiveIntegerField(  # исправлено: PositiveIntegerField (было PositiveBigIntegerField)
        help_text='Ожидаемое количество (в штуках)'
    )
    actual_qty = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Фактическое количество (в штуках)'
    )
    discrepancy_type = models.CharField(  # исправлено: добавил поле discrepancy_type
        max_length=20,
        choices=DiscrepancyType.choices,
        default=DiscrepancyType.NONE,
        help_text='Тип расхождения'
    )
    discrepancy_qty = models.IntegerField(  # исправлено: IntegerField (было IntegerChoices)
        default=0,
        help_text='Количество расхождения (положительное число)'
    )

    class Meta:
        verbose_name = 'Товар в поставке'
        verbose_name_plural = 'Товары в поставках'

    def __str__(self):
        return f'{self.product.name} - {self.expected_qty} шт.'