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