from flask import render_template, request
from app import app
from app.utils.nhl_api import get_nhl_player_stats
from app.utils.analysis import analyze_player_performance

# Route to display a basic form
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        player_id = request.form['player_id']
        # Fetch player data with API
        player_data = get_nhl_player_stats(player_id)

        if player_data:
            analyzed_data = analyze_player_performance(player_data)
 
            return render_template(
                        'report.html',
                        player_info=analyzed_data["player_info"],
                        career_stats=analyzed_data["career_stats"],
                        last_5_games=analyzed_data["last_5_games"]
                    )
        else:
            error_message = 'Could not fetch data with player ID: {player_id}'
            return render_template('index.html', error_message=error_message)
        
    return render_template('index.html')
