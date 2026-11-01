"""Macht aus vielen Beobachtungen einzelne Fahrten.  [Mo]

Das fachliche Herzstück. Regeln:

1. Beobachtungen mit gleichem ``Departure.trip_key()`` gehören zur selben Fahrt.
2. Die endgültige Verspätung ist der LETZTE gesehene timeReal-Wert
   minus timePlanned.
3. Status:
   - not_supported: realtime_supported war bei der Fahrt false
   - no_realtime:   nie ein timeReal gesehen
   - unsure:        nach der letzten Sichtung gab es KEINE erfolgreiche
                    Abfrage mehr (z. B. Laptop im Ruhemodus), oder die
                    nächste kam erst nach mehr als ``MAX_GAP``. Dann wissen
                    wir nicht, ob die letzte Prognose noch gestimmt hat
   - ok:            alles andere
"""

from datetime import datetime, timedelta

from tramcheck import models
from tramcheck.models import Departure, Trip

# Kam nach der letzten Sichtung länger als das keine erfolgreiche Abfrage,
# ist die Fahrt vermutlich in einer Datenlücke abgefahren: dann "unsure".
MAX_GAP = timedelta(minutes=5)


def compute_delay_seconds(time_planned: datetime, time_real: datetime) -> int:
    """Verspätung in ganzen Sekunden. Negativ, wenn die Fahrt zu früh ist.

    Beispiel: geplant 13:53:30, real 13:54:02 -> 32
    """
    return int((time_real - time_planned).total_seconds())


def group_by_trip(observations: list[Departure]) -> dict[tuple, list[Departure]]:
    """Sortiert die Beobachtungen nach Fahrt.

    Returns:
        ``dict``: Schlüssel = ``trip_key()``, Wert = Liste der Beobachtungen
        dieser Fahrt, nach ``fetched_at`` aufsteigend sortiert.
    """
    groups = {}
    for obs in observations:
        groups.setdefault(obs.trip_key(), []).append(obs)

    for key in groups:
        groups[key] = sorted(groups[key], key=lambda d: d.fetched_at)
    return groups


def has_disappeared(last_seen: datetime, successful_poll_times: list[datetime]) -> bool:
   
    for successful_poll_time in successful_poll_times:
        if successful_poll_time > last_seen:
            return True

    return False


def next_poll_after(last_seen: datetime, successful_poll_times: list[datetime]) -> datetime | None:
    """Die erste erfolgreiche Abfrage nach ``last_seen``, oder ``None``."""
    for poll_time in successful_poll_times:
        if poll_time > last_seen:
            return poll_time
    return None


def build_trip(observations: list[Departure], successful_poll_times: list[datetime]) -> Trip:
    """Baut aus den Beobachtungen EINER Fahrt ein ``Trip``-Objekt.

    Args:
        observations: alle Beobachtungen dieser Fahrt, nach Zeit sortiert.
        successful_poll_times: aus ``storage.load_successful_poll_times``,
            aufsteigend sortiert.
    """
    first = observations[0]
    last_seen = observations[-1].fetched_at

    with_real = [obs for obs in observations if obs.time_real is not None]
    final_time_real = with_real[-1].time_real if with_real else None
    delay = compute_delay_seconds(first.time_planned, final_time_real) if final_time_real else None

    if any(not obs.realtime_supported for obs in observations):
        status = models.STATUS_NOT_SUPPORTED
    elif final_time_real is None:
        status = models.STATUS_NO_REALTIME
    elif not has_disappeared(last_seen, successful_poll_times):
        status = models.STATUS_UNSURE
    elif next_poll_after(last_seen, successful_poll_times) - last_seen > MAX_GAP:
        status = models.STATUS_UNSURE
    else:
        status = models.STATUS_OK

    return Trip(
        line=first.line,
        stop_id=first.stop_id,
        direction=first.direction,
        time_planned=first.time_planned,
        final_time_real=final_time_real,
        delay_seconds=delay,
        status=status,
        observation_count=len(observations),
    )


def build_trips(observations: list[Departure], successful_poll_times: list[datetime]) -> list[Trip]:
    """Baut alle Fahrten: ``group_by_trip``, dann ``build_trip`` für jede Gruppe."""
    poll_times = sorted(successful_poll_times)
    groups = group_by_trip(observations)
    return [build_trip(group, poll_times) for group in groups.values()]
