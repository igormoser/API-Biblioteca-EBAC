from kafka import KafkaProducer
import json
import os

KAFKA_SERVER = os.environ.get('KAFKA_SERVER', 'localhost:9092')
producer = None

def get_producer():
    global producer

    if producer is None:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_SERVER,
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
        )

    return producer

def enviar_evento(topic: str, event: dict):
    prod = get_producer()
    future = prod.send(topic, event)
    prod.flush()
    return future.get(timeout=10)
