import pytest
from unittest.mock import patch
from app import create_app

@pytest.fixture
def app():
    app = create_app('testing')
    app.testing = True 
    with app.app_context(): 
        yield app

@pytest.fixture
def client(app):
    with app.test_client() as client:  
        yield client

def test_metrics_endpoint(client):
    with patch('prometheus_client.exposition.generate_latest') as mock_generate_latest:
        with patch('prometheus_client.exposition.generate_latest') as mock_generate_latest:
            mock_generate_latest.return_value = b'# HELP app_info Application info\n# TYPE app_info gauge\napp_info{version="1.0.0"} 1\n'

            # Make a GET request to the /metrics endpoint
            response = client.get('/metrics')

            # Assertions
            assert response.status_code == 200
            assert response.content_type == 'text/plain; version=0.0.4; charset=utf-8'
            assert b'app_info{version="1.0.0"} 1' in response.data
