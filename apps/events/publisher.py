import json
import redis
from django.conf import settings

# Initialize Redis client
redis_client = redis.StrictRedis.from_url(settings.REDIS_URL, decode_responses=True)

def publish_shipment_created(shipment_id, warehouse_id, items_data):
    """
    Отправляет событие о создании отгрузки
    """
    event_data = {
        "shipment_id": str(shipment_id),
        "warehouse_id": str(warehouse_id),
        "items": items_data
    }
    redis_client.publish("factory.shipment.created", json.dumps(event_data))
    return True

def publish_reception_completed(delivery_id, warehouse_id, items_data):
    """
    Отправляет событие о завершении приемки
    """
    event_data = {
        "delivery_id": str(delivery_id),
        "warehouse_id": str(warehouse_id),
        "items": items_data
    }
    redis_client.publish("factory.reception.completed", json.dumps(event_data))
    return True

def publish_factory_payment_sent(payment_id, warehouse_id, amount, paid_at):
    """
    Отправляет событие об отправке платежа
    """
    event_data = {
        "payment_id": str(payment_id),
        "warehouse_id": str(warehouse_id),
        "amount": float(amount),
        "paid_at": paid_at.isoformat() if hasattr(paid_at, 'isoformat') else str(paid_at)
    }
    redis_client.publish("factory.payment.sent", json.dumps(event_data))
    return True
