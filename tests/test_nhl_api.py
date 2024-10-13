import pytest
from app.utils.nhl_api import get_nhl_player_stats
import requests
from unittest.mock import patch

# Sample mock response data from the NHL API
mock_api_response = {
    "people": [{
        "id": 8478402,
        "fullName": "Connor McDavid",
        "currentTeam": {"id": 22, "name": "Edmonton Oilers"},
        "primaryPosition": {"name": "Center"},
        # ... other fields as needed for testing
    }]
}

@patch('app.utils.nhl_api.requests.get')
def test_get_nhl_player_stats(mock_get):
    # Set up the mock to return the sample response with status 200
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_api_response

    # Call the function with a sample player ID
    result = get_nhl_player_stats(8478402)

    # Assert the result matches the mock data
    assert result["people"][0]["fullName"] == "Connor McDavid"
    assert result["people"][0]["currentTeam"]["name"] == "Edmonton Oilers"
    assert result["people"][0]["primaryPosition"]["name"] == "Center"

@patch('app.utils.nhl_api.requests.get')
def test_get_nhl_player_stats_api_error(mock_get):
    # Simulate a failed API call (e.g., 404 Not Found)
    mock_get.return_value.status_code = 404

    # Call the function with a sample player ID
    result = get_nhl_player_stats(8478402)

    # Test that it returns None or raises the expected error
    assert result is None