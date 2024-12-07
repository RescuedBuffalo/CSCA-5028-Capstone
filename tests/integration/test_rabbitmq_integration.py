"""
Integration test for RabbitMQ task processing.

This file:
- Verifies the integration between RabbitMQ, the `worker` script, and the Flask application.
- Publishes a test task to a RabbitMQ queue.
- Simulates message consumption and ensures the task is correctly processed by the `worker`.

Dependencies:
- `pytest` for managing test cases and fixtures.
- `pika` for RabbitMQ communication.
- Flask app for application context.
- `dotenv` for loading environment variables.

Fixtures:
- `client`: Sets up the Flask app and provides a test client.

Test Cases:
- `test_rabbitmq_integration`: Verifies task publishing, consuming, and processing via RabbitMQ.

Preconditions:
- RabbitMQ server must be accessible via the `RABBITMQ_URL` environment variable.
"""

import pytest
import pika
import app.scripts.worker as worker
from datetime import datetime
from json import loads, dumps
import ssl
import os
import time
from app import create_app
from dotenv import load_dotenv


@pytest.fixture
def client():
    """
    Pytest fixture to provide a test client for the Flask app.

    This fixture:
    - Loads environment variables using `dotenv`.
    - Creates the Flask app in testing mode.

    Yields:
        Flask test client for HTTP request simulation.
    """
    load_dotenv()  # Load environment variables

    # Create the app instance for testing
    app = create_app('testing')

    yield app.test_client()  # Provide the test client


def test_rabbitmq_integration(client):
    """
    Test RabbitMQ integration with task publishing and consumption.

    Steps:
    1. Load the `RABBITMQ_URL` environment variable and configure RabbitMQ connection.
    2. Declare a test queue (`test_queue`) for publishing tasks.
    3. Publish a serialized JSON task to the test queue.
    4. Define a `callback` function to simulate task consumption and processing.
    5. Consume messages from the queue and ensure the task is processed within a timeout.
    6. Cleanup: Delete the test queue and close the RabbitMQ connection.

    Assertions:
    - Verify that the task is processed by the `worker`.
    - Ensure the processed task matches the published task.

    Expected Outcome:
    - The task is correctly published to the queue, consumed, and processed.
    """
    with client.application.app_context():
        # Load RabbitMQ URL from environment variables
        rabbitmq_url = os.getenv("RABBITMQ_URL")
        if not rabbitmq_url:
            pytest.fail("Environment variable RABBITMQ_URL is not set.")

        parameters = pika.URLParameters(rabbitmq_url)

        # Configure SSL for RabbitMQ connection
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        parameters.ssl_options = pika.SSLOptions(context)

        # Establish connection and channel
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        # Declare the test queue
        queue_name = "test_queue"
        channel.queue_declare(queue=queue_name, durable=True)

        # Publish a test task to the queue
        task = {"task": "fetch_team_data", "timestamp": datetime.now().isoformat()}
        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=dumps(task),  # Serialize to JSON
            properties=pika.BasicProperties(delivery_mode=2),  # Make the message persistent
        )

        # List to store processed tasks
        processed_tasks = []

        def callback(ch, method, properties, body):
            """
            Callback function to process messages from the queue.

            Args:
                ch: The channel object.
                method: Delivery method.
                properties: Message properties.
                body (bytes): The message body containing the task as JSON.
            """
            try:
                # Decode and append the task to the list
                processed_tasks.append(loads(body.decode()))  # Deserialize JSON message
                print(f'PROCESSING TASK: {processed_tasks}')
                # Pass the raw body to the worker's `process_task` function
                worker.process_task(ch, method, properties, body)

                # Acknowledge the task
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                # Negatively acknowledge the task in case of an error
                ch.basic_nack(delivery_tag=method.delivery_tag)
                pytest.fail(f"Error in callback: {e}")

        # Start consuming messages
        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=False)

        try:
            # Timeout for consuming messages
            start_time = time.time()
            while len(processed_tasks) == 0 and time.time() - start_time < 10:
                connection.process_data_events(time_limit=1)
        finally:
            # Cleanup: delete the queue and close the connection
            if not channel.is_closed:
                channel.queue_delete(queue=queue_name)
            if not connection.is_closed:
                connection.close()

        # Assertions to verify task processing
        assert len(processed_tasks) == 1, "No task was processed."
        assert processed_tasks[0]["task"] == "fetch_team_data", "Processed task does not match the published task."