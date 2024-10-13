import polars as pl

def analyze_player_performance(player_data):
    # Extract basic info
    player_info = {
        "first_name": player_data["firstName"]["default"],
        "last_name": player_data["lastName"]["default"],
        "team_name": player_data["fullTeamName"]["default"],
        "position": player_data["position"],
        "jersey_number": player_data["sweaterNumber"],
        "headshot": player_data["headshot"],
        "hero_image": player_data["heroImage"],
        "birth_date": player_data["birthDate"],
        "birth_city": player_data["birthCity"]["default"],
        "birth_province": player_data.get("birthStateProvince", {}).get("default", ""),
        "birth_country": player_data["birthCountry"],
        "height_in_inches": player_data["heightInInches"],
        "weight_in_pounds": player_data["weightInPounds"],
    }

    # Extract career regular season stats
    career_stats = player_data["careerTotals"]["regularSeason"]

    # Extract last 5 games
    last_5_games = player_data["last5Games"]

    # Create a dictionary to hold all this information for easy rendering
    return {
        "player_info": player_info,
        "career_stats": career_stats,
        "last_5_games": last_5_games
    }