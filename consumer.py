# consumer.py
import pika
import json
import time
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from main import LoginMetadata, engine

SessionLocal = sessionmaker(bind=engine)

# WAŻNE: w docker-compose używasz nazwy serwisu, NIE localhost
RABBITMQ_URL = "amqp://guest:guest@rabbitmq:5672/"

def connect():
    while True:
        try:
            print("Connecting to RabbitMQ...")
            params = pika.URLParameters(RABBITMQ_URL)
            connection = pika.BlockingConnection(params)
            print("Connected to RabbitMQ ✅")
            return connection
        except pika.exceptions.AMQPConnectionError:
            print("RabbitMQ not ready, retrying in 5s...")
            time.sleep(5)

def callback(ch, method, properties, body):
    print("Received message:", body)

    data = json.loads(body)
    db = SessionLocal()

    try:
        metadata = LoginMetadata(
            username=data["username"],
            ip_address=data["ip_address"],
            city=data.get("city"),
            region=data.get("region"),
            country=data.get("country"),
            screen_width=data.get("screen_width"),
            screen_height=data.get("screen_height"),
            timezone=data.get("timezone"),
            user_agent=data.get("user_agent"),
            created_at=datetime.fromisoformat(data["created_at"])
            if data.get("created_at") else datetime.utcnow()
        )

        db.add(metadata)
        db.commit()
        print("Saved to DB ✅")

    except Exception as e:
        print("Error processing message:", e)
        db.rollback()

    finally:
        db.close()

    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == "__main__":
    connection = connect()
    channel = connection.channel()

    channel.queue_declare(queue="login_metadata", durable=True)
    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(
        queue="login_metadata",
        on_message_callback=callback
    )

    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()
