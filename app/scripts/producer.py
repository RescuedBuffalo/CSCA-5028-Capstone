"""
Producer script for RabbitMQ task management.

This script:
- Publishes tasks to a RabbitMQ queue (`data_collection`) in a predefined sequence.
- Handles secure RabbitMQ connections using SSL.
- Processes and publishes tasks like fetching team, roster, player, and game data.

Dependencies:
- `pika` for RabbitMQ communication.
- `dotenv` for loading environment variables.
- `ssl` for secure RabbitMQ connections.

Usage:
Run this script to enqueue a new task into the `data_collection` queue. Each task is published 
with persistence, ensuring that messages are not lost in case of a RabbitMQ restart.

Preconditions:
- RabbitMQ server must be running and accessible via `RABBITMQ_URL`.
- Environment variables must be set in a `.env` file, including:
  - `RABBITMQ_URL`: The RabbitMQ connection URL.
"""

import pika
import ssl
import json
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from a .env file
load_dotenv()

def connect_to_rabbitmq():
    """
    Establish a connection to the RabbitMQ server with SSL.

    Returns:
        connection (pika.BlockingConnection): The RabbitMQ connection object.
        channel (pika.channel.Channel): The RabbitMQ channel object.
    
    Environment Variables:
        - `RABBITMQ_URL`: RabbitMQ connection URL (must be set in the `.env` file).

    Raises:
        pika.exceptions.AMQPError: If the connection or channel cannot be established.
    """
    try:
        rabbitmq_url = os.getenv("RABBITMQ_URL")
        parameters = pika.URLParameters(rabbitmq_url)

        # Configure SSL context for secure RabbitMQ communication
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        parameters.ssl_options = pika.SSLOptions(context)

        # Establish connection and channel
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        # Ensure the queue is declared as durable
        channel.queue_declare(queue='data_collection', durable=True)

        return connection, channel
    except Exception as e:
        print(f"Error connecting to RabbitMQ: {e}")
        raise

def publish_task(task_name, channel):
    """
    Publish a task to the RabbitMQ queue.

    Args:
        task_name (str): The name of the task to enqueue (e.g., `fetch_team_data`).
        channel (pika.channel.Channel): The RabbitMQ channel object.

    Raises:
        Exception: If the message cannot be published.
    """
    try:
        task = {
            'task': task_name,
            'timestamp': datetime.now().isoformat()  # Include a timestamp for traceability
        }

        # Convert the task to JSON and publish it to the queue
        channel.basic_publish(
            exchange='',
            routing_key='data_collection',
            body=json.dumps(task).encode('utf-8'),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make the message persistent
            )
        )

        print(f"Task published: {task}")
    except Exception as e:
        print(f"Error publishing task: {e}")
        raise

def main():
    """
    Main function to publish a predefined task sequence to RabbitMQ.

    The task sequence is:
        1. `fetch_team_data`
        2. `fetch_roster_data`
        3. `fetch_player_data`
        4. `fetch_game_data`

    This function:
    - Connects to RabbitMQ.
    - Publishes each task in the sequence.
    - Closes the RabbitMQ connection after publishing all tasks.

    Raises:
        Exception: If any error occurs during the RabbitMQ connection or task publication.
    """
    try:
        # Connect to RabbitMQ
        connection, channel = connect_to_rabbitmq()

        # Define the sequence of tasks
        tasks = ['fetch_team_data', 'fetch_roster_data', 'fetch_player_data', 'fetch_game_data']

        # Publish each task in the sequence
        for task_name in tasks:
            publish_task(task_name, channel)

        print("All tasks published successfully.")

        # Close the RabbitMQ connection
        channel.close()
        connection.close()

    except Exception as e:
        print(f"Error in producer script: {e}")
        raise

if __name__ == "__main__":
    """
    Entry point for the producer script.

    This section ensures that the script is only executed when run directly, 
    and not when imported as a module.
    """
    main()