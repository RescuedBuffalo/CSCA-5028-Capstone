"""
Worker script for processing RabbitMQ tasks related to data collection.

This script:
- Connects to a RabbitMQ instance.
- Consumes messages from a queue (`data_collection`).
- Processes tasks based on the message content.
- Publishes the next task in a predefined order after completing the current one.
- Handles graceful shutdown on receiving termination signals.

Dependencies:
- `pika` for RabbitMQ connection.
- `flask` for app context handling.
- Custom fetch scripts for collecting player, team, roster, and game data.
"""

import signal
import pika
import sys
import os
from dotenv import load_dotenv
import ssl
import json
from datetime import datetime
from app.scripts.fetch_player_data import fetch_player_data
from app.scripts.fetch_team_data import fetch_team_data
from app.scripts.fetch_roster_data import fetch_roster_data
from app.scripts.fetch_game_data import fetch_game_data
from app import create_app

# Load environment variables and Flask app context
load_dotenv('.env')
app = create_app(os.getenv("CONFIG_NAME"))

# Global variables for RabbitMQ connection and channel
connection = None
channel = None

def graceful_shutdown(signum, frame):
    """
    Handle SIGINT or SIGTERM signals for graceful shutdown of the worker.

    Closes the RabbitMQ channel and connection to ensure a clean exit.
    Args:
        signum (int): Signal number.
        frame: Current stack frame (unused).
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
    Process the task from a RabbitMQ message.

    This function determines the type of task and executes the corresponding data fetch script.

    Args:
        ch: The channel object.
        method: Delivery method of the message.
        properties: Message properties.
        body (bytes): The message body, containing task information in JSON format.
    """
    message = json.loads(body)

    with app.app_context():  # Run tasks within the Flask app context
        if message['task'] == 'fetch_team_data':
            print('Fetching team data...')
            fetch_team_data()
            print('Fetched team data.')
        elif message['task'] == 'fetch_roster_data':
            fetch_roster_data()
            print('Fetched roster data.')
        elif message['task'] == 'fetch_player_data':
            fetch_player_data()
            print('Fetched player data.')
        elif message['task'] == 'fetch_game_data':
            fetch_game_data()
            print('Fetched game data.')

    print(f"Received message: {message.get('task')}")

def publish_next_task(channel, body):
    """
    Publish the next task in a predefined sequence to the RabbitMQ queue.

    The task sequence is:
        1. `fetch_team_data`
        2. `fetch_roster_data`
        3. `fetch_player_data`
        4. `fetch_game_data`

    Args:
        channel: RabbitMQ channel to publish the next task.
        body (bytes): JSON-encoded message containing the current task.
    """
    task_order = ['fetch_team_data', 'fetch_roster_data', 'fetch_player_data', 'fetch_game_data']

    message = json.loads(body)
    current_task = message['task']

    if current_task in task_order:
        current_index = task_order.index(current_task)
        if current_index < len(task_order) - 1:
            next_task = task_order[current_index + 1]

            task = {
                'task': next_task,
                'timestamp': datetime.now().isoformat()
            }

            body = json.dumps(task)

            channel.basic_publish(
                exchange='',
                routing_key='data_collection',
                body=body.encode('utf-8'),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make the message persistent
                )
            )

            print(f"Published next task: {task}")

def callback(ch, method, properties, body):
    """
    Callback function triggered when a new message is received from the RabbitMQ queue.

    This function:
    - Processes the current task.
    - Publishes the next task in the sequence.
    - Acknowledges the message.

    Args:
        ch: The channel object.
        method: Delivery method of the message.
        properties: Message properties.
        body (bytes): The message body, containing task information in JSON format.
    """
    body = body.decode('utf-8')

    process_task(ch, method, properties, body)
    publish_next_task(ch, body)

    ch.basic_ack(delivery_tag=method.delivery_tag)  # Acknowledge the message

def main():
    """
    Main entry point for the worker script.

    This function:
    - Establishes a RabbitMQ connection and channel.
    - Declares the `data_collection` queue.
    - Starts consuming messages from the queue.
    - Handles graceful shutdown via signal handling.
    """
    global connection, channel

    rabbitmq_url = os.getenv("RABBITMQ_URL")
    parameters = pika.URLParameters(rabbitmq_url)

    # Configure SSL options for secure RabbitMQ connection
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
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)

    main()