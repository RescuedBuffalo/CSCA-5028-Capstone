import pytest
from unittest.mock import patch, MagicMock
import pika
import worker, producer
from datetime import datetime
from json import dumps
from app import create_app, db

@pytest.fixture
def mock_rabbitmq_connection():
    with patch('pika.BlockingConnection') as mock_blocking_connection:
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_connection.channel.return_value = mock_channel
        mock_blocking_connection.return_value = mock_connection
        yield mock_connection

def test_produce_tasks(mock_rabbitmq_connection):
    # Publish our task to the Queue
    producer.publish_task(mock_rabbitmq_connection.channel, mock_rabbitmq_connection)

    assert mock_rabbitmq_connection.channel.basic_publish.call_count == 1

@patch('worker.process_task')
def test_consume_tasks(mock_process_task, mock_rabbitmq_connection):
    mock_channel = mock_rabbitmq_connection.channel.return_value

    def mock_callback(ch, method, properties, body):
        mock_process_task(body)

    mock_channel.basic_consume.side_effect = lambda *args, **kwargs: mock_callback(
            None, None, None, dumps({"task": "fetch_team_data", "timestamp": datetime.now().isoformat()})
        )

    task = {
        'task': 'fetch_team_data',
        'timestamp': datetime.now().isoformat()
    }

    worker.main()
    
    assert mock_channel.basic_consume.call_count == 1

def test_message_acknowledgment(mock_rabbitmq_connection):
    app = create_app('testing')

    with app.app_context():
        db.create_all()

        mock_channel = MagicMock()
        mock_rabbitmq_connection.channel.return_value = mock_channel

        task = dumps({
            'task': 'fetch_team_data',
            'timestamp': datetime.now().isoformat()
        })

        worker.callback(mock_channel, MagicMock(), MagicMock(), task.encode('utf-8'))

        mock_channel.basic_ack.assert_called_once()