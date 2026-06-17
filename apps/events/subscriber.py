import json
import redis
import threading
from django.conf import settings
from apps.invoices.services import InvoiceService

class RedisSubscriber(threading.Thread):
    def __init__(self):
        super().__init__()
        self.redis_client = redis.StrictRedis.from_url(settings.REDIS_URL, decode_responses=True)
        self.pubsub = self.redis_client.pubsub()
        self.pubsub.subscribe("warehouse.dispatch.created")
        self.daemon = True

    def run(self):
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    InvoiceService.create_from_dispatch(data)
                except Exception as e:
                    print(f"Error processing warehouse.dispatch.created: {e}")

# This part is usually initialized in apps.py or a management command
def start_subscriber():
    subscriber = RedisSubscriber()
    subscriber.start()
