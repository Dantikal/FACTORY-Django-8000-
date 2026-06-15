from django.db import transaction
from .models import FactoryDelivery, DeliveryItem, DeliveryStatus
from apps.payments.services import increase_warehouse_debt
from apps.events.publisher import publish_reception_completed

class ReceptionService:
    @staticmethod
    @transaction.atomic
    def accept_full(delivery_id):
        delivery = FactoryDelivery.objects.select_related('shipment').get(id=delivery_id)
        delivery.status = DeliveryStatus.ACCEPTED
        delivery.save()
        increase_warehouse_debt(delivery.warehouse_id, delivery.total_amount)
        delivery.shipment.status = 'accepted'
        delivery.shipment.save()
        publish_reception_completed(delivery.id, delivery.warehouse_id, delivery.total_amount, 'full')
        return delivery

    @staticmethod
    @transaction.atomic
    def accept_partial(delivery_id, items_data):
        delivery = FactoryDelivery.objects.select_related('shipment').get(id=delivery_id)
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
        publish_reception_completed(delivery.id, delivery.warehouse_id, total_accepted, 'partial')
        return delivery