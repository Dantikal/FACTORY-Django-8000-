from datetime import date
from decimal import Decimal
from uuid import uuid4
from unittest.mock import patch

from rest_framework.test import APITestCase

from apps.products.models import Product
from apps.shipments.models import Shipment
from apps.users.models import User
from .models import WarehouseOrder, WarehouseOrderItem, WarehouseOrderStatus


class WarehouseOrderApiTests(APITestCase):
    def setUp(self):
        self.warehouse_id = uuid4()
        self.other_warehouse_id = uuid4()
        self.manager = User.objects.create_user(
            username='warehouse-manager',
            password='pass',
            full_name='Warehouse Manager',
            role='warehouse_manager',
            warehouse_id=self.warehouse_id,
        )
        self.other_manager = User.objects.create_user(
            username='other-warehouse-manager',
            password='pass',
            full_name='Other Warehouse Manager',
            role='warehouse_manager',
            warehouse_id=self.other_warehouse_id,
        )
        self.factory_user = User.objects.create_user(
            username='factory',
            password='pass',
            full_name='Factory',
            role='factory',
        )
        self.product = Product.objects.create(
            barcode='123456',
            name='Test product',
            pieces_per_box=12,
            expiry_date=date(2027, 1, 1),
            batch_number='B-1',
            factory_price=Decimal('10.00'),
            dispatch_price=Decimal('12.50'),
            status='active',
        )

    def test_warehouse_manager_creates_order_for_own_warehouse(self):
        self.client.force_authenticate(self.manager)

        response = self.client.post(
            '/api/factory/warehouse-orders/',
            {
                'items': [
                    {'productId': str(self.product.id), 'qty': 100},
                ],
                'comment': 'Need stock',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(WarehouseOrder.objects.count(), 1)
        order = WarehouseOrder.objects.get()
        self.assertEqual(order.warehouse_id, self.warehouse_id)
        self.assertEqual(order.created_by, self.manager)
        self.assertEqual(order.items.get().qty, 100)

    def test_manager_lists_only_own_orders_and_factory_lists_all(self):
        own_order = WarehouseOrder.objects.create(
            warehouse_id=self.warehouse_id,
            created_by=self.manager,
        )
        WarehouseOrderItem.objects.create(order=own_order, product=self.product, qty=10)
        other_order = WarehouseOrder.objects.create(
            warehouse_id=self.other_warehouse_id,
            created_by=self.other_manager,
        )
        WarehouseOrderItem.objects.create(order=other_order, product=self.product, qty=20)

        self.client.force_authenticate(self.manager)
        response = self.client.get('/api/factory/warehouse-orders/')

        self.assertEqual(response.status_code, 200)
        manager_ids = {item['id'] for item in response.data['results']}
        self.assertEqual(manager_ids, {str(own_order.id)})

        self.client.force_authenticate(self.factory_user)
        response = self.client.get('/api/factory/warehouse-orders/')

        self.assertEqual(response.status_code, 200)
        factory_ids = {item['id'] for item in response.data['results']}
        self.assertEqual(factory_ids, {str(own_order.id), str(other_order.id)})

    @patch('apps.shipments.services.publish_shipment_created')
    def test_approving_order_creates_shipment(self, publish_mock):
        order = WarehouseOrder.objects.create(
            warehouse_id=self.warehouse_id,
            created_by=self.manager,
        )
        WarehouseOrderItem.objects.create(order=order, product=self.product, qty=25)

        self.client.force_authenticate(self.factory_user)
        response = self.client.put(
            f'/api/factory/warehouse-orders/{order.id}/status',
            {'status': WarehouseOrderStatus.APPROVED},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, WarehouseOrderStatus.APPROVED)
        self.assertEqual(Shipment.objects.count(), 1)
        shipment = Shipment.objects.get()
        self.assertEqual(shipment.warehouse_id, self.warehouse_id)
        self.assertEqual(shipment.items.get().qty_pieces, 25)
        self.assertEqual(response.data['shipment_id'], str(shipment.id))
        publish_mock.assert_called_once()
