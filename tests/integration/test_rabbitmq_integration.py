import pytest
import pika
import worker
from datetime import datetime
from json import loads, dumps
import ssl
import os
import time
from app import create_app
from dotenv import load_dotenv

@pytest.fixture
def client():
    load_dotenv()

    app = create_app('testing')

    yield app.test_client()

def test_rabbitmq_integration(client):

    with client.application.app_context():
        rabbitmq_url = os.getenv("RABBITMQ_URL")
        if not rabbitmq_url:
            pytest.fail("Environment variable RABBITMQ_URL is not set.")

        parameters = pika.URLParameters(rabbitmq_url)

        # Configure SSL
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        parameters.ssl_options = pika.SSLOptions(context)

        # Establish connection and channel
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        # Declare the queue
        queue_name = "test_queue"
        channel.queue_declare(queue=queue_name, durable=True)

        # Publish a test task
        task = {"task": "fetch_team_data", "timestamp": datetime.now().isoformat()}
        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=dumps(task),  # Serialize to JSON
            properties=pika.BasicProperties(delivery_mode=2),  # Make the message persistent
        )

        processed_tasks = []

        def callback(ch, method, properties, body):
            try:
                # Decode the body and append it to processed_tasks
                processed_tasks.append(loads(body.decode()))  # Decode JSON message
                print('PROCESSING TASK {}'.format(processed_tasks))
                # Pass the raw body to `worker.process_task` as expected
                worker.process_task(ch, method, properties, body)

                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                ch.basic_nack(delivery_tag=method.delivery_tag)
                pytest.fail(f"Error in callback: {e}")

        # Start consuming messages
        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=False)

        try:
            start_time = time.time()
            while len(processed_tasks) == 0 and time.time() - start_time < 10:
                connection.process_data_events(time_limit=1)
        finally:
            # Cleanup: delete the queue and close the connection
            if not channel.is_closed:
                channel.queue_delete(queue=queue_name)
            if not connection.is_closed:
                connection.close()

        # Assertions to verify the task processing
        assert len(processed_tasks) == 1, "No task was processed."
        assert processed_tasks[0]["task"] == "fetch_team_data", "Processed task does not match the published task."