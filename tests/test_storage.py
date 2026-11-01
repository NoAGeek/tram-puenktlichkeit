"""Tests für Mo: storage. Datenbank nur im Arbeitsspeicher (":memory:")."""

from conftest import make_departure, t
from tramcheck import models, storage


def test_connect_creates_all_tables():
    conn = storage.connect(":memory:")
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    assert {row[0] for row in rows} == {"polls", "observations", "trips"}


def test_datetime_text_roundtrip():
    original = t(13, 53, 30)
    assert storage.from_text(storage.to_text(original)) == original
    assert storage.from_text(storage.to_text(None)) is None


# --- Tests für die umgesetzten Funktionen -----------------------------


def test_save_and_load_observations_roundtrip():
    conn = storage.connect(":memory:")
    dep = make_departure(fetched_at=t(13, 45), time_planned=t(13, 53, 30), time_real=None)

    storage.save_poll(conn, t(13, 45), True, [dep])

    assert storage.load_observations(conn) == [dep]


def test_failed_poll_is_saved_but_not_counted_as_successful():
    conn = storage.connect(":memory:")
    storage.save_poll(conn, t(13, 45), True, [])
    storage.save_poll(conn, t(13, 46), False, [], "Timeout")

    assert storage.load_successful_poll_times(conn) == [t(13, 45)]


def test_save_and_load_trips_roundtrip():
    conn = storage.connect(":memory:")
    trip = models.Trip(
        line="2", stop_id=322, direction="R", time_planned=t(14, 0),
        final_time_real=t(14, 4), delay_seconds=240, status=models.STATUS_OK, observation_count=3,
    )

    storage.replace_trips(conn, [trip])
    storage.replace_trips(conn, [trip])  # zweimal: darf keine Duplikate geben

    assert storage.load_trips(conn) == [trip]
