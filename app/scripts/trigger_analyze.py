import os
import requests

def main():
    base_url = os.getenv('APP_BASE_URL')  # Your app's base URL
    endpoint = "/analyze/players"

    try:
        response = requests.post(f"{base_url}{endpoint}")
        if response.status_code == 200:
            print("Successfully triggered analyze_players.")
        else:
            print(f"Failed to trigger analyze_players. Status code: {response.status_code}")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"Error while hitting the endpoint: {e}")

if __name__ == "__main__":
    main()