"""
Unit tests for the `analyze_player_performance` function.

This file:
- Verifies that the `analyze_player_performance` function correctly processes player data.
- Tests both complete and incomplete input data for robustness.
- Uses sample data to simulate API responses.

Dependencies:
- `pytest` for managing test cases.
- `app.utils.analysis.analyze_player_performance` for the function under test.

Test Cases:
- `test_analyze_player_performance`: Ensures the function correctly parses and analyzes complete player data.
- `test_analyze_player_performance_missing_data`: Tests the function's behavior when input data is incomplete or missing.

Sample Data:
- `sample_player_data`: Mock data simulating a typical API response.
"""

import pytest
from app.utils.analysis import analyze_player_performance

# Sample data to mock an API response
sample_player_data = {
    "firstName": {"default": "Connor"},
    "lastName": {"default": "McDavid"},
    "fullTeamName": {"default": "Edmonton Oilers"},
    "position": "C",
    "sweaterNumber": 97,
    "headshot": "https://example.com/headshot.png",
    "heroImage": "https://example.com/hero.png",
    "birthDate": "1997-01-13",
    "birthCity": {"default": "Richmond Hill"},
    "birthStateProvince": {"default": "Ontario"},
    "birthCountry": "CAN",
    "heightInInches": 73,
    "weightInPounds": 194,
    "currentTeamId": 22,
    "careerTotals": {
        "regularSeason": {
            "gamesPlayed": 645,
            "goals": 335,
            "assists": 647,
            "points": 982,
            "shots": 2211,
            "powerPlayGoals": 78,
            "shootingPctg": 0.1515,
            "avgToi": "22:00",
        }
    },
    "last5Games": [
        {"gameDate": "2024-05-14", "goals": 0, "assists": 1, "points": 1, "shots": 4, "toi": "23:12"},
        {"gameDate": "2024-05-12", "goals": 0, "assists": 0, "points": 0, "shots": 4, "toi": "29:42"},
        {"gameDate": "2024-05-10", "goals": 1, "assists": 3, "points": 4, "shots": 5, "toi": "28:12"},
        {"gameDate": "2024-05-08", "goals": 0, "assists": 1, "points": 1, "shots": 0, "toi": "24:03"},
        {"gameDate": "2024-05-01", "goals": 0, "assists": 2, "points": 2, "shots": 4, "toi": "23:36"}
    ]
}


def test_analyze_player_performance():
    """
    Test the `analyze_player_performance` function with complete data.

    Steps:
    1. Pass `sample_player_data` (complete player data) to the function.
    2. Verify that the player's basic information is correctly extracted.
    3. Validate the calculations for career stats such as games played, points per game, and goals per game.
    4. Ensure the last 5 games data is parsed and matches the input.

    Expected Outcome:
    - Basic player information, career stats, and last 5 games data are accurately processed.
    """
    result = analyze_player_performance(sample_player_data)

    # Test basic player info extraction
    assert result["player_info"]["first_name"] == "Connor"
    assert result["player_info"]["last_name"] == "McDavid"
    assert result["player_info"]["team_name"] == "Edmonton Oilers"
    assert result["player_info"]["position"] == "C"

    # Test career stats calculations
    career_stats = result["career_stats"]
    assert career_stats["gamesPlayed"] == 645
    assert career_stats["points_per_game"] == pytest.approx(1.52, 0.01)  # Rounded value
    assert career_stats["goals_per_game"] == pytest.approx(0.52, 0.01)  # Rounded value

    # Test last 5 games data
    last_5_games = result["last_5_games"]
    assert len(last_5_games) == 5
    assert last_5_games[0]["goals"] == 0
    assert last_5_games[2]["goals"] == 1
    assert last_5_games[4]["assists"] == 2


def test_analyze_player_performance_missing_data():
    """
    Test the `analyze_player_performance` function with incomplete data.

    Steps:
    1. Modify `sample_player_data` to simulate missing data (e.g., remove `last5Games`).
    2. Pass the modified data to the function.
    3. Verify that basic player information is still correctly extracted.
    4. Ensure the missing data is handled gracefully (e.g., return an empty list for `last_5_games`).

    Expected Outcome:
    - Basic player information is extracted.
    - Missing data (e.g., last 5 games) does not cause errors, and the output correctly handles the absence of data.
    """
    # Remove some fields from the mock data to simulate missing data
    incomplete_data = sample_player_data.copy()
    del incomplete_data["last5Games"]  # Simulate missing last 5 games

    # Call the function with incomplete data
    result = analyze_player_performance(incomplete_data)

    # Ensure it still returns basic player info
    assert result["player_info"]["first_name"] == "Connor"

    # Test that last 5 games is empty or None
    assert "last_5_games" in result
    assert result["last_5_games"] == []