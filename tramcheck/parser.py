
"""Wandelt das JSON der Wiener-Linien-API in Departure-Objekte um. [Omar]"""

from datetime import datetime

from tramcheck.config import LineConfig
from tramcheck.models import Departure


def parse_api_time(text: str) -> datetime:
    """Wandelt einen API-Zeitstempel in ein datetime-Objekt um."""
    return datetime.fromisoformat(text)


def is_wanted(
    line: str,
    stop_id: int,
    direction: str,
    lines: list[LineConfig],
) -> bool:
    """Prüft, ob Linie, Haltestelle und Richtung in der Config stehen."""
    for configured_line in lines:
        if (
            configured_line.line == line
            and configured_line.stop_id == stop_id
            and configured_line.direction == direction
        ):
            return True

    return False


def parse_monitor(
    data: dict,
    lines: list[LineConfig],
    fetched_at: datetime,
) -> list[Departure]:
    """Liest die gewünschten Abfahrten aus der API-Antwort."""
    results = []

    for monitor in data.get("data", {}).get("monitors", []):
        attributes = (
            monitor.get("locationStop", {})
            .get("properties", {})
            .get("attributes", {})
        )

        stop_id = attributes.get("rbl")

        if stop_id is None:
            continue

        for line_data in monitor.get("lines", []):
            line = str(line_data.get("name", ""))
            direction = str(line_data.get("direction", ""))
            towards = str(line_data.get("towards", ""))

            if not is_wanted(line, stop_id, direction, lines):
                continue

            departures = (
                line_data.get("departures", {})
                .get("departure", [])
            )

            for departure in departures:
                departure_time = departure.get("departureTime", {})

                planned_text = departure_time.get("timePlanned")

                if not planned_text:
                    continue

                time_planned = parse_api_time(planned_text)

                real_text = departure_time.get("timeReal")

                time_real = (
                    parse_api_time(real_text)
                    if real_text
                    else None
                )

                vehicle = departure.get("vehicle") or {}

                line_realtime = line_data.get("realtimeSupported")
                vehicle_realtime = vehicle.get("realtimeSupported")

                if line_realtime is False or vehicle_realtime is False:
                    realtime_supported = False
                elif vehicle_realtime is not None:
                    realtime_supported = vehicle_realtime
                else:
                    realtime_supported = bool(line_realtime)

                result = Departure(
                    fetched_at=fetched_at,
                    line=line,
                    stop_id=stop_id,
                    direction=direction,
                    towards=towards,
                    time_planned=time_planned,
                    time_real=time_real,
                    realtime_supported=realtime_supported,
                )

                results.append(result)

    return results
