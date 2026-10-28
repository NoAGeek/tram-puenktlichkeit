"""Macht aus vielen Beobachtungen einzelne Fahrten.  [Omar]

Das fachliche Herzstück. Regeln:

1. Beobachtungen mit gleichem ``Departure.trip_key()`` gehören zur selben Fahrt.
2. Die endgültige Verspätung ist der LETZTE gesehene timeReal-Wert
   minus timePlanned.
3. Status:
   - not_supported: realtime_supported war bei der Fahrt false
   - no_realtime:   nie ein timeReal gesehen
   - unsure:        nach der letzten Sichtung gab es KEINE erfolgreiche
                    Abfrage mehr (z. B. Laptop im Ruhemodus), also wissen
                    wir nicht, ob die Fahrt wirklich abgefahren ist
   - ok:            alles andere
"""

from datetime import datetime

from tramcheck.models import Departure, Trip


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

    TODO (Omar): umsetzen. Tipp: ``dict.setdefault(key, []).append(obs)``,
        danach jede Liste mit ``sorted(..., key=lambda d: d.fetched_at)``.
    """
    raise NotImplementedError("TODO Omar: group_by_trip")


def has_disappeared(last_seen: datetime, successful_poll_times: list[datetime]) -> bool:
    """Prüft, ob die Fahrt wirklich aus dem Monitor verschwunden ist.

    Das ist nur sicher, wenn es NACH ``last_seen`` noch mindestens eine
    erfolgreiche Abfrage gab (in der die Fahrt dann gefehlt hat).

    TODO (Omar): ``True``, wenn irgendein Zeitpunkt in
        ``successful_poll_times`` größer als ``last_seen`` ist.
    """
    raise NotImplementedError("TODO Omar: has_disappeared")


def build_trip(observations: list[Departure], successful_poll_times: list[datetime]) -> Trip:
    """Baut aus den Beobachtungen EINER Fahrt ein ``Trip``-Objekt.

    Args:
        observations: alle Beobachtungen dieser Fahrt, nach Zeit sortiert.
        successful_poll_times: aus ``storage.load_successful_poll_times``.

    TODO (Omar): Status nach den Regeln oben bestimmen, letzte
        Beobachtung mit ``time_real`` suchen, ``compute_delay_seconds`` nutzen.
    """
    raise NotImplementedError("TODO Omar: build_trip")


def build_trips(observations: list[Departure], successful_poll_times: list[datetime]) -> list[Trip]:
    """Baut alle Fahrten: ``group_by_trip``, dann ``build_trip`` für jede Gruppe.

    TODO (Omar): umsetzen.
    """
    raise NotImplementedError("TODO Omar: build_trips")
