from confluent_kafka import Consumer, KafkaException, KafkaError
import requests
import json
import torch
from PIL import Image
import numpy as np
import os
from producer import produce_message

# Kafka consumer configuration
conf = {
    'bootstrap.servers': '34.138.205.183:9094,34.138.104.233:9094,34.138.118.154:9094',
    'group.id': 'image-group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)
TOPIC_NAME = 'mariam-mahmoud'
ERROR_TOPIC = 'mariam-mahmoud-error'
COMPLETED_TOPIC = 'mariam-mahmoud-completed'
consumer.subscribe([TOPIC_NAME])

# Load the YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

def detect_object(image_path):
    try:
        # Load and preprocess the image
        image = Image.open(image_path).convert('RGB')
        results = model(image)
        detections = results.pandas().xyxy[0]

        if not detections.empty:
            # Get the label of the top detection
            detected_object = detections.iloc[0]['name']
        else:
            detected_object = 'unknown'

        return detected_object
    except Exception as e:
        print(f"Error in object detection: {e}")
        return 'unknown'

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

            image_path = f"images/{filename}"

            if os.path.exists(image_path):
                try:
                    detected_object = detect_object(image_path)
                    response = requests.put(f'http://127.0.0.1:5000/object/{image_id}', json={"object": detected_object})
                    response.raise_for_status()
                    print(f"Updated image {image_id} with label {detected_object}")

                    completed_message = {'id': image_id, 'status': 'completed'}
                    produce_message(COMPLETED_TOPIC, completed_message)
                except Exception as e:
                    print(f"Error processing image {image_id}: {e}")
                    error_message = {'id': image_id, 'error': str(e)}
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
