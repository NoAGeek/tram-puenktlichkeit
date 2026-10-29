
"""HTTP-Abruf vom Echtzeit-Monitor der Wiener Linien. [Omar]

Bei Problemen wird eine Warnung geloggt und None zurückgegeben,
damit das Sammeln der Daten weiterlaufen kann.
"""

import logging

import requests

logger = logging.getLogger(__name__)


def fetch_monitor(api_url: str, stop_ids: list[int], timeout: int) -> dict | None:
    """Ruft Echtzeitdaten für mehrere Haltestellen von der API ab."""

    try:
        response = requests.get(
            api_url,
            params={"stopId": stop_ids},
            timeout=timeout
        )

        response.raise_for_status()

        return response.json()

    except requests.Timeout:
        logger.warning("API request timed out")
        return None

    except requests.ConnectionError:
        logger.warning("Could not connect to the API")
        return None

    except requests.RequestException as error:
        logger.warning("API request failed: %s", error)
        return None

    except ValueError:
        logger.warning("API returned invalid JSON")
        return None


def is_valid_response(data: dict | None) -> bool:
    """Prüft, ob die API-Antwort gültige Monitordaten enthält."""

    if not isinstance(data, dict):
        return False

    message = data.get("message")
    if not isinstance(message, dict):
        return False

    if message.get("value") != "OK":
        return False

    content = data.get("data")
    if not isinstance(content, dict):
        return False

    monitors = content.get("monitors", [])

    if not isinstance(monitors, list) or len(monitors) == 0:
        return False

    return True
