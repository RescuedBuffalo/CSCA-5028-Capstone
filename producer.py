import pika
import json
from datetime import datetime
import os
import ssl

def publish_message():
    rabbitmq_url = os.getenv("RABBITMQ_URL")

    parameters = pika.URLParameters(rabbitmq_url)
    
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(queue='data_collection', durable=True)

    task = {
        'task': 'fetch_team_data',
        'timestamp': datetime.now().isoformat()
    }

    channel.basic_publish(
        exchange='',
        routing_key='data_collection',
        body=json.dumps(task),
        properties=pika.BasicProperties(
            delivery_mode=2,
        )
    )

    print(f"Published task: {task}")

    connection.close()

if __name__ == "__main__":
    publish_message()