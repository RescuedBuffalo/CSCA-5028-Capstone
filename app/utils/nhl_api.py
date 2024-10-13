import requests

def get_nhl_player_stats(player_id):
    url = f'https://api-web.nhle.com/v1/player/{player_id}/landing'
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else: 
        return None