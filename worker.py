import signal
import pika
import sys
import os
from dotenv import load_dotenv
import ssl
import json
from datetime import datetime
from scripts import fetch_player_data, fetch_team_data, fetch_roster_data, fetch_game_data

load_dotenv('.env')

# Global variable to hold the connection
connection = None
channel = None

def graceful_shutdown(signum, frame):
    """
    Handle SIGINT or SIGTERM signals for graceful shutdown.
    """
    print("Shutting down gracefully...")
    if channel and not channel.is_closed:
        print("Closing RabbitMQ channel...")
        channel.close()
    if connection and not connection.is_closed:
        print("Closing RabbitMQ connection...")
        connection.close()
    sys.exit(0)

def process_task(ch, method, properties, body):
    """
    Callback function to process messages.
    """
    message = json.loads(body)
    if message['task'] == 'fetch_player_data':
        fetch_player_data()
        print('Fetched player data.')
    elif message['task'] == 'fetch_team_data':
        fetch_team_data()
        print('Fetched team data.')
    elif message['task'] == 'fetch_roster_data':
        fetch_roster_data()
        print('Fetched roster data.')
    elif message['task'] == 'fetch_game_data':
        fetch_game_data()
        print('Fetched game data.')
        
    print(f"Received message: {body.decode()}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def publish_next_task(channel, current_task):
    task_order = ['fetch_team_data', 'fetch_roster_data', 'fetch_player_data', 'fetch_game_data']

    if current_task in task_order:
        current_index = task_order.index(current_task)
        if current_index < len(task_order) - 1:
            next_task = task_order[current_index + 1]

            task = {
                'task': next_task,
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

            print(f"Published next task: {task}")

def callback(ch, method, properties, body):
    task = json.loads(body)
    task_name = task.get('task')

    process_task(task_name)

    publish_next_task(ch, task_name)

    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    global connection, channel

    # Setup RabbitMQ connection and channel
    rabbitmq_url = os.getenv("RABBITMQ_URL")
    parameters = pika.URLParameters(rabbitmq_url)

    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    parameters.ssl_options = pika.SSLOptions(context)

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # Declare the queue
    queue_name = "data_collection"
    channel.queue_declare(queue=queue_name, durable=True)

    # Set up a consumer
    channel.basic_consume(queue=queue_name, on_message_callback=callback)

    print("Worker started. Waiting for messages...")

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        graceful_shutdown(None, None)

if __name__ == "__main__":
    # Handle termination signals for graceful shutdown
    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)

    # Run the main worker loop
    main()
