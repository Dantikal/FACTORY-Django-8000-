import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from apps.products.models import Product

class SyncInitialView(APIView):
    """
    Эндпоинт для начальной синхронизации.
    Собирает данные о товарах из локальной БД и объединяет их с данными об остатках
    из warehouse-service, а также получает данные о долгах водителей из drivers-service.
    """

    def get(self, request, *args, **kwargs):
        # 1. Получаем продукты из локальной БД
        products = Product.objects.filter(status='active')
        warnings = []

        # 2. Запрос к warehouse-service за остатками
        inventory_data = {}
        warehouse_available = True
        try:
            response = requests.get(
                f"{settings.WAREHOUSE_SERVICE_URL}/api/warehouse/inventory",
                timeout=5
            )
            response.raise_for_status()
            # Ожидаем список объектов с barcode и stockQuantity
            for item in response.json():
                inventory_data[item.get('barcode')] = item.get('stockQuantity', 0)
        except requests.exceptions.RequestException as e:
            warehouse_available = False
            warnings.append("warehouse_unavailable")
            print(f"Error fetching inventory: {e}")

        # 3. Запрос к drivers-service за долгами
        drivers_data = []
        try:
            response = requests.get(
                f"{settings.DRIVERS_SERVICE_URL}/api/drivers/debts",
                timeout=5
            )
            response.raise_for_status()
            drivers_data = response.json()
        except requests.exceptions.RequestException as e:
            warnings.append("drivers_unavailable")
            print(f"Error fetching drivers debts: {e}")

        # 4. Формируем итоговый список продуктов
        products_list = []
        for p in products:
            products_list.append({
                "id": str(p.id),
                "barcode": p.barcode,
                "name": p.name,
                "stockQuantity": inventory_data.get(p.barcode, 0) if warehouse_available else None,
                "factoryPrice": str(p.factory_price),
                "issuePrice": str(p.dispatch_price),
                "piecesPerBox": getattr(p, 'pieces_per_box', 1), # На случай если поле называется иначе
                "batchNumber": p.batch_number,
                "expiryDate": p.expiry_date.isoformat() if p.expiry_date else None,
            })

        # 5. Формируем ответ
        result = {
            "products": products_list,
            "drivers": drivers_data,
            "warnings": warnings,
        }

        return Response(result, status=status.HTTP_200_OK)
