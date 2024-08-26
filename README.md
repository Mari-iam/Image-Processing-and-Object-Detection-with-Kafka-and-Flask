# Image Processing and Object Detection with Kafka and Flask
This project implements an image processing pipeline that integrates Kafka, Flask, and YOLOv5 for real-time object detection and label updating. The system includes a Kafka producer to send image metadata, a Kafka consumer to process images using YOLOv5, a Flask server to update image labels, and WebSocket communication to interact with a web interface.
## Requirements
* Python 3.7+
* Kafka
* Flask
* TensorFlow or PyTorch
* YOLOv5
* WebSocket library
## Usage
### 1-Start the Kafka consumer: 
### python consumer.py
This script consumes messages from a Kafka topic, performs object detection on the received images using YOLOv5, updates the image labels via the Flask endpoint, and sends status updates to the WebSocket server.
### python bw_consumer.py
This script consumes messages from a Kafka topic, converts the image to B&W, updates the image labels via the Flask endpoint, and sends status updates to the WebSocket server.
### 2-Run the Flask application:
### python server.py
This script starts the Flask server which handles image label updates and communicates with the WebSocket server.
## Error Handling
* If an error occurs during image processing or detection, an error message is sent to the mariam-mahmoud-error Kafka topic and published to the WebSocket server.
* Upon successful processing, a completed message is sent to the mariam-mahmoud-completed Kafka topic and published to the WebSocket server.
## WebSocket Integration
* The project includes WebSocket functionality to communicate task status updates (completed or error) with a web interface.
* Status updates are sent to the WebSocket server, which then communicates with the browser to refresh tasks upon completion or failure.
## Troubleshooting
* Ensure all services (Kafka, Flask server, WebSocket server) are running and properly configured.
* Check logs for detailed error messages.

