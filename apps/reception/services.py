from django.db import transaction
from .models import FactoryDelivery, DeliveryItem, DeliveryStatus
from apps.payments.services import increase_warehouse_debt
from apps.events.publisher import publish_reception_completed


def _delivery_items_payload(delivery):
    return [
        {
            'product_id': str(item.product_id),
            'expected_qty': item.expected_qty,
            'actual_qty': item.actual_qty,
            'discrepancy_type': item.discrepancy_type,
            'discrepancy_qty': item.discrepancy_qty,
        }
        for item in delivery.items.select_related('product').all()
    ]

class ReceptionService:
    @staticmethod
    @transaction.atomic
    def accept_full(delivery_id):
        delivery = (
            FactoryDelivery.objects
            .select_related('shipment')
            .prefetch_related('items__product')
            .get(id=delivery_id)
        )
        delivery.status = DeliveryStatus.ACCEPTED
        delivery.save()
        for item in delivery.items.all():
            item.actual_qty = item.expected_qty
            item.discrepancy_type = 'none'
            item.discrepancy_qty = 0
            item.save(update_fields=['actual_qty', 'discrepancy_type', 'discrepancy_qty', 'updated_at'])
        increase_warehouse_debt(delivery.warehouse_id, delivery.total_amount)
        delivery.shipment.status = 'accepted'
        delivery.shipment.save()
        publish_reception_completed(delivery.id, delivery.warehouse_id, _delivery_items_payload(delivery))
        return delivery

    @staticmethod
    @transaction.atomic
    def accept_partial(delivery_id, items_data):
        delivery = (
            FactoryDelivery.objects
            .select_related('shipment')
            .prefetch_related('items__product')
            .get(id=delivery_id)
        )
        total_accepted = 0
        for item_data in items_data:
            ditem = DeliveryItem.objects.get(id=item_data['id'])
            ditem.actual_qty = item_data['actual_qty']
            diff = ditem.expected_qty - item_data['actual_qty']
            if diff > 0:
                ditem.discrepancy_type = 'shortage'
                ditem.discrepancy_qty = diff
            elif diff < 0:
                ditem.discrepancy_type = 'surplus'
                ditem.discrepancy_qty = -diff
            else:
                ditem.discrepancy_type = 'none'
            ditem.save()
            # цена из связанного shipment_item или из продукта
            total_accepted += item_data['actual_qty'] * ditem.product.dispatch_price
        delivery.status = DeliveryStatus.ACCEPTED_WITH_DISCREPANCY
        delivery.total_amount = total_accepted
        delivery.save()
        increase_warehouse_debt(delivery.warehouse_id, total_accepted)
        delivery.shipment.status = 'accepted_with_discrepancy'
        delivery.shipment.save()
        publish_reception_completed(delivery.id, delivery.warehouse_id, _delivery_items_payload(delivery))
        return delivery
