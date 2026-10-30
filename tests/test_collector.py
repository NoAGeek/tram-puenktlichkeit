"""Tests für collector und save_poll. Die echte API wird durch eine Fixture ersetzt."""

from conftest import load_fixture, make_departure, t
from tramcheck import api_client, collector, storage


def count_rows(conn, table):
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def test_poll_once_saves_departures(config, monkeypatch):
    data = load_fixture("monitor_multi_322_319_350.json")
    monkeypatch.setattr(api_client, "fetch_monitor", lambda *args: data)
    monkeypatch.setattr(collector, "now", lambda: t(13, 45, 27))
    conn = storage.connect(":memory:")

    count = collector.poll_once(config, conn)

    assert count == 36
    assert count_rows(conn, "observations") == 36
    assert conn.execute("SELECT fetched_at, success FROM polls").fetchall() == [
        ("2026-10-28T13:45:27+01:00", 1)
    ]


def test_poll_once_saves_failed_poll_as_gap(config, monkeypatch):
    monkeypatch.setattr(api_client, "fetch_monitor", lambda *args: None)
    conn = storage.connect(":memory:")

    assert collector.poll_once(config, conn) == 0
    assert conn.execute("SELECT success FROM polls").fetchall() == [(0,)]
    assert count_rows(conn, "observations") == 0


def test_save_poll_stores_missing_time_real_as_null():
    conn = storage.connect(":memory:")
    dep = make_departure(fetched_at=t(13, 45), time_planned=t(13, 53, 30), time_real=None)

    poll_id = storage.save_poll(conn, t(13, 45), True, [dep])

    row = conn.execute("SELECT poll_id, time_planned, time_real FROM observations").fetchone()
    assert row == (poll_id, "2026-10-28T13:53:30+01:00", None)
