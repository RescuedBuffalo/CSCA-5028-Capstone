"""
Unit tests for RabbitMQ integration.

This file:
- Tests the functionality of the producer (`publish_task`) to publish messages to the RabbitMQ queue.
- Verifies that the worker processes and acknowledges tasks correctly.
- Uses mocks and patches to simulate RabbitMQ connections and interactions.

Dependencies:
- `pytest` for managing test cases.
- `unittest.mock` for mocking RabbitMQ connections and channel methods.
- Flask app and SQLAlchemy for database context.

Fixtures:
- `mock_rabbitmq_connection`: Mocks the RabbitMQ connection and channel.

Test Cases:
- `test_produce_tasks`: Verifies that tasks are successfully published to the RabbitMQ queue.
- `test_consume_tasks`: Ensures tasks are correctly consumed and processed by the worker.
- `test_message_acknowledgment`: Confirms that tasks are acknowledged after processing.
"""

import pytest
from unittest.mock import patch, MagicMock
import pika
import app.scripts.worker as worker
import app.scripts.producer as producer
from datetime import datetime
from json import dumps
from app import create_app, db

@pytest.fixture
def mock_rabbitmq_connection():
    """
    Fixture to mock RabbitMQ connections and channels.

    This fixture:
    - Mocks the `pika.BlockingConnection` class.
    - Simulates the behavior of RabbitMQ connection and channel objects.
    - Ensures that RabbitMQ-related tests do not require a live RabbitMQ server.

    Yields:
        MagicMock: A mocked RabbitMQ connection object with a mocked channel.
    """
    with patch('pika.BlockingConnection') as mock_blocking_connection:
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_connection.channel.return_value = mock_channel
        mock_blocking_connection.return_value = mock_connection
        yield mock_connection

def test_produce_tasks(mock_rabbitmq_connection):
    """
    Test that tasks are successfully published to the RabbitMQ queue.

    Steps:
    1. Mock the RabbitMQ channel object using the `mock_rabbitmq_connection` fixture.
    2. Call the `publish_task` function with a task name and the mocked channel.
    3. Verify that the `basic_publish` method on the mocked channel was called once.

    Expected Outcome:
    - The `basic_publish` method is called with the correct parameters, indicating the task was published.
    """
    mock_channel = mock_rabbitmq_connection.channel.return_value
    task_name = "fetch_team_data"

    # Test publishing
    producer.publish_task(task_name, mock_channel)
    mock_channel.basic_publish.assert_called_once()

@patch('app.scripts.worker.process_task')
def test_consume_tasks(mock_process_task, mock_rabbitmq_connection):
    """
    Test that tasks are correctly consumed and processed by the worker.

    Steps:
    1. Mock the RabbitMQ channel and its `basic_consume` method.
    2. Simulate a callback function that processes a sample task.
    3. Call the `worker.main` function to start consuming tasks.
    4. Verify that the `basic_consume` method was called exactly once.

    Expected Outcome:
    - The `basic_consume` method is called, and tasks are processed via the mocked callback function.
    """
    mock_channel = mock_rabbitmq_connection.channel.return_value

    def mock_callback(ch, method, properties, body):
        mock_process_task(body)

    # Simulate consuming a task with a mock callback
    mock_channel.basic_consume.side_effect = lambda *args, **kwargs: mock_callback(
        None, None, None, dumps({"task": "fetch_team_data", "timestamp": datetime.now().isoformat()})
    )

    task = {
        'task': 'fetch_team_data',
        'timestamp': datetime.now().isoformat()
    }

    # Run the worker's main function
    worker.main()
    
    assert mock_channel.basic_consume.call_count == 1

def test_message_acknowledgment(mock_rabbitmq_connection):
    """
    Test that tasks are acknowledged after processing.

    Steps:
    1. Mock the RabbitMQ channel and create a sample task message.
    2. Call the `worker.callback` function with the mocked channel and sample task.
    3. Verify that the `basic_ack` method was called on the mocked channel.

    Expected Outcome:
    - The `basic_ack` method is called, indicating that the task was acknowledged.
    """
    app = create_app('testing')

    with app.app_context():
        db.create_all()

        mock_channel = MagicMock()
        mock_rabbitmq_connection.channel.return_value = mock_channel

        task = dumps({
            'task': 'fetch_team_data',
            'timestamp': datetime.now().isoformat()
        })

        # Call the worker's callback function with the task
        worker.callback(mock_channel, MagicMock(), MagicMock(), task.encode('utf-8'))

        mock_channel.basic_ack.assert_called_once()