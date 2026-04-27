import pika
import json

RABBITMQ_URL = "amqp://guest:guest@rabbitmq:5672/"

def send_to_queue(queue_name: str, message: dict):
    """Wysyła wiadomość do kolejki RabbitMQ"""
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        )
    )
    connection.close()
