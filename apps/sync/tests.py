from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

import requests
from django.test import RequestFactory, SimpleTestCase, override_settings

from apps.sync.views import SyncInitialView


class MockResponse:
    def __init__(self, data):
        self.data = data

    def json(self):
        return self.data

    def raise_for_status(self):
        return None


def make_product(barcode="123"):
    return SimpleNamespace(
        id=1,
        barcode=barcode,
        name="Test product",
        pieces_per_box=12,
        expiry_date=date(2027, 1, 15),
        batch_number="B-1",
        factory_price=Decimal("10.00"),
        dispatch_price=Decimal("12.00"),
    )


@override_settings(
    WAREHOUSE_SERVICE_URL="http://warehouse-service",
    DRIVERS_SERVICE_URL="http://drivers-service",
)
class SyncInitialViewTests(SimpleTestCase):
    def setUp(self):
        self.request = RequestFactory().get("/api/v1/sync/initial")

    @patch("apps.sync.views.Product.objects.filter")
    @patch("apps.sync.views.requests.get")
    def test_returns_null_stock_quantity_when_warehouse_unavailable(
        self,
        mock_get,
        mock_filter,
    ):
        mock_filter.return_value = [make_product()]

        def request_side_effect(url, timeout):
            if "warehouse-service" in url:
                raise requests.exceptions.ConnectTimeout()
            return MockResponse([{"driverId": 1, "debt": "100.00"}])

        mock_get.side_effect = request_side_effect

        response = SyncInitialView().get(self.request)

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data["products"][0]["stockQuantity"])
        self.assertEqual(response.data["drivers"], [{"driverId": 1, "debt": "100.00"}])
        self.assertEqual(response.data["warnings"], ["warehouse_unavailable"])

    @patch("apps.sync.views.Product.objects.filter")
    @patch("apps.sync.views.requests.get")
    def test_returns_empty_drivers_when_drivers_unavailable(
        self,
        mock_get,
        mock_filter,
    ):
        mock_filter.return_value = [make_product()]

        def request_side_effect(url, timeout):
            if "drivers-service" in url:
                raise requests.exceptions.ConnectionError()
            return MockResponse([{"barcode": "123", "stockQuantity": 7}])

        mock_get.side_effect = request_side_effect

        response = SyncInitialView().get(self.request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["products"][0]["stockQuantity"], 7)
        self.assertEqual(response.data["drivers"], [])
        self.assertEqual(response.data["warnings"], ["drivers_unavailable"])

    @patch("apps.sync.views.Product.objects.filter")
    @patch("apps.sync.views.requests.get")
    def test_returns_empty_warnings_when_services_available(
        self,
        mock_get,
        mock_filter,
    ):
        mock_filter.return_value = [make_product()]

        def request_side_effect(url, timeout):
            if "warehouse-service" in url:
                return MockResponse([{"barcode": "123", "stockQuantity": 7}])
            return MockResponse([{"driverId": 1, "debt": "100.00"}])

        mock_get.side_effect = request_side_effect

        response = SyncInitialView().get(self.request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["products"][0]["stockQuantity"], 7)
        self.assertEqual(response.data["drivers"], [{"driverId": 1, "debt": "100.00"}])
        self.assertEqual(response.data["warnings"], [])
