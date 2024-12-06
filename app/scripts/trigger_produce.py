import os
import requests

def main():
    base_url = os.getenv('APP_BASE_URL')  # Your app's base URL
    endpoint = "/produce_tasks"

    try:
        response = requests.get(f"{base_url}{endpoint}")
        if response.status_code == 200:
            print("Successfully triggered produce_tasks.")
        else:
            print(f"Failed to trigger produce_tasks. Status code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error while hitting the endpoint: {e}")

if __name__ == "__main__":
    main()