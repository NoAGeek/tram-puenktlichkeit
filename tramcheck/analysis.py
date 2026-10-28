"""Kennzahlen pro Linie.  [Mo]

Nur Fahrten mit Status "ok" fließen in Anteil und Durchschnitt ein.
Alle anderen werden extra gezählt und NIE als pünktlich gewertet.
"""

from dataclasses import dataclass

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

    TODO (Mo):
        1. Fahrten nach ``trip.line`` gruppieren
        2. Pro Linie zählen und rechnen (siehe Attribute von ``LineStats``)
        3. Für den Durchschnitt hilft ``statistics.mean`` aus der Standardbibliothek
    """
    raise NotImplementedError("TODO Mo: compute_line_stats")
