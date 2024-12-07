"""
Unit tests for NHL API utility functions.

This file:
- Tests the `get_nhl_player_stats` function to ensure it interacts correctly with the NHL API.
- Uses `unittest.mock.patch` to mock API requests and simulate different responses.

Dependencies:
- `pytest` for managing test cases.
- `unittest.mock` for mocking HTTP requests.
- `requests` for simulating API behavior.

Test Cases:
- `test_get_nhl_player_stats`: Verifies that player stats are correctly fetched and parsed from the API.
- `test_get_nhl_player_stats_api_error`: Ensures proper handling of API errors (e.g., 404 responses).
"""

import pytest
from app.utils.nhl_api import get_nhl_player_stats
import requests
from unittest.mock import patch

# Mock response data simulating the NHL API's response structure
mock_api_response = {
    "people": [{
        "id": 8478402,
        "fullName": "Connor McDavid",
        "currentTeam": {"id": 22, "name": "Edmonton Oilers"},
        "primaryPosition": {"name": "Center"},
        # Add other fields as necessary for testing
    }]
}


@patch('app.utils.nhl_api.requests.get')
def test_get_nhl_player_stats(mock_get):
    """
    Test the `get_nhl_player_stats` function for successful API interaction.

    Steps:
    1. Mock the `requests.get` method to return a successful (200) response with sample data.
    2. Call `get_nhl_player_stats` with a valid `player_id`.
    3. Assert that the returned data matches the mocked API response.

    Expected Outcome:
    - The function returns a dictionary containing the player's stats as provided by the mock response.
    """
    # Set up the mock to return the sample response with status 200
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_api_response

    # Call the function
    result = get_nhl_player_stats(8478402)

    # Assert the result matches the mock data
    assert result["people"][0]["fullName"] == "Connor McDavid"
    assert result["people"][0]["currentTeam"]["name"] == "Edmonton Oilers"
    assert result["people"][0]["primaryPosition"]["name"] == "Center"


@patch('app.utils.nhl_api.requests.get')
def test_get_nhl_player_stats_api_error(mock_get):
    """
    Test the `get_nhl_player_stats` function for API error handling.

    Steps:
    1. Mock the `requests.get` method to simulate a 404 error.
    2. Call `get_nhl_player_stats` with an invalid `player_id`.
    3. Assert that the function returns the string '404', indicating an API error.

    Expected Outcome:
    - The function correctly handles the error and returns '404' as the error code.
    """
    # Set up the mock to return a 404 status code
    mock_get.return_value.status_code = 404

    # Call the function
    result = get_nhl_player_stats(99)

    # Assert that the function handles the 404 error correctly
    assert result == '404'