import pika
import json
from datetime import datetime
import os
import ssl

def publish_task(channel, connection):

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

def connect():
    rabbitmq_url = os.getenv('RABBITMQ_URL')
    parameters = pika.URLParameters(rabbitmq_url)

    # Skip SSL verification for testing
    if os.getenv('CONFIG_NAME') == 'testing':
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        parameters.ssl_options = pika.SSLOptions(context)

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    return channel, connection

def main():
    channel, connection = connect()

    publish_task(channel, connection)

if __name__ == "__main__":

    main()