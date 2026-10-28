"""Tests für Mo: Verfolgung einer Fahrt über mehrere Abfragen.

Braucht keine JSON-Dateien: die Departures werden mit make_departure von Hand gebaut.
"""

from conftest import make_departure, t, todo
from tramcheck import models
from tramcheck.trips import build_trip, compute_delay_seconds

PLANNED = t(14, 0)


def test_delay_positive_when_late():
    assert compute_delay_seconds(t(13, 53, 30), t(13, 54, 2)) == 32


def test_delay_negative_when_early():
    assert compute_delay_seconds(t(14, 0), t(13, 59, 30)) == -30


# --- Tests für TODO-Funktionen: @todo löschen, sobald umgesetzt -----------


@todo
def test_last_timereal_counts():
    """Die Prognose ändert sich; zählen soll die letzte vor dem Verschwinden."""
    observations = [
        make_departure(fetched_at=t(13, 57), time_planned=PLANNED, time_real=t(14, 1)),
        make_departure(fetched_at=t(13, 58), time_planned=PLANNED, time_real=t(14, 3)),
        make_departure(fetched_at=t(13, 59), time_planned=PLANNED, time_real=t(14, 4)),
    ]
    polls = [t(13, 57), t(13, 58), t(13, 59), t(14, 0)]  # um 14:00 war sie weg

    trip = build_trip(observations, polls)

    assert trip.status == models.STATUS_OK
    assert trip.delay_seconds == 240
    assert trip.observation_count == 3


@todo
def test_trip_without_timereal_is_marked():
    observations = [make_departure(fetched_at=t(13, 59), time_planned=PLANNED, time_real=None)]
    trip = build_trip(observations, [t(13, 59), t(14, 0)])

    assert trip.status == models.STATUS_NO_REALTIME
    assert trip.delay_seconds is None


@todo
def test_trip_not_supported_is_marked():
    observations = [
        make_departure(fetched_at=t(13, 59), time_planned=PLANNED, time_real=None, realtime_supported=False)
    ]
    trip = build_trip(observations, [t(13, 59), t(14, 0)])

    assert trip.status == models.STATUS_NOT_SUPPORTED


@todo
def test_trip_is_unsure_when_collector_stopped():
    """Nach der letzten Sichtung gab es keine erfolgreiche Abfrage mehr."""
    observations = [make_departure(fetched_at=t(13, 59), time_planned=PLANNED, time_real=t(14, 2))]
    trip = build_trip(observations, [t(13, 58), t(13, 59)])

    assert trip.status == models.STATUS_UNSURE
