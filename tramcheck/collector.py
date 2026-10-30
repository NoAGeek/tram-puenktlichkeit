"""Die Sammelschleife: fragt die API regelmäßig ab und speichert.  [Omar]

Hier treffen die beiden Hälften zusammen:
api_client -> parser -> storage.save_poll
"""

import logging
import sqlite3
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from tramcheck import api_client, parser, storage
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
    """
    fetched_at = now()
    data = api_client.fetch_monitor(config.api_url, config.stop_ids(), config.request_timeout_seconds)

    if not api_client.is_valid_response(data):
        storage.save_poll(conn, fetched_at, False, [], "Keine gültige Antwort von der API")
        logger.warning("Abfrage fehlgeschlagen, als Lücke gespeichert")
        return 0

    departures = parser.parse_monitor(data, config.lines, fetched_at)
    storage.save_poll(conn, fetched_at, True, departures)
    logger.info("%d Abfahrten gespeichert", len(departures))
    return len(departures)


def run_forever(config: Config) -> None:
    """Ruft ``poll_once`` endlos im Abstand ``config.poll_interval_seconds`` auf.

    Ein unerwarteter Fehler wird geloggt, beendet die Schleife aber nicht.
    Beenden mit Strg+C (``KeyboardInterrupt`` wird absichtlich nicht abgefangen).
    """
    conn = storage.connect(config.database_path)
    logger.info("Sammeln gestartet, Abfrage alle %d s", config.poll_interval_seconds)

    while True:
        try:
            poll_once(config, conn)
        except Exception:
            logger.exception("Unerwarteter Fehler bei der Abfrage, mache weiter")
        time.sleep(config.poll_interval_seconds)
