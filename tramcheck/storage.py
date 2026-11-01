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
    """
    cursor = conn.execute(
        "INSERT INTO polls (fetched_at, success, error_message) VALUES (?, ?, ?)",
        (to_text(fetched_at), int(success), error_message),
    )
    poll_id = cursor.lastrowid

    conn.executemany(
        """INSERT INTO observations
           (poll_id, line, stop_id, direction, towards, time_planned, time_real, realtime_supported)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        [
            (
                poll_id,
                d.line,
                d.stop_id,
                d.direction,
                d.towards,
                to_text(d.time_planned),
                to_text(d.time_real),
                int(d.realtime_supported),
            )
            for d in departures
        ],
    )
    conn.commit()
    return poll_id


def load_successful_poll_times(conn: sqlite3.Connection) -> list[datetime]:
    """Alle Zeitpunkte erfolgreicher Abfragen, aufsteigend sortiert.

    Wird von ``trips.build_trips`` gebraucht, um Datenlücken zu erkennen.
    """
    rows = conn.execute("SELECT fetched_at FROM polls WHERE success = 1").fetchall()
    return sorted(from_text(row[0]) for row in rows)


def load_observations(conn: sqlite3.Connection) -> list[Departure]:
    """Liest alle Beobachtungen wieder als ``Departure``-Objekte.

    ``fetched_at`` kommt aus der Tabelle ``polls`` (JOIN über ``poll_id``).
    """
    rows = conn.execute(
        """SELECT p.fetched_at, o.line, o.stop_id, o.direction, o.towards,
                  o.time_planned, o.time_real, o.realtime_supported
           FROM observations o JOIN polls p ON p.id = o.poll_id
           ORDER BY o.id"""
    ).fetchall()
    return [
        Departure(
            fetched_at=from_text(fetched_at),
            line=line,
            stop_id=stop_id,
            direction=direction,
            towards=towards,
            time_planned=from_text(time_planned),
            time_real=from_text(time_real),
            realtime_supported=bool(realtime_supported),
        )
        for fetched_at, line, stop_id, direction, towards, time_planned, time_real, realtime_supported in rows
    ]


def replace_trips(conn: sqlite3.Connection, trips: list[Trip]) -> None:
    """Löscht alle alten Fahrten und speichert die neu berechneten."""
    conn.execute("DELETE FROM trips")
    conn.executemany(
        """INSERT INTO trips
           (line, stop_id, direction, time_planned, final_time_real,
            delay_seconds, status, observation_count)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        [
            (
                trip.line,
                trip.stop_id,
                trip.direction,
                to_text(trip.time_planned),
                to_text(trip.final_time_real),
                trip.delay_seconds,
                trip.status,
                trip.observation_count,
            )
            for trip in trips
        ],
    )
    conn.commit()


def load_trips(conn: sqlite3.Connection) -> list[Trip]:
    """Liest alle berechneten Fahrten als ``Trip``-Objekte."""
    rows = conn.execute(
        """SELECT line, stop_id, direction, time_planned, final_time_real,
                  delay_seconds, status, observation_count
           FROM trips ORDER BY time_planned, line"""
    ).fetchall()
    return [
        Trip(
            line=line,
            stop_id=stop_id,
            direction=direction,
            time_planned=from_text(time_planned),
            final_time_real=from_text(final_time_real),
            delay_seconds=delay_seconds,
            status=status,
            observation_count=observation_count,
        )
        for line, stop_id, direction, time_planned, final_time_real, delay_seconds, status, observation_count in rows
    ]
