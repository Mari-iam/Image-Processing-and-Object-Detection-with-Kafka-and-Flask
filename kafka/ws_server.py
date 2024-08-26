import asyncio
import websockets
from kafka import KafkaConsumer
import json


WS_PORT = 8765 #8766

# Kafka configuration
KAFKA_SERVERS = ['34.138.205.183:9094', '34.138.104.233:9094', '34.138.118.154:9094']  
KAFKA_TOPIC = 'mariam-mahmoud-completed'  

# Create a Kafka consumer
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_SERVERS,
    group_id='websocket-group',
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# List to keep track of connected WebSocket clients
connected_websockets = set()

async def handle_connection(websocket, path):
    # Register new connection
    connected_websockets.add(websocket)
    try:
        async for _ in websocket:  # Keeping the connection alive
            pass
    finally:
        # Unregister connection on close
        connected_websockets.remove(websocket)

async def consume_and_send():
    async with websockets.serve(handle_connection, 'localhost', WS_PORT):
        while True:
            msg = consumer.poll(timeout_ms=1000)
            for _, messages in msg.items():
                for message in messages:
                    print(f"Received message from Kafka: {message.value}")
                    # Broadcast the message to all connected WebSocket clients
                    for ws in connected_websockets:
                        try:
                            await ws.send(json.dumps(message.value))
                        except Exception as e:
                            print(f"Error sending message to WebSocket client: {e}")

async def main():
    await consume_and_send()

if __name__ == "__main__":
    asyncio.run(main())
