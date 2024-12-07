"""
Unit test for the `/health` endpoint.

This file:
- Verifies that the `/health` endpoint returns the correct HTTP status code and response data.
- Ensures the endpoint functions as expected in a testing environment.

Dependencies:
- `pytest` for managing test cases and fixtures.
- Flask app for endpoint testing.

Fixtures:
- `client`: Provides a test client for simulating HTTP requests.

Test Cases:
- `test_health_endpoint`: Verifies that the `/health` endpoint returns a 200 status code and the expected response body.
"""

import pytest
from app import create_app


@pytest.fixture
def client():
    """
    Pytest fixture to provide a test client for the Flask app.

    This fixture:
    - Creates a Flask app instance configured for testing.
    - Provides a test client for simulating HTTP requests.

    Yields:
        Flask test client for HTTP request simulation.
    """
    app = create_app('testing')
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """
    Test the `/health` endpoint.

    This test:
    - Sends a POST request to the `/health` endpoint using the test client.
    - Asserts that the HTTP response status code is 200 (OK).
    - Verifies that the response body contains the string "ok".

    Steps:
    1. Use the test client to send a POST request to `/health`.
    2. Validate the HTTP response status code.
    3. Check that the response body matches the expected string.

    Expected Outcome:
    - The `/health` endpoint responds with a 200 status code and the string "ok".
    """
    # Send a POST request to the /health endpoint
    response = client.post('/health')

    # Assertions
    assert response.status_code == 200, "Expected HTTP status code 200 for the /health endpoint."
    assert response.data == b"ok", "Expected response body to be 'ok'."