from decimal import Decimal
from django.db import transaction
from apps.products.models import Product
from .models import Shipment, ShipmentItem, ShipmentStatus
from apps.events.publisher import publish_shipment_created

class ShipmentService:
    @staticmethod
    @transaction.atomic
    def create_shipment(warehouse_id, shipment_date, truck_number, truck_driver, items, created_by):
        total_amount = Decimal('0.00')
        enriched_items = []
        for it in items:
            product = Product.objects.get(id=it['product_id'])
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
            publish_shipment_created(shipment.id, warehouse_id, total_amount)
            return shipment
        @staticmethod
        def update_status(shipment_id, new_status):
            shipment = Shipment.objects.get(id=shipment_id)
            shipment.status = new_status
            shipment.save()
            return shipment