from datetime import date
from decimal import Decimal
from uuid import uuid4
from unittest.mock import patch

from rest_framework.test import APITestCase

from apps.payments.models import WarehouseDebt
from apps.products.models import Product
from apps.reception.models import DeliveryItem, FactoryDelivery
from apps.users.models import User


class OfflineReceptionApiTests(APITestCase):
    def setUp(self):
        self.factory_user = User.objects.create_user(
            username='factory',
            password='pass',
            full_name='Factory',
            role='factory',
        )
        self.warehouse_id = uuid4()
        self.product = Product.objects.create(
            barcode='4600001',
            name='Milk',
            pieces_per_box=12,
            expiry_date=date(2027, 1, 1),
            batch_number='B-1',
            factory_price=Decimal('55.00'),
            dispatch_price=Decimal('60.00'),
            status='active',
        )
        self.client.force_authenticate(self.factory_user)

    @patch('apps.reception.services.publish_reception_completed_offline')
    def test_create_offline_reception(self, publish_mock):
        client_id = uuid4()

        response = self.client.post(
            '/api/factory/reception/offline',
            {
                'warehouseId': str(self.warehouse_id),
                'createdAt': '2026-07-02T10:00:00+06:00',
                'clientId': str(client_id),
                'items': [
                    {
                        'barcode': self.product.barcode,
                        'actualQty': 100,
                        'factoryPrice': '55.00',
                    },
                ],
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        delivery = FactoryDelivery.objects.get(client_id=str(client_id))
        self.assertIsNone(delivery.shipment_id)
        self.assertEqual(delivery.warehouse_id, self.warehouse_id)
        self.assertEqual(delivery.total_amount, Decimal('5500.00'))
        item = DeliveryItem.objects.get(delivery=delivery)
        self.assertEqual(item.product, self.product)
        self.assertEqual(item.actual_qty, 100)
        self.assertEqual(item.expected_qty, 100)
        self.assertEqual(WarehouseDebt.objects.get(warehouse_id=self.warehouse_id).amount, Decimal('5500.00'))
        publish_mock.assert_called_once()

    @patch('apps.reception.services.publish_reception_completed_offline')
    def test_offline_reception_is_idempotent_by_client_id(self, publish_mock):
        payload = {
            'warehouseId': str(self.warehouse_id),
            'createdAt': '2026-07-02T10:00:00+06:00',
            'clientId': str(uuid4()),
            'items': [
                {
                    'barcode': self.product.barcode,
                    'actualQty': 100,
                    'factoryPrice': '55.00',
                },
            ],
        }

        first = self.client.post('/api/factory/reception/offline', payload, format='json')
        second = self.client.post('/api/factory/reception/offline', payload, format='json')

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(FactoryDelivery.objects.count(), 1)
        self.assertEqual(DeliveryItem.objects.count(), 1)
        self.assertEqual(WarehouseDebt.objects.get(warehouse_id=self.warehouse_id).amount, Decimal('5500.00'))
        publish_mock.assert_called_once()

    @patch('apps.reception.services.publish_reception_completed_offline')
    def test_unknown_barcode_returns_404(self, publish_mock):
        response = self.client.post(
            '/api/factory/reception/offline',
            {
                'warehouseId': str(self.warehouse_id),
                'createdAt': '2026-07-02T10:00:00+06:00',
                'clientId': str(uuid4()),
                'items': [
                    {
                        'barcode': 'missing',
                        'actualQty': 100,
                        'factoryPrice': '55.00',
                    },
                ],
            },
            format='json',
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error']['code'], 'product_not_found')
        self.assertFalse(FactoryDelivery.objects.exists())
        self.assertFalse(WarehouseDebt.objects.exists())
        publish_mock.assert_not_called()
