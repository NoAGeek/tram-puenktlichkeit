"""Gemeinsame Datenklassen: die Schnittstelle zwischen Mo und Omar.

Mo (Datenabruf) erzeugt ``Departure``-Objekte.
Omar (Speicherung, Statistik) verarbeitet ``Departure``- und ``Trip``-Objekte.

Änderungen an dieser Datei bitte nur gemeinsam absprechen,
sonst passt der Code der beiden Hälften nicht mehr zusammen.
"""

from dataclasses import dataclass
from datetime import datetime

# Mögliche Werte für Trip.status
STATUS_OK = "ok"                        # Verspätung sicher bestimmt
STATUS_NO_REALTIME = "no_realtime"      # nie ein timeReal gesehen
STATUS_NOT_SUPPORTED = "not_supported"  # realtimeSupported war false
STATUS_UNSURE = "unsure"                # Fahrt nur wegen Datenlücke "verschwunden"


@dataclass(frozen=True)
class Departure:
    """Eine Abfahrt, so wie sie bei EINER Abfrage im Monitor stand.

    Dieselbe echte Fahrt taucht über mehrere Abfragen hinweg mehrmals auf,
    jeweils mit anderem ``fetched_at`` und eventuell anderem ``time_real``.

    Attributes:
        fetched_at: Zeitpunkt, zu dem WIR die API abgefragt haben.
        line: Liniennummer als Text, z. B. "2".
        stop_id: Bahnsteig-Nummer (RBL), z. B. 322.
        direction: "H" oder "R" laut API.
        towards: Fahrtziel laut API, z. B. "Dornbach".
        time_planned: Abfahrt laut Fahrplan (``departureTime.timePlanned``).
        time_real: Prognose (``departureTime.timeReal``), ``None`` wenn sie fehlt.
        realtime_supported: Wert von ``vehicle.realtimeSupported``.
    """

    fetched_at: datetime
    line: str
    stop_id: int
    direction: str
    towards: str
    time_planned: datetime
    time_real: datetime | None
    realtime_supported: bool

    def trip_key(self) -> tuple[str, int, str, datetime]:
        """Gibt den Schlüssel zurück, an dem wir eine Fahrt wiedererkennen.

        Zwei Departures mit gleichem Schlüssel gehören zur selben Fahrt.
        """
        return (self.line, self.stop_id, self.direction, self.time_planned)


@dataclass(frozen=True)
class Trip:
    """Eine ausgewertete Fahrt, berechnet aus mehreren Departures.

    Attributes:
        line, stop_id, direction, time_planned: wie bei ``Departure``
            (zusammen der Schlüssel der Fahrt).
        final_time_real: letzter gesehener timeReal-Wert oder ``None``.
        delay_seconds: ``final_time_real - time_planned`` in Sekunden,
            ``None`` wenn nicht bestimmbar. Negativ = zu früh.
        status: einer der ``STATUS_*``-Werte oben.
        observation_count: in wie vielen Abfragen die Fahrt gesehen wurde.
    """

    line: str
    stop_id: int
    direction: str
    time_planned: datetime
    final_time_real: datetime | None
    delay_seconds: int | None
    status: str
    observation_count: int
