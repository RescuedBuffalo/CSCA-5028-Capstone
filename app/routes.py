from flask import Flask, render_template, request
from app import app

# Route to display a basic form
@app.route('/', method=['GET', 'POST'])
def index():
    if request.method == 'POST':
        player_id = request.form['player_id']
        return render_template('report.html', player_id=player_id)
    return render_template('index.html')
