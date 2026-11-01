"""Kennzahlen pro Linie.  [Mo]

Nur Fahrten mit Status "ok" fließen in Anteil und Durchschnitt ein.
Alle anderen werden extra gezählt und NIE als pünktlich gewertet.
"""

from dataclasses import dataclass
from statistics import mean

from tramcheck import models
from tramcheck.models import Trip


@dataclass(frozen=True)
class LineStats:
    """Ergebnis der Auswertung für eine Linie.

    Attributes:
        line: Liniennummer.
        trips_total: alle Fahrten, egal welcher Status.
        trips_evaluated: Fahrten mit Status "ok".
        trips_delayed: davon verspätet.
        delayed_share: ``trips_delayed / trips_evaluated`` (0.0 bis 1.0),
            ``None`` wenn ``trips_evaluated == 0``.
        mean_delay_seconds: Durchschnitt von ``delay_seconds`` der "ok"-Fahrten,
            ``None`` wenn es keine gibt.
        trips_without_realtime: Status "no_realtime" oder "not_supported".
        trips_unsure: Status "unsure".
    """

    line: str
    trips_total: int
    trips_evaluated: int
    trips_delayed: int
    delayed_share: float | None
    mean_delay_seconds: float | None
    trips_without_realtime: int
    trips_unsure: int


def is_delayed(delay_seconds: int, threshold_seconds: int) -> bool:
    """Verspätet heißt: MEHR als ``threshold_seconds`` zu spät.

    Genau auf dem Schwellenwert gilt noch als pünktlich.
    Verfrühte Fahrten (negativ) gelten als pünktlich.
    """
    return delay_seconds > threshold_seconds


def compute_line_stats(trips: list[Trip], threshold_seconds: int) -> dict[str, LineStats]:
    """Berechnet ``LineStats`` für jede Linie.

    Returns:
        ``dict`` Liniennummer -> ``LineStats``.
    """
    by_line = {}
    for trip in trips:
        by_line.setdefault(trip.line, []).append(trip)

    stats = {}
    for line, line_trips in by_line.items():
        delays = [trip.delay_seconds for trip in line_trips if trip.status == models.STATUS_OK]
        delayed = [d for d in delays if is_delayed(d, threshold_seconds)]
        statuses = [trip.status for trip in line_trips]

        stats[line] = LineStats(
            line=line,
            trips_total=len(line_trips),
            trips_evaluated=len(delays),
            trips_delayed=len(delayed),
            delayed_share=len(delayed) / len(delays) if delays else None,
            mean_delay_seconds=mean(delays) if delays else None,
            trips_without_realtime=statuses.count(models.STATUS_NO_REALTIME)
            + statuses.count(models.STATUS_NOT_SUPPORTED),
            trips_unsure=statuses.count(models.STATUS_UNSURE),
        )
    return stats
