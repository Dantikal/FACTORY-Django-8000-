from decimal import Decimal

from django.db.models import DecimalField, ExpressionWrapper, F, IntegerField, Sum, Value
from django.db.models.functions import Coalesce
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.payments.models import FactoryPayment, WarehouseDebt
from apps.products.models import Product
from apps.reception.models import DeliveryItem, DeliveryStatus, FactoryDelivery
from apps.shipments.models import Shipment
from .serializers import CountryStatsSerializer, TopProductSerializer, WarehouseStatsSerializer
from shared.permissions import IsManager


DECIMAL_ZERO = Decimal('0.00')


def _decimal_sum(queryset, field):
    return queryset.aggregate(total=Sum(field))['total'] or DECIMAL_ZERO


def _warehouse_ids():
    ids = set()
    ids.update(Shipment.objects.values_list('warehouse_id', flat=True))
    ids.update(FactoryDelivery.objects.values_list('warehouse_id', flat=True))
    ids.update(FactoryPayment.objects.values_list('warehouse_id', flat=True))
    ids.update(WarehouseDebt.objects.values_list('warehouse_id', flat=True))
    return sorted(ids, key=str)


def _warehouse_stats(warehouse_id):
    shipments = Shipment.objects.filter(warehouse_id=warehouse_id)
    deliveries = FactoryDelivery.objects.filter(warehouse_id=warehouse_id)
    payments = FactoryPayment.objects.filter(warehouse_id=warehouse_id)
    debt = WarehouseDebt.objects.filter(warehouse_id=warehouse_id).first()

    return {
        'warehouse_id': warehouse_id,
        'total_shipments': shipments.count(),
        'total_deliveries': deliveries.count(),
        'accepted_deliveries': deliveries.filter(
            status__in=[DeliveryStatus.ACCEPTED, DeliveryStatus.ACCEPTED_WITH_DISCREPANCY]
        ).count(),
        'pending_deliveries': deliveries.filter(status=DeliveryStatus.PENDING).count(),
        'total_payments': _decimal_sum(payments, 'amount'),
        'total_debt': debt.amount if debt else DECIMAL_ZERO,
        'total_sales': _decimal_sum(deliveries, 'total_amount'),
    }


def _limit_from_request(request, default=10, maximum=100):
    try:
        limit = int(request.query_params.get('limit', default))
    except (TypeError, ValueError):
        return default
    return max(1, min(limit, maximum))


def _quantity_expression(prefix=''):
    actual_field = f'{prefix}actual_qty'
    expected_field = f'{prefix}expected_qty'
    return Coalesce(actual_field, expected_field, output_field=IntegerField())


def _total_amount_expression(quantity_expression, price_field):
    return ExpressionWrapper(
        quantity_expression * F(price_field),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )


def _top_product_rows(ordering, limit):
    quantity = _quantity_expression()
    total_amount = _total_amount_expression(quantity, 'product__dispatch_price')

    rows = (
        DeliveryItem.objects
        .values('product_id', 'product__name', 'product__barcode')
        .annotate(
            quantity=Coalesce(Sum(quantity), Value(0), output_field=IntegerField()),
            total_amount=Coalesce(
                Sum(total_amount),
                Value(DECIMAL_ZERO),
                output_field=DecimalField(max_digits=14, decimal_places=2),
            ),
        )
        .order_by(*ordering)[:limit]
    )

    return [
        {
            'product_id': row['product_id'],
            'name': row['product__name'],
            'barcode': row['product__barcode'],
            'quantity': row['quantity'],
            'total_amount': row['total_amount'],
        }
        for row in rows
    ]


class CountryStatsView(APIView):
    permission_classes = [IsManager]

    def get(self, request):
        deliveries = FactoryDelivery.objects.all()
        payments = FactoryPayment.objects.all()

        data = {
            'total_shipments': Shipment.objects.count(),
            'total_deliveries': deliveries.count(),
            'accepted_deliveries': deliveries.filter(
                status__in=[DeliveryStatus.ACCEPTED, DeliveryStatus.ACCEPTED_WITH_DISCREPANCY]
            ).count(),
            'pending_deliveries': deliveries.filter(status=DeliveryStatus.PENDING).count(),
            'total_payments': _decimal_sum(payments, 'amount'),
            'total_debt': _decimal_sum(WarehouseDebt.objects.all(), 'amount'),
            'total_sales': _decimal_sum(deliveries, 'total_amount'),
            'active_products': Product.objects.filter(status='active').count(),
        }
        serializer = CountryStatsSerializer(data)
        return Response(serializer.data)


class WarehousesStatsView(APIView):
    permission_classes = [IsManager]

    def get(self, request):
        data = [_warehouse_stats(warehouse_id) for warehouse_id in _warehouse_ids()]
        serializer = WarehouseStatsSerializer(data, many=True)
        return Response(serializer.data)


class WarehouseStatsView(APIView):
    permission_classes = [IsManager]

    def get(self, request, id):
        serializer = WarehouseStatsSerializer(_warehouse_stats(id))
        return Response(serializer.data)


class TopProductsView(APIView):
    permission_classes = [IsManager]

    def get(self, request):
        data = _top_product_rows(['-quantity', '-total_amount'], _limit_from_request(request))
        serializer = TopProductSerializer(data, many=True)
        return Response(serializer.data)


class WeakProductsView(APIView):
    permission_classes = [IsManager]

    def get(self, request):
        limit = _limit_from_request(request)
        quantity = _quantity_expression('delivery_items__')
        total_amount = _total_amount_expression(quantity, 'dispatch_price')

        rows = (
            Product.objects
            .filter(status='active')
            .annotate(
                quantity=Coalesce(Sum(quantity), Value(0), output_field=IntegerField()),
                total_amount=Coalesce(
                    Sum(total_amount),
                    Value(DECIMAL_ZERO),
                    output_field=DecimalField(max_digits=14, decimal_places=2),
                ),
            )
            .order_by('quantity', 'total_amount', 'name')[:limit]
        )

        data = [
            {
                'product_id': product.id,
                'name': product.name,
                'barcode': product.barcode,
                'quantity': product.quantity,
                'total_amount': product.total_amount,
            }
            for product in rows
        ]
        serializer = TopProductSerializer(data, many=True)
        return Response(serializer.data)


class RegionalSalesView(APIView):
    permission_classes = [IsManager]

    def get(self, request):
        data = [_warehouse_stats(warehouse_id) for warehouse_id in _warehouse_ids()]
        data.sort(key=lambda row: row['total_sales'], reverse=True)
        serializer = WarehouseStatsSerializer(data, many=True)
        return Response(serializer.data)
