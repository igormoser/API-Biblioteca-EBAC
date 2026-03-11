from kafka import KafkaProducer
import json
import os

KAFKA_SERVER = os.environ.get('KAFKA_SERVER', 'localhost:9092')

producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)

def get_producer():
    global producer
    if producer is None:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_SERVER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    return producer

def enviar_evento(topic: str, event: dict):
    prod = get_producer()
    prod.send(topic, event)
    prod.flush()
