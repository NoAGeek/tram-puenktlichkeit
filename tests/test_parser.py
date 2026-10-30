
"""Tests für Omar: api_client und parser. Rufen NIE die echte API auf."""

from datetime import timedelta

from conftest import load_fixture, t, todo
from tramcheck import api_client
from tramcheck.parser import parse_api_time, parse_monitor


# --- Sicherstellen, dass unsere Fixtures so aussehen wie erwartet ---------


def test_fixture_has_expected_structure():
    data = load_fixture("monitor_hoechstaedtplatz_322.json")
    line = data["data"]["monitors"][0]["lines"][0]
    departure = line["departures"]["departure"][0]

    assert "realtimeSupported" in line
    assert "timePlanned" in departure["departureTime"]
    assert "timeReal" in departure["departureTime"]


def test_parse_api_time_keeps_timezone():
    result = parse_api_time("2026-10-28T13:53:30.000+0100")
    assert result == t(13, 53, 30)
    assert result.utcoffset() == timedelta(hours=1)


# --- Tests für die implementierten Funktionen -----------------------------


def test_parse_monitor_keeps_only_configured_lines(config):
    """In der Antwort steckt auch der 2er Richtung Friedrich-Engels-Platz (stopId 319)."""
    data = load_fixture("monitor_multi_322_319_350.json")
    departures = parse_monitor(data, config.lines, fetched_at=t(13, 45, 52))

    found = {(d.line, d.stop_id) for d in departures}
    assert found == {("2", 322), ("31", 322), ("12", 319), ("5", 350)}
    assert len(departures) == 36


def test_parse_monitor_reads_times(config):
    data = load_fixture("monitor_hoechstaedtplatz_319.json")
    departures = parse_monitor(data, config.lines, fetched_at=t(13, 45, 27))

    first = departures[0]
    assert first.line == "12"
    assert first.time_planned == t(13, 53, 30)
    assert first.time_real == t(13, 54, 2)


def test_parse_monitor_missing_timereal_becomes_none(config):
    data = load_fixture("monitor_no_timereal.json")
    departures = parse_monitor(data, config.lines, fetched_at=t(13, 45))

    line_2 = [d for d in departures if d.line == "2"]
    assert line_2[0].time_real is None
    assert line_2[1].time_real is not None


def test_parse_monitor_reads_realtime_supported_false(config):
    data = load_fixture("monitor_realtime_not_supported.json")
    departures = parse_monitor(data, config.lines, fetched_at=t(13, 45))

    line_31 = [d for d in departures if d.line == "31"]
    assert line_31
    assert all(d.realtime_supported is False for d in line_31)


def test_parse_monitor_empty_response_gives_empty_list(config):
    data = load_fixture("monitor_empty.json")
    assert parse_monitor(data, config.lines, fetched_at=t(13, 45)) == []


def test_empty_response_is_not_valid():
    assert api_client.is_valid_response(load_fixture("monitor_empty.json")) is False
    assert api_client.is_valid_response(None) is False
    assert api_client.is_valid_response(load_fixture("monitor_hoechstaedtplatz_322.json")) is True
