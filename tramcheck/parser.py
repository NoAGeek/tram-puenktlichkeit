"""Wandelt das JSON der API in ``Departure``-Objekte um.  [Person A]

Reine Funktionen ohne Netzwerk, darum leicht mit Fixtures zu testen.

Struktur der API-Antwort (vereinfacht):

    data.monitors[]                         # ein Eintrag pro stopId
        .locationStop.properties.attributes.rbl   -> stop_id (int)
        .lines[]                            # Linien an diesem Bahnsteig
            .name, .direction, .towards
            .departures.departure[]         # die einzelnen Abfahrten
                .departureTime.timePlanned
                .departureTime.timeReal     # kann fehlen!
                .vehicle.realtimeSupported
"""

from datetime import datetime

from tramcheck.config import LineConfig
from tramcheck.models import Departure


def parse_api_time(text: str) -> datetime:
    """Wandelt einen Zeitstempel der API in ein ``datetime`` um.

    Beispiel: ``"2026-10-28T13:53:30.000+0100"`` wird zu einem
    ``datetime`` mit Zeitzone +01:00. Die Zeitzone bleibt erhalten,
    damit die Sommer-/Winterzeit-Umstellung keine Fehler macht.
    """
    return datetime.fromisoformat(text)


def is_wanted(line: str, stop_id: int, direction: str, lines: list[LineConfig]) -> bool:
    """Prüft, ob diese Kombination in unserer Config steht.

    Nötig, weil an einem Bahnsteig auch andere Linien halten.
    Beispiel: An stopId 319 hält auch der 2er Richtung Friedrich-Engels-Platz,
    den wollen wir dort aber nicht.

    TODO (Person A): ``True`` zurückgeben, wenn ein Eintrag in ``lines``
        dieselbe ``line``, ``stop_id`` und ``direction`` hat.
    """
    raise NotImplementedError("TODO Person A: is_wanted")


def parse_monitor(data: dict, lines: list[LineConfig], fetched_at: datetime) -> list[Departure]:
    """Holt alle gewünschten Abfahrten aus einer API-Antwort.

    Args:
        data: das JSON von ``api_client.fetch_monitor``.
        lines: die Linien aus der Config (nur diese werden behalten).
        fetched_at: Zeitpunkt unserer Abfrage.

    Returns:
        Liste von ``Departure``. Leere Liste, wenn nichts Passendes dabei ist.

    TODO (Person A):
        1. Über ``data["data"]["monitors"]`` gehen, pro Monitor die
           stop_id aus ``locationStop.properties.attributes.rbl`` lesen
        2. Darin über ``lines`` gehen, mit ``is_wanted`` filtern
        3. Darin über ``departures.departure`` gehen und je ein
           ``Departure`` bauen:
           - ``time_planned`` mit ``parse_api_time``
           - ``time_real``: ``None`` wenn der Schlüssel fehlt
             (Tipp: ``departure_time.get("timeReal")``)
           - ``realtime_supported`` aus ``vehicle``, falls vorhanden,
             sonst vom Linien-Eintrag
    """
    raise NotImplementedError("TODO Person A: parse_monitor")
