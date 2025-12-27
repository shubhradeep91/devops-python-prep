import time
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

def check_service_health(url: str, retries: int, delay: int) -> bool:

    for attempt in range(1, retries+1):
        try:
            print(f"Attempt {attempt} to check service health")

            with urlopen(url, timeout =5) as response:
                if response.status == 200:
                    print("Service is HEALTHY")
                    return True
                else:
                    print(f"Non-200 status code: {response.status}")

        except HTTPError as e:
            print(f"HTTP Error on attempt {attempt}: {e.code}")

        except URLError as e:
            print(f"Network Error on attempt {attempt}: {e.reason}")
        
        except Exception as e:
            print(f"Unexpected Error on attempt {attempt}: {e}")

        if attempt < retries:
            time.sleep(delay)

    print("Service is unhealthy after all retries")
    return False