from apps.payments.models import WarehouseDebt


def increase_warehouse_debt(warehouse_id, amount):
    """Increase warehouse debt by the given amount."""
    debt, created = WarehouseDebt.objects.get_or_create(
        warehouse_id=warehouse_id,
        defaults={'amount': 0}
    )
    debt.amount += amount
    debt.save()
