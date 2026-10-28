"""Gemeinsame Hilfen für alle Tests.

pytest lädt diese Datei automatisch. Fixtures, die hier stehen, können
alle Testdateien einfach als Parameter verwenden.
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from tramcheck.config import load_config
from tramcheck.models import Departure

FIXTURE_DIR = Path(__file__).parent / "fixtures"
PROJECT_DIR = Path(__file__).parent.parent

# Wiener Winterzeit, wie in den API-Antworten
VIENNA = timezone(timedelta(hours=1))

# Markierung für Tests von Funktionen, die noch TODO sind.
# Sobald ihr die Funktion programmiert habt: @todo über dem Test löschen.
todo = pytest.mark.skip(reason="Funktion noch nicht umgesetzt (TODO)")


def load_fixture(name: str) -> dict:
    """Lädt eine gespeicherte API-Antwort aus tests/fixtures/."""
    with open(FIXTURE_DIR / name, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def config():
    """Die echte config.toml des Projekts."""
    return load_config(PROJECT_DIR / "config.toml")


def t(hour: int, minute: int, second: int = 0) -> datetime:
    """Kurzschreibweise für eine Uhrzeit am 28.10.2026 in Wien."""
    return datetime(2026, 10, 28, hour, minute, second, tzinfo=VIENNA)


def make_departure(
    fetched_at: datetime,
    time_planned: datetime,
    time_real: datetime | None,
    line: str = "2",
    realtime_supported: bool = True,
) -> Departure:
    """Baut ein Departure von Hand: für Tests von Omar ohne API und JSON."""
    return Departure(
        fetched_at=fetched_at,
        line=line,
        stop_id=322,
        direction="R",
        towards="Dornbach",
        time_planned=time_planned,
        time_real=time_real,
        realtime_supported=realtime_supported,
    )
