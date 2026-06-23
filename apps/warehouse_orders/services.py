from django.db import transaction
from django.utils import timezone

from apps.shipments.services import ShipmentService
from shared.exceptions import AppException
from .models import WarehouseOrder, WarehouseOrderItem, WarehouseOrderStatus


class WarehouseOrderService:
    @staticmethod
    @transaction.atomic
    def create_order(items, comment, created_by):
        if created_by.role != 'warehouse_manager':
            raise AppException(
                status_code=403,
                error_code='forbidden',
                message='Only warehouse managers can create warehouse orders',
            )
        if not created_by.warehouse_id:
            raise AppException(
                status_code=400,
                error_code='warehouse_required',
                message='Warehouse manager must have warehouse_id',
            )

        order = WarehouseOrder.objects.create(
            warehouse_id=created_by.warehouse_id,
            comment=comment or '',
            created_by=created_by,
        )

        for item in items:
            WarehouseOrderItem.objects.create(
                order=order,
                product=item['product'],
                qty=item['qty'],
            )

        return order

    @staticmethod
    @transaction.atomic
    def update_status(order_id, new_status, updated_by):
        try:
            order = (
                WarehouseOrder.objects
                .select_for_update()
                .prefetch_related('items__product')
                .get(id=order_id)
            )
        except WarehouseOrder.DoesNotExist:
            raise AppException(
                status_code=404,
                error_code='warehouse_order_not_found',
                message=f"Warehouse order with ID '{order_id}' not found",
            )

        previous_status = order.status
        order.status = new_status
        order.save(update_fields=['status', 'updated_at'])

        shipment = None
        if (
            new_status == WarehouseOrderStatus.APPROVED
            and previous_status != WarehouseOrderStatus.APPROVED
        ):
            shipment = WarehouseOrderService._create_shipment(order, updated_by)

        return order, shipment

    @staticmethod
    def _create_shipment(order, created_by):
        shipment_items = [
            {
                'product_id': item.product_id,
                'qty_boxes': 0,
                'qty_pieces': item.qty,
            }
            for item in order.items.all()
        ]

        return ShipmentService.create_shipment(
            warehouse_id=order.warehouse_id,
            shipment_date=timezone.localdate(),
            truck_number=f'WO-{str(order.id)[:8]}',
            truck_driver='warehouse_order_auto',
            items=shipment_items,
            created_by=created_by,
        )
