"""Speicherung in SQLite.  [Mo]

Das einzige Modul mit SQL. Alle anderen Module arbeiten nur mit
``Departure``- und ``Trip``-Objekten.

Tabellen:
    polls         jede API-Abfrage (auch fehlgeschlagene)
    observations  Rohdaten: jede gesehene Abfahrt pro Abfrage (nur anhängen!)
    trips         berechnet: darf jederzeit gelöscht und neu gebaut werden

Zeiten speichern wir als ISO-Text mit Zeitzone, z. B.
``"2026-10-28T13:53:30+01:00"``. SQLite hat keinen eigenen Datums-Typ.
"""

import sqlite3
from datetime import datetime
from pathlib import Path

from tramcheck.models import Departure, Trip

SCHEMA = """
CREATE TABLE IF NOT EXISTS polls (
    id            INTEGER PRIMARY KEY,
    fetched_at    TEXT NOT NULL,
    success       INTEGER NOT NULL,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS observations (
    id                 INTEGER PRIMARY KEY,
    poll_id            INTEGER NOT NULL REFERENCES polls(id),
    line               TEXT NOT NULL,
    stop_id            INTEGER NOT NULL,
    direction          TEXT NOT NULL,
    towards            TEXT,
    time_planned       TEXT NOT NULL,
    time_real          TEXT,
    realtime_supported INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_observations_trip
    ON observations (line, stop_id, direction, time_planned);

CREATE TABLE IF NOT EXISTS trips (
    line              TEXT NOT NULL,
    stop_id           INTEGER NOT NULL,
    direction         TEXT NOT NULL,
    time_planned      TEXT NOT NULL,
    final_time_real   TEXT,
    delay_seconds     INTEGER,
    status            TEXT NOT NULL,
    observation_count INTEGER NOT NULL,
    PRIMARY KEY (line, stop_id, direction, time_planned)
);
"""


def connect(database_path: str | Path) -> sqlite3.Connection:
    """Öffnet (oder erstellt) die Datenbank und legt fehlende Tabellen an.

    Args:
        database_path: Pfad zur .db-Datei, oder ``":memory:"`` für Tests
            (Datenbank nur im Arbeitsspeicher, nach dem Test weg).
    """
    if str(database_path) != ":memory:":
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(database_path)
    conn.executescript(SCHEMA)
    return conn


def to_text(value: datetime | None) -> str | None:
    """datetime -> ISO-Text für die Datenbank (``None`` bleibt ``None``)."""
    return value.isoformat() if value is not None else None


def from_text(value: str | None) -> datetime | None:
    """ISO-Text aus der Datenbank -> datetime (``None`` bleibt ``None``)."""
    return datetime.fromisoformat(value) if value is not None else None


def save_poll(
    conn: sqlite3.Connection,
    fetched_at: datetime,
    success: bool,
    departures: list[Departure],
    error_message: str | None = None,
) -> int:
    """Speichert eine Abfrage und alle darin gesehenen Abfahrten.

    Returns:
        Die ``id`` der neuen Zeile in ``polls``.

    TODO (Mo):
        1. ``INSERT INTO polls ...``, die neue id steht danach in
           ``cursor.lastrowid``
        2. Für jede Departure ``INSERT INTO observations ...`` mit dieser poll_id
           (Tipp: ``conn.executemany`` für viele Zeilen auf einmal)
        3. Immer ``?``-Platzhalter verwenden, nie f-Strings im SQL!
        4. ``conn.commit()`` am Ende
    """
    raise NotImplementedError("TODO Mo: save_poll")


def load_successful_poll_times(conn: sqlite3.Connection) -> list[datetime]:
    """Alle Zeitpunkte erfolgreicher Abfragen, aufsteigend sortiert.

    Wird von ``trips.build_trips`` gebraucht, um Datenlücken zu erkennen.

    TODO (Mo): ``SELECT fetched_at FROM polls WHERE success = 1 ORDER BY fetched_at``
    """
    raise NotImplementedError("TODO Mo: load_successful_poll_times")


def load_observations(conn: sqlite3.Connection) -> list[Departure]:
    """Liest alle Beobachtungen wieder als ``Departure``-Objekte.

    ``fetched_at`` kommt aus der Tabelle ``polls`` (JOIN über ``poll_id``).

    TODO (Mo): SELECT mit JOIN, jede Zeile in ein ``Departure`` umbauen
        (Zeiten mit ``from_text``, ``realtime_supported`` mit ``bool(...)``).
    """
    raise NotImplementedError("TODO Mo: load_observations")


def replace_trips(conn: sqlite3.Connection, trips: list[Trip]) -> None:
    """Löscht alle alten Fahrten und speichert die neu berechneten.

    TODO (Mo): ``DELETE FROM trips``, dann alle ``trips`` einfügen,
        dann ``conn.commit()``.
    """
    raise NotImplementedError("TODO Mo: replace_trips")


def load_trips(conn: sqlite3.Connection) -> list[Trip]:
    """Liest alle berechneten Fahrten als ``Trip``-Objekte.

    TODO (Mo): umsetzen, analog zu ``load_observations``.
    """
    raise NotImplementedError("TODO Mo: load_trips")
