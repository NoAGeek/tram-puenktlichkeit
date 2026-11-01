"""Tests für Mo: Verfolgung einer Fahrt über mehrere Abfragen.

Braucht keine JSON-Dateien: die Departures werden mit make_departure von Hand gebaut.
"""

from conftest import make_departure, t
from tramcheck import models
from tramcheck.trips import build_trip, build_trips, compute_delay_seconds, group_by_trip

PLANNED = t(14, 0)


def test_delay_positive_when_late():
    assert compute_delay_seconds(t(13, 53, 30), t(13, 54, 2)) == 32


def test_delay_negative_when_early():
    assert compute_delay_seconds(t(14, 0), t(13, 59, 30)) == -30


# --- Tests für die umgesetzten Funktionen -----------------------------


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


def test_trip_without_timereal_is_marked():
    observations = [make_departure(fetched_at=t(13, 59), time_planned=PLANNED, time_real=None)]
    trip = build_trip(observations, [t(13, 59), t(14, 0)])

    assert trip.status == models.STATUS_NO_REALTIME
    assert trip.delay_seconds is None


def test_trip_not_supported_is_marked():
    observations = [
        make_departure(fetched_at=t(13, 59), time_planned=PLANNED, time_real=None, realtime_supported=False)
    ]
    trip = build_trip(observations, [t(13, 59), t(14, 0)])

    assert trip.status == models.STATUS_NOT_SUPPORTED


def test_trip_is_unsure_when_collector_stopped():
    """Nach der letzten Sichtung gab es keine erfolgreiche Abfrage mehr."""
    observations = [make_departure(fetched_at=t(13, 59), time_planned=PLANNED, time_real=t(14, 2))]
    trip = build_trip(observations, [t(13, 58), t(13, 59)])

    assert trip.status == models.STATUS_UNSURE


def test_trip_is_unsure_after_long_gap():
    """Die nächste Abfrage kam erst 30 min später: Abfahrt fiel in die Lücke."""
    observations = [make_departure(fetched_at=t(13, 59), time_planned=PLANNED, time_real=t(14, 2))]
    trip = build_trip(observations, [t(13, 59), t(14, 29)])

    assert trip.status == models.STATUS_UNSURE


def test_group_by_trip_sorts_each_trip_by_time():
    late = make_departure(fetched_at=t(13, 58), time_planned=PLANNED, time_real=t(14, 3))
    early = make_departure(fetched_at=t(13, 57), time_planned=PLANNED, time_real=t(14, 1))
    other = make_departure(fetched_at=t(13, 57), time_planned=t(14, 10), time_real=None)

    groups = group_by_trip([late, other, early])

    assert len(groups) == 2
    assert groups[early.trip_key()] == [early, late]


def test_build_trips_makes_one_trip_per_key():
    observations = [
        make_departure(fetched_at=t(13, 57), time_planned=PLANNED, time_real=t(14, 1)),
        make_departure(fetched_at=t(13, 58), time_planned=PLANNED, time_real=t(14, 1)),
        make_departure(fetched_at=t(13, 57), time_planned=PLANNED, time_real=t(14, 0), line="31"),
    ]
    trips = build_trips(observations, [t(13, 57), t(13, 58), t(13, 59)])

    assert sorted(trip.line for trip in trips) == ["2", "31"]
