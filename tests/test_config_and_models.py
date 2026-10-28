"""Tests für die gemeinsamen Teile: Config und Datenklassen."""

from conftest import make_departure, t


def test_config_has_four_lines(config):
    assert [line.line for line in config.lines] == ["2", "31", "12", "5"]


def test_config_does_not_use_line_33(config):
    assert "33" not in [line.line for line in config.lines]


def test_config_stop_ids_are_unique_and_sorted(config):
    assert config.stop_ids() == [319, 322, 350]


def test_config_threshold_is_three_minutes(config):
    assert config.delay_threshold_seconds == 180


def test_same_trip_has_same_key_across_polls():
    """Dieselbe Fahrt, zwei Abfragen, andere Prognose -> gleicher Schlüssel."""
    first = make_departure(fetched_at=t(13, 45), time_planned=t(13, 53, 30), time_real=t(13, 54))
    second = make_departure(fetched_at=t(13, 46), time_planned=t(13, 53, 30), time_real=t(13, 55))
    assert first.trip_key() == second.trip_key()


def test_different_planned_time_means_different_trip():
    first = make_departure(fetched_at=t(13, 45), time_planned=t(13, 53, 30), time_real=None)
    second = make_departure(fetched_at=t(13, 45), time_planned=t(14, 3, 30), time_real=None)
    assert first.trip_key() != second.trip_key()
