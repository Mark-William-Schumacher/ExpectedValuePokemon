import os
from time import sleep
import requests
from core_module.utils.util import debug_print

# Global constants
token = os.getenv("POKEDATA_IO_TOKEN")
BEARER_TOKEN = f"Bearer {token}"
DEV_URL = "https://www.pokedata.io"

# --- Proxy Configuration ---
PROXY_ENABLED = True
PROXY_USERNAME = os.getenv("PROXY_USERNAME", "td-customer-MomsVpn")
PROXY_PASSWORD = os.getenv("PROXY_PASSWORD", "Sharktale360")
PROXY_SERVER = os.getenv("PROXY_SERVER", "398vripy.pr.thordata.net:9999")

# If this flag is True, all subsequent requests will use the proxy.
USE_PROXY_GLOBALLY = False


def _get_proxies():
    """Helper function to construct the proxies dictionary."""
    if PROXY_ENABLED and PROXY_USERNAME and PROXY_PASSWORD and PROXY_SERVER:
        proxy_url = f"https://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_SERVER}"
        print(f"Using proxy: {PROXY_SERVER}")
        return {"https": proxy_url, "http": proxy_url}

    print("Proxy use requested, but credentials are not fully configured.")
    return None


def make_get_request(endpoint, params=None):
    """
    Handles all shared GET request logic with automatic proxy failover.

    It will attempt a request, and if it fails with a rate-limit error (403, 429),
    it will retry once using a proxy. If the proxy retry succeeds, all subsequent
    requests in the session will automatically use the proxy.
    """
    global USE_PROXY_GLOBALLY
    url = f"{DEV_URL}{endpoint}"
    headers = {
        'Authorization': BEARER_TOKEN
    }

    # The request will be attempted up to two times.
    # 1st attempt: Normal request (or with proxy if globally enabled).
    # 2nd attempt: Retry with proxy if the first one was blocked.
    for attempt in range(2):
        is_retry_attempt = attempt > 0
        should_use_proxy = USE_PROXY_GLOBALLY or is_retry_attempt

        proxies = None
        if should_use_proxy:
            proxies = _get_proxies()

        try:
            sleep(2)  # To avoid overwhelming the API
            response = requests.get(url, headers=headers, params=params, proxies=proxies)
            debug_print(f"Request sent to: {response.request.url} (Proxy: {bool(proxies)})")

            # --- Handle Response ---

            # 1. Success
            if response.status_code == 200:
                print(f"Request successful: {response.status_code}")
                # If a retry with proxy was successful, enable it globally.
                if is_retry_attempt:
                    print("Proxy retry successful. Activating proxy for all future requests.")
                    USE_PROXY_GLOBALLY = True
                return response.json()

            # 2. Rate-limit / block error -> triggers a retry
            if response.status_code in [403, 429, 500]:
                print(f"Request failed with status {response.status_code}. Retrying with proxy...")
                continue  # Go to the next attempt in the loop

            # 3. Other HTTP error (not retryable) -> fail fast
            else:
                print(f"Request failed with non-retryable status code {response.status_code}: {response.reason}")
                print(f"Response text: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            # Catch network/connection errors and fail fast
            print(f"A network error occurred: {e}")
            return None

    # If the loop finishes, it means all attempts failed.
    print("Request failed on all attempts.")
    return None


# API-specific functions
def get_account_info():
    return make_get_request("/v0/account")


def get_all_pokemon_sets():
    return make_get_request("/v0/sets", params={"language": "ENGLISH"})


def get_all_cards_in_set(set_id):
    return make_get_request(f"/v0/set", params={"set_id": set_id, "stats": "kwan"})


def get_card_prices_of_set(set_id=None):
    return make_get_request("/api/cards", params={"set_id": set_id, "stats": "kwan"})


def get_card_id_psa_pop(set_id=None):
    return make_get_request("/api/cards/pops", params={"id": set_id})


def get_volume_of_transactions(card_id):
    return make_get_request("/api/transactions", params={"card_id": card_id, "page": 0})


# Debugging/testing function outputs
if __name__ == '__main__':
    # Just an example for debugging responses
    # debug_print(get_card_id_psa_pop(71601))
    # debug_print(get_card_prices_of_set(555))
    debug_print(get_volume_of_transactions(71601))
