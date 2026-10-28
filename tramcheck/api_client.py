"""HTTP-Abruf vom Echtzeit-Monitor der Wiener Linien.  [Omar]

Wichtigste Regel: Dieses Modul wirft NIE eine Exception nach außen.
Bei jedem Problem wird geloggt und ``None`` zurückgegeben, damit das
Sammeln über Tage und Wochen weiterläuft.
"""

import logging

import requests

logger = logging.getLogger(__name__)


def fetch_monitor(api_url: str, stop_ids: list[int], timeout: int) -> dict | None:
    """Fragt den Monitor für mehrere stopIds in EINER Anfrage ab.

    Die API akzeptiert ``?stopId=322&stopId=319&stopId=350``.
    ``requests`` baut das automatisch, wenn man eine Liste übergibt:
    ``params={"stopId": stop_ids}``.

    Args:
        api_url: Basis-URL aus der Config.
        stop_ids: Liste der stopIds, z. B. ``[319, 322, 350]``.
        timeout: maximale Wartezeit in Sekunden.

    Returns:
        Das JSON als Python-``dict``, oder ``None`` bei einem Fehler.

    TODO (Omar):
        1. ``requests.get(...)`` mit ``params`` und ``timeout`` aufrufen
        2. ``response.raise_for_status()``: wirft Fehler bei HTTP 4xx/5xx
        3. ``response.json()`` zurückgeben
        4. Diese Fehler einzeln abfangen, mit ``logger.warning(...)`` loggen
           und ``None`` zurückgeben:
           ``requests.Timeout``, ``requests.ConnectionError``,
           ``requests.RequestException`` (alles andere von requests),
           ``ValueError`` (Antwort war kein gültiges JSON)
    """
    raise NotImplementedError("TODO Omar: fetch_monitor")


def is_valid_response(data: dict | None) -> bool:
    """Prüft, ob eine API-Antwort brauchbare Daten enthält.

    Achtung: Die API antwortet auch bei einer falschen stopId mit
    ``message.value == "OK"``, nur ist ``data.monitors`` dann eine leere Liste.

    Args:
        data: Rückgabe von ``fetch_monitor``.

    Returns:
        ``True`` nur wenn ``data`` nicht ``None`` ist, ``message.value``
        gleich ``"OK"`` ist und ``data.monitors`` nicht leer ist.

    TODO (Omar): umsetzen. Tipp: ``data.get("data", {}).get("monitors", [])``
        stürzt nicht ab, wenn ein Schlüssel fehlt.
    """
    raise NotImplementedError("TODO Omar: is_valid_response")
