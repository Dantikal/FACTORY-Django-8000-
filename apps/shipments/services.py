from decimal import Decimal
from django.db import transaction
from apps.products.models import Product
from .models import Shipment, ShipmentItem, ShipmentStatus
from apps.events.publisher import publish_shipment_created
from shared.exceptions import AppException

class ShipmentService:
    @staticmethod
    @transaction.atomic
    def create_shipment(warehouse_id, shipment_date, truck_number, truck_driver, items, created_by):
        total_amount = Decimal('0.00')
        enriched_items = []
        for it in items:
            try:
                product = Product.objects.get(id=it['product_id'])
            except Product.DoesNotExist:
                raise AppException(
                    status_code=404,
                    error_code="product_not_found",
                    message=f"Product with ID '{it['product_id']}' not found"
                )
            qty_pieces = it['qty_boxes'] * product.pieces_per_box + it['qty_pieces']
            total = qty_pieces * product.dispatch_price
            total_amount += total
            enriched_items.append({
                **it,
                'price': product.dispatch_price,
                'total': total
            })
        
        shipment = Shipment.objects.create(
            warehouse_id=warehouse_id,
            shipment_date=shipment_date,
            truck_number=truck_number,
            truck_driver=truck_driver,
            total_amount=total_amount,
            created_by=created_by
        )

        for it in enriched_items:
            ShipmentItem.objects.create(
                shipment=shipment,
                product_id=it['product_id'],
                qty_boxes=it['qty_boxes'],
                qty_pieces=it['qty_pieces'],
                price=it['price'],
                total=it['total']
            )

        event_items = [
            {
                'product_id': str(it['product_id']),
                'qty_boxes': it['qty_boxes'],
                'qty_pieces': it['qty_pieces'],
                'price': str(it['price']),
                'total': str(it['total']),
            }
            for it in enriched_items
        ]
        publish_shipment_created(shipment.id, warehouse_id, event_items)
        return shipment

    @staticmethod
    def update_status(shipment_id, new_status):
        try:
            shipment = Shipment.objects.get(id=shipment_id)
        except Shipment.DoesNotExist:
            raise AppException(
                status_code=404,
                error_code="shipment_not_found",
                message=f"Shipment with ID '{shipment_id}' not found"
            )
        shipment.status = new_status
        shipment.save()
        return shipment
