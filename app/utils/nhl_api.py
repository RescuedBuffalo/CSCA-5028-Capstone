import requests

def get_nhl_player_stats(player_id):
    url = f'https://api-web.nhle.com/v1/player/{player_id}/landing'
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else: 
        return '404'
    
def get_nhl_teams():
    url = 'https://api.nhle.com/stats/rest/en/team'
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        return '404'
    
def get_nhl_team_roster_by_season(team, season):
    url = f'https://api-web.nhle.com/v1/roster/{team}/{season}'

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        return '404'