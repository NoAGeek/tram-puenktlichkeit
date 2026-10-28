"""Tests für Omar: Kennzahlen pro Linie."""

import pytest

from conftest import t, todo
from tramcheck import models
from tramcheck.analysis import compute_line_stats, is_delayed


@pytest.mark.parametrize(
    ("delay", "expected"),
    [
        (0, False),
        (180, False),   # genau 3 min: noch pünktlich
        (181, True),    # mehr als 3 min: verspätet
        (-60, False),   # zu früh: zählt als pünktlich
    ],
)
def test_is_delayed_with_three_minute_threshold(delay, expected):
    assert is_delayed(delay, threshold_seconds=180) is expected


def make_trip(line: str, delay: int | None, status: str = models.STATUS_OK) -> models.Trip:
    return models.Trip(
        line=line, stop_id=322, direction="R", time_planned=t(14, 0),
        final_time_real=None, delay_seconds=delay, status=status, observation_count=1,
    )


# --- Tests für TODO-Funktionen: @todo löschen, sobald umgesetzt -----------


@todo
def test_line_stats_counts_only_ok_trips():
    trips = [
        make_trip("2", 60),
        make_trip("2", 300),
        make_trip("2", None, models.STATUS_NO_REALTIME),
        make_trip("2", None, models.STATUS_UNSURE),
    ]
    stats = compute_line_stats(trips, threshold_seconds=180)["2"]

    assert stats.trips_total == 4
    assert stats.trips_evaluated == 2
    assert stats.trips_delayed == 1
    assert stats.delayed_share == 0.5
    assert stats.mean_delay_seconds == 180
    assert stats.trips_without_realtime == 1
    assert stats.trips_unsure == 1
