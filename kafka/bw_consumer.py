from confluent_kafka import Consumer, KafkaException, KafkaError
import json
import requests
from PIL import Image
import os
from producer import produce_message

conf = {
    'bootstrap.servers': '34.138.205.183:9094,34.138.104.233:9094,34.138.118.154:9094',
    'group.id': 'bw-image-group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)
TOPIC_NAME = 'mariam-mahmoud'
ERROR_TOPIC = 'mariam-mahmoud-error'
COMPLETED_TOPIC = 'mariam-mahmoud-completed'
consumer.subscribe([TOPIC_NAME])

def convert_image_to_bw(image_path):
    try:
        img = Image.open(image_path).convert('L')
        img.save(image_path)
        return True
    except Exception as e:
        print(f"Failed to convert image: {e}")
        return False

def consume_messages():
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    raise KafkaException(msg.error())

            message_value = msg.value().decode('utf-8')
            message_data = json.loads(message_value)
            image_id = message_data['id']
            filename = message_data['filename']
            print(f"Received message for image: {image_id}")

            image_path = os.path.join("images", filename)

            if os.path.exists(image_path):
                if convert_image_to_bw(image_path):
                    completed_message = {'id': image_id, 'status': 'converted to B&W'}
                    produce_message(COMPLETED_TOPIC, completed_message)
                else:
                    error_message = {'id': image_id, 'error': 'Failed to convert to B&W'}
                    produce_message(ERROR_TOPIC, error_message)
            else:
                error_message = {'id': image_id, 'error': 'File not found'}
                produce_message(ERROR_TOPIC, error_message)

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == "__main__":
    consume_messages()
