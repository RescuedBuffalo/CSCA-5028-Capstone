import requests

def get_nhl_player_stats(player_id):
    url = f'https://statsapi.web.nhl.com/api/v1/people/{player_id}/stats?stats=yearByYear'
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else: 
        return None