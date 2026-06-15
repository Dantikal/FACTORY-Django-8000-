# apps/events/publisher.py

def publish_shipment_created(shipment_id, shipment_data):
    """
    Отправляет событие о создании отгрузки
    """
    # TODO: Реализовать отправку в RabbitMQ/Kafka/другой брокер
    print(f"Event: shipment_created - ID: {shipment_id}")
    return True

def publish_shipment_status_changed(shipment_id, old_status, new_status):
    """
    Отправляет событие об изменении статуса отгрузки
    """
    print(f"Event: shipment_status_changed - ID: {shipment_id}, {old_status} -> {new_status}")
    return True

def publish_reception_completed(delivery_id, warehouse_id, amount, acceptance_type):
    """
    Отправляет событие о завершении приемки
    """
    print(f"Event: reception_completed - Delivery ID: {delivery_id}, Warehouse: {warehouse_id}, Amount: {amount}, Type: {acceptance_type}")
    return True