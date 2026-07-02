from decimal import Decimal

from django.db import transaction
from .models import FactoryDelivery, DeliveryItem, DeliveryStatus
from apps.payments.services import increase_warehouse_debt
from apps.events.publisher import publish_reception_completed, publish_reception_completed_offline
from apps.products.models import Product
from shared.exceptions import AppException


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
    def create_offline(validated_data, user):
        client_id = str(validated_data['clientId'])
        existing = FactoryDelivery.objects.filter(client_id=client_id).prefetch_related('items__product').first()
        if existing:
            return existing, False

        products_by_barcode = {
            product.barcode: product
            for product in Product.objects.filter(
                barcode__in=[item['barcode'] for item in validated_data['items']]
            )
        }
        missing_barcodes = [
            item['barcode']
            for item in validated_data['items']
            if item['barcode'] not in products_by_barcode
        ]
        if missing_barcodes:
            raise AppException(
                status_code=404,
                error_code='product_not_found',
                message=f"Product with barcode '{missing_barcodes[0]}' not found",
                fields={'barcode': missing_barcodes[0]},
            )

        operation_time = validated_data['createdAt']
        total_amount = sum(
            Decimal(item['actualQty']) * item['factoryPrice']
            for item in validated_data['items']
        )

        delivery, created = FactoryDelivery.objects.get_or_create(
            client_id=client_id,
            defaults={
                'shipment': None,
                'warehouse_id': validated_data['warehouseId'],
                'delivery_number': f'offline-{client_id}',
                'delivered_at': operation_time,
                'status': DeliveryStatus.ACCEPTED,
                'total_amount': total_amount,
                'created_by': user,
                'operation_time': operation_time,
            },
        )
        if not created:
            delivery = FactoryDelivery.objects.prefetch_related('items__product').get(id=delivery.id)
            return delivery, False

        for item in validated_data['items']:
            DeliveryItem.objects.create(
                delivery=delivery,
                product=products_by_barcode[item['barcode']],
                expected_qty=item['actualQty'],
                actual_qty=item['actualQty'],
                discrepancy_type='none',
                discrepancy_qty=0,
            )

        increase_warehouse_debt(delivery.warehouse_id, total_amount)
        FactoryDelivery.objects.filter(id=delivery.id).update(created_at=operation_time)
        delivery = FactoryDelivery.objects.prefetch_related('items__product').get(id=delivery.id)
        publish_reception_completed_offline(delivery.id, delivery.warehouse_id, _delivery_items_payload(delivery))
        return delivery, True

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
