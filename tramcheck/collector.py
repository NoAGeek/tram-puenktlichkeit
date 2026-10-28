"""Die Sammelschleife: fragt die API regelmäßig ab und speichert.  [Person A]

Hier treffen die beiden Hälften zusammen:
api_client -> parser -> storage.save_poll
"""

import logging
import sqlite3
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from tramcheck.config import Config

logger = logging.getLogger(__name__)


def setup_logging(log_path: Path) -> None:
    """Loggt gleichzeitig in die Konsole und in eine Datei.

    Die Logdatei wird bei 5 MB gewechselt (max. 5 alte Dateien),
    damit sie bei wochenlangem Betrieb nicht unendlich wächst.
    """
    log_path.parent.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

    file_handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(file_handler)
    root.addHandler(console_handler)


def now() -> datetime:
    """Aktuelle Zeit mit lokaler Zeitzone (in Tests leicht zu ersetzen)."""
    return datetime.now().astimezone()


def poll_once(config: Config, conn: sqlite3.Connection) -> int:
    """Führt genau EINE Abfrage durch und speichert das Ergebnis.

    Auch eine fehlgeschlagene Abfrage wird gespeichert (``success=False``),
    damit wir später Datenlücken erkennen.

    Returns:
        Anzahl der gespeicherten Abfahrten (0 bei Fehler).

    TODO (Person A):
        1. ``fetched_at = now()``
        2. ``data = api_client.fetch_monitor(...)``
        3. Wenn ``not api_client.is_valid_response(data)``:
           ``storage.save_poll(conn, fetched_at, False, [], "...")`` und 0 zurückgeben
        4. Sonst ``parser.parse_monitor(...)``, dann
           ``storage.save_poll(conn, fetched_at, True, departures)``
        5. Anzahl der Abfahrten zurückgeben und mit ``logger.info`` loggen
    """
    raise NotImplementedError("TODO Person A: poll_once")


def run_forever(config: Config) -> None:
    """Ruft ``poll_once`` endlos im Abstand ``config.poll_interval_seconds`` auf.

    Beenden mit Strg+C.

    TODO (Person A):
        - Datenbank öffnen: ``conn = storage.connect(config.database_path)``
        - ``while True:``-Schleife
        - Jeden Durchlauf in ``try: ... except Exception: logger.exception(...)``
          packen: ein unerwarteter Fehler darf die Schleife NICHT beenden
        - ``KeyboardInterrupt`` (Strg+C) NICHT abfangen, damit man beenden kann
        - ``time.sleep(config.poll_interval_seconds)``
    """
    raise NotImplementedError("TODO Person A: run_forever")
