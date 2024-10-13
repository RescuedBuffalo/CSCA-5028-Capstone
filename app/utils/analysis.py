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

    # Calculate summary stats based on career
    games_played = career_stats["gamesPlayed"] # this will be our often used denominator
    if games_played > 0:
        points_per_game = career_stats["points"] / games_played
        goals_per_game = career_stats["goals"] / games_played
        avg_toi = career_stats["avgToi"]
        shooting_pct = career_stats["shootingPctg"]
    else:
        points_per_game = 0
        goals_per_game = 0
        avg_toi = 0
        shooting_pct = 0

    # Add these summary stats to the career stats dictionary
    career_stats["points_per_game"] = points_per_game
    career_stats["goals_per_game"] = goals_per_game

    # Extract last 5 games
    last_5_games = player_data.get("last5Games", [])

    # Create a dictionary to hold all this information for easy rendering
    return {
        "player_info": player_info,
        "career_stats": career_stats,
        "last_5_games": last_5_games
    }