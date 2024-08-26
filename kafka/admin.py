from confluent_kafka.admin import AdminClient, NewTopic

# Kafka admin client configuration
conf = {
    'bootstrap.servers': '34.138.205.183:9094,34.138.104.233:9094,34.138.118.154:9094'
}

admin_client = AdminClient(conf)
topic_name = 'mariam-mahmoud'

def create_topic():
    topic_list = [NewTopic(topic_name, num_partitions=3, replication_factor=1)]
    fs = admin_client.create_topics(topic_list)
    for topic, future in fs.items():
        try:
            future.result()
            print(f"Topic {topic} created.")
        except Exception as e:
            print(f"Failed to create topic {topic}: {e}")

def delete_topic():
    fs = admin_client.delete_topics([topic_name])
    for topic, future in fs.items():
        try:
            future.result()
            print(f"Topic {topic} deleted.")
        except Exception as e:
            print(f"Failed to delete topic {topic}: {e}")

if __name__ == "__main__":
    # Uncomment the one you need
    # delete_topic()
    create_topic()
