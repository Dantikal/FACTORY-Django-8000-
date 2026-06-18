from decimal import Decimal
from decimal import InvalidOperation
from uuid import UUID

import requests
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.payments.models import FactoryPayment
from apps.products.models import Product
from apps.reception.models import DeliveryStatus, FactoryDelivery
from .serializers import SyncPushSerializer


def _camel_or_snake(data, snake_key, camel_key=None, default=None):
    camel_key = camel_key or snake_key
    if snake_key in data:
        return data[snake_key]
    if camel_key in data:
        return data[camel_key]
    return default


def _operation_client_id(operation):
    payload = operation.get('payload') or {}
    return (
        operation.get('id')
        or operation.get('clientId')
        or payload.get('id')
        or payload.get('clientId')
        or payload.get('client_id')
    )


def _parse_uuid(value, field_name):
    if value is None:
        raise ValidationError({field_name: 'This field is required.'})
    try:
        return UUID(str(value))
    except ValueError:
        raise ValidationError({field_name: 'Invalid UUID.'})


def _parse_operation_time(payload):
    raw_value = (
        payload.get('createdAt')
        or payload.get('created_at')
        or payload.get('operationTime')
        or payload.get('operation_time')
        or payload.get('paidAt')
        or payload.get('paid_at')
        or payload.get('deliveredAt')
        or payload.get('delivered_at')
    )

    if not raw_value:
        return timezone.now()

    parsed = parse_datetime(str(raw_value))
    if not parsed:
        raise ValidationError({'createdAt': 'Invalid ISO 8601 datetime.'})
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed


def _parse_decimal(value, field_name):
    if value is None:
        raise ValidationError({field_name: 'This field is required.'})
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValidationError({field_name: 'Invalid decimal.'})


def _json_safe(value):
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def _result(operation, status_value, **extra):
    client_id = _operation_client_id(operation)
    data = {
        'id': str(client_id) if client_id else None,
        'action': operation.get('action'),
        'status': status_value,
    }
    data.update(extra)
    return data


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


class SyncPullView(SyncInitialView):
    pass


class SyncStatusView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({
            'status': 'ok',
            'mode': 'partial',
            'pull': {
                'products': True,
                'drivers': True,
                'warnings': True,
            },
            'push': {
                'atomic': False,
                'idempotency': 'id_or_clientId',
                'supportedActions': [
                    'CREATE_ORDER',
                    'CREATE_RECEIPT',
                    'CREATE_RETURN',
                    'CREATE_PAYMENT',
                ],
            },
        })


