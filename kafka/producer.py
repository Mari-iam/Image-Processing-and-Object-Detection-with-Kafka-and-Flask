from confluent_kafka import Producer
import json

TOPIC_NAME = 'mariam-mahmoud'
ERROR_TOPIC = 'mariam-mahmoud-error'
COMPLETED_TOPIC = 'mariam-mahmoud-completed'

p = Producer({'bootstrap.servers': '34.138.205.183:9094,34.138.104.233:9094,34.138.118.154:9094'})

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} ")

def produce_message(topic, message):
    p.produce(topic, value=json.dumps(message).encode('utf-8'), callback=delivery_report)
    p.flush()

def on_image_upload(image_id, filename):
    message = {'id': image_id, 'filename': filename}
    try:
        produce_message(TOPIC_NAME, message)
        print(f"Produced message for image: {image_id}")
    except Exception as e:
        error_message = {'id': image_id, 'error': str(e)}
        produce_message(ERROR_TOPIC, error_message)
        print(f"Produced error message for {image_id} with error: {e}")
    else:
        completed_message = {'id': image_id, 'status': 'completed'}
        produce_message(COMPLETED_TOPIC, completed_message)
        print(f"Produced completed message for image: {image_id}")
