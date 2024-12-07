import concurrent.futures
import time
import requests
import pytest
import os
from dotenv import load_dotenv


# Constants
load_dotenv()
BASE_URL = os.getenv("APP_BASE_URL")
NUM_USERS = 100  # Number of concurrent users
ALLOWED_FAILURES = 1  # Maximum allowed failures
MAX_AVERAGE_RESPONSE_TIME = 4  # Max average response time (in seconds)


def make_request(endpoint):
    """
    Makes a GET request to the specified endpoint and returns status code and response time.
    """
    try:
        start_time = time.time()
        response = requests.get(f"{BASE_URL}{endpoint}")
        response_time = time.time() - start_time
        return response.status_code, response_time
    except Exception:
        return None, None


@pytest.mark.integration
def test_concurrent_users():
    """
    Tests if the app can handle 100 concurrent users.
    Verifies:
      - Average response times are under 4 seconds.
      - No more than 1 failure.
    """
    endpoints = ["/", "/team/16", "/player/8482700"]
    results = []

    # Simulate concurrent users
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_USERS) as executor:
        future_to_request = {
            executor.submit(make_request, endpoint): endpoint
            for endpoint in endpoints * (NUM_USERS // len(endpoints))
        }

        for future in concurrent.futures.as_completed(future_to_request):
            try:
                result = future.result()
                results.append(result)
            except Exception:
                results.append((None, None))

    success_count = sum(1 for status, _ in results if status == 200)
    failure_count = sum(1 for status, _ in results if status != 200 or status is None)

    response_times_by_endpoint = {endpoint: [] for endpoint in endpoints}
    for i, (_, response_time) in enumerate(results):
        if response_time is not None:
            endpoint = endpoints[i % len(endpoints)]
            response_times_by_endpoint[endpoint].append(response_time)

    average_response_times = {
        endpoint: sum(times) / len(times) if times else float('inf')
        for endpoint, times in response_times_by_endpoint.items()
    }

    # Assertions
    assert failure_count <= ALLOWED_FAILURES, f"Too many failures: {failure_count} failures"
    for endpoint, avg_time in average_response_times.items():
        assert avg_time <= MAX_AVERAGE_RESPONSE_TIME, f"Average response time for {endpoint} exceeded: {avg_time:.2f}s"