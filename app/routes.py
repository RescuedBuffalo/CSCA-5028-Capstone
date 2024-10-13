from flask import render_template, request
from app import app
from app.utils.nhl_api import get_nhl_player_stats

# Route to display a basic form
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        player_id = request.form['player_id']
        # Fetch player data with API
        player_data = get_nhl_player_stats(player_id)
        if player_data:
            return render_template('report.html', player_id=player_id, player_data=player_data)
        else:
            error_message = 'Could not fetch data with player ID: {player_id}'
            return render_template('index.html', error_message=error_message)
        
    return render_template('index.html')
