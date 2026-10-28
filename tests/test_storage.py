"""Tests für Omar: storage. Datenbank nur im Arbeitsspeicher (":memory:")."""

from conftest import make_departure, t, todo
from tramcheck import storage


def test_connect_creates_all_tables():
    conn = storage.connect(":memory:")
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    assert {row[0] for row in rows} == {"polls", "observations", "trips"}


def test_datetime_text_roundtrip():
    original = t(13, 53, 30)
    assert storage.from_text(storage.to_text(original)) == original
    assert storage.from_text(storage.to_text(None)) is None


# --- Tests für TODO-Funktionen: @todo löschen, sobald umgesetzt -----------


@todo
def test_save_and_load_observations_roundtrip():
    conn = storage.connect(":memory:")
    dep = make_departure(fetched_at=t(13, 45), time_planned=t(13, 53, 30), time_real=None)

    storage.save_poll(conn, t(13, 45), True, [dep])

    assert storage.load_observations(conn) == [dep]


@todo
def test_failed_poll_is_saved_but_not_counted_as_successful():
    conn = storage.connect(":memory:")
    storage.save_poll(conn, t(13, 45), True, [])
    storage.save_poll(conn, t(13, 46), False, [], "Timeout")

    assert storage.load_successful_poll_times(conn) == [t(13, 45)]