class SyncPushView(APIView):
    """
    Обрабатывает офлайн-очередь независимо по каждой операции.
    Дубли с тем же id/clientId возвращаются как ok и не создают запись повторно.
    """

    def post(self, request, *args, **kwargs):
        serializer = SyncPushSerializer(data=self._normalize_payload(request.data))
        serializer.is_valid(raise_exception=True)

        results = []
        processed = 0
        failed = 0

        for operation in serializer.validated_data['operations']:
            try:
                with transaction.atomic():
                    result = self._process_operation(operation)
                processed += 1
            except Exception as exc:
                failed += 1
                result = _result(operation, 'error', error=self._error_payload(exc))
            results.append(result)

        response_status = 'success' if failed == 0 else 'partial'
        if processed == 0 and failed > 0:
            response_status = 'failed'

        return Response({
            'processed': processed,
            'failed': failed,
            'status': response_status,
            'results': results,
        }, status=status.HTTP_200_OK)

    def _normalize_payload(self, data):
        if isinstance(data, list):
            return {'operations': data}
        if isinstance(data, dict) and isinstance(data.get('operations'), list):
            return data
        raise ValidationError({'operations': 'Expected an array or an object with operations array.'})

    def _process_operation(self, operation):
        action = operation['action']

        if action == 'CREATE_PAYMENT':
            return self._create_payment(operation)
        if action == 'CREATE_RECEIPT':
            return self._create_receipt(operation)
        if action in ('CREATE_ORDER', 'CREATE_RETURN'):
            return self._forward_driver_operation(operation)

        raise ValidationError({'action': 'Unsupported action.'})

    def _create_payment(self, operation):
        payload = operation['payload']
        client_id = str(_operation_client_id(operation))
        operation_uuid = _parse_uuid(client_id, 'id')

        existing = (
            FactoryPayment.objects.filter(id=operation_uuid).first()
            or FactoryPayment.objects.filter(client_id=client_id).first()
        )
        if existing:
            return _result(operation, 'ok', duplicate=True, objectId=str(existing.id))

        operation_time = _parse_operation_time(payload)
        payment = FactoryPayment.objects.create(
            id=operation_uuid,
            warehouse_id=_parse_uuid(_camel_or_snake(payload, 'warehouse_id', 'warehouseId'), 'warehouse_id'),
            amount=_parse_decimal(payload.get('amount'), 'amount'),
            payment_method=_camel_or_snake(payload, 'payment_method', 'paymentMethod', 'cash'),
            comment=payload.get('comment'),
            paid_at=operation_time,
            created_by=self.request.user,
            client_id=client_id,
            operation_time=operation_time,
        )
        FactoryPayment.objects.filter(id=payment.id).update(created_at=operation_time)
        return _result(operation, 'ok', objectId=str(payment.id))

    def _create_receipt(self, operation):
        payload = operation['payload']
        client_id = str(_operation_client_id(operation))
        operation_uuid = _parse_uuid(client_id, 'id')

        existing = (
            FactoryDelivery.objects.filter(id=operation_uuid).first()
            or FactoryDelivery.objects.filter(client_id=client_id).first()
        )
        if existing:
            return _result(operation, 'ok', duplicate=True, objectId=str(existing.id))

        operation_time = _parse_operation_time(payload)
        delivery = FactoryDelivery.objects.create(
            id=operation_uuid,
            shipment_id=_parse_uuid(_camel_or_snake(payload, 'shipment_id', 'shipmentId'), 'shipment_id'),
            warehouse_id=_parse_uuid(_camel_or_snake(payload, 'warehouse_id', 'warehouseId'), 'warehouse_id'),
            delivery_number=_camel_or_snake(payload, 'delivery_number', 'deliveryNumber', client_id),
            delivered_at=_parse_datetime_field(payload, 'delivered_at', 'deliveredAt', operation_time),
            status=_camel_or_snake(payload, 'status', default=DeliveryStatus.PENDING),
            total_amount=_parse_decimal(_camel_or_snake(payload, 'total_amount', 'totalAmount', '0'), 'total_amount'),
            warehouse_comment=payload.get('comment') or payload.get('warehouse_comment') or '',
            created_by=self.request.user,
            client_id=client_id,
            operation_time=operation_time,
        )
        FactoryDelivery.objects.filter(id=delivery.id).update(created_at=operation_time)
        return _result(operation, 'ok', objectId=str(delivery.id))

    def _forward_driver_operation(self, operation):
        try:
            response = requests.post(
                f'{settings.DRIVERS_SERVICE_URL}/api/offline/sync',
                json={'operations': [_json_safe(operation)]},
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as exc:
            raise ValidationError({
                'drivers_service': f'Drivers service unavailable: {exc}'
            })

        if isinstance(data, dict) and data.get('results'):
            forwarded = data['results'][0]
            if forwarded.get('status') == 'error':
                raise ValidationError({'drivers_service': forwarded.get('error')})
            return _result(operation, 'ok', forwarded=True, result=forwarded)

        return _result(operation, 'ok', forwarded=True, result=data)

    def _error_payload(self, exc):
        if isinstance(exc, ValidationError):
            return {
                'code': 'validation_error',
                'message': 'Validation error',
                'fields': exc.detail,
            }
        return {
            'code': 'internal_error',
            'message': str(exc),
        }


def _parse_datetime_field(payload, snake_key, camel_key, default):
    raw_value = _camel_or_snake(payload, snake_key, camel_key)
    if not raw_value:
        return default
    parsed = parse_datetime(str(raw_value))
    if not parsed:
        raise ValidationError({camel_key: 'Invalid ISO 8601 datetime.'})
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed
