import pytest
from app import create_app
import requests

@pytest.fixture
def client():
    app = create_app('testing')
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client

# Test the /health endpoint to ensure it returns a 200 status code
def test_health_endpoint(client):

    response = client.post('/health')
    
    assert response.status_code == 200
    assert response.data == b"ok"