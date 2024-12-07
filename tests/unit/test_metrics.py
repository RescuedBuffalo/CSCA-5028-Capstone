"""
Unit tests for the `/metrics` endpoint.

This file:
- Verifies that the `/metrics` endpoint correctly exposes Prometheus metrics.
- Ensures the proper HTTP response status, content type, and data format.
- Mocks Prometheus's `generate_latest` function to simulate metrics output.

Dependencies:
- `pytest` for managing test cases and fixtures.
- `unittest.mock` for mocking external dependencies.
- Flask app for endpoint testing.

Fixtures:
- `app`: Creates a Flask app instance in a testing configuration.
- `client`: Provides a test client for simulating HTTP requests.

Test Cases:
- `test_metrics_endpoint`: Verifies that the `/metrics` endpoint returns the correct HTTP status, content type, and metrics data.
"""

import pytest
from unittest.mock import patch
from app import create_app

@pytest.fixture
def app():
    """
    Pytest fixture to create a Flask app instance in testing mode.

    This fixture:
    - Configures the Flask app with the 'testing' environment.
    - Yields the app context for use in test cases.

    Yields:
        Flask app instance configured for testing.
    """
    app = create_app('testing')
    app.testing = True
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    """
    Pytest fixture to provide a test client for the Flask app.

    This fixture:
    - Creates a test client from the Flask app instance.
    - Yields the test client for simulating HTTP requests.

    Args:
        app: The Flask app instance provided by the `app` fixture.

    Yields:
        Flask test client for HTTP request simulation.
    """
    with app.test_client() as client:
        yield client

def test_metrics_endpoint(client):
    """
    Test the `/metrics` endpoint.

    This test:
    - Mocks the `generate_latest` function from Prometheus's `exposition` module to simulate metrics output.
    - Sends a POST request to the `/metrics` endpoint using the test client.
    - Asserts that the response status code is 200 (OK).
    - Verifies the content type is `text/plain; version=0.0.4; charset=utf-8`.
    - Confirms the response data contains the mocked metrics output.

    Steps:
    1. Mock the `generate_latest` function to return a sample Prometheus metrics string.
    2. Send a POST request to the `/metrics` endpoint.
    3. Validate the HTTP response status, content type, and data.

    Expected Outcome:
    - The `/metrics` endpoint correctly exposes the mocked Prometheus metrics data.
    """
    with patch('prometheus_client.exposition.generate_latest') as mock_generate_latest:
        # Mocked Prometheus metrics output
        mock_generate_latest.return_value = b'# HELP app_info Application info\n# TYPE app_info gauge\napp_info{version="1.0.0"} 1\n'

        # Send a POST request to the /metrics endpoint
        response = client.post('/metrics')

        # Assertions
        assert response.status_code == 200, "Expected HTTP status code 200 for the /metrics endpoint."
        assert response.content_type == 'text/plain; version=0.0.4; charset=utf-8', "Unexpected content type for /metrics response."
        assert b'app_info{version="1.0.0"} 1' in response.data, "Expected metrics data not found in the /metrics response."