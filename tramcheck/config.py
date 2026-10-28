"""Lädt die Konfiguration aus ``config.toml`` (gemeinsam genutzt).

Dieses Modul ist bereits fertig, weil es nur Werte einliest.
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LineConfig:
    """Eine gemessene Linie an einem festen Bahnsteig in fester Richtung."""

    line: str
    stop_id: int
    stop_name: str
    direction: str
    towards: str


@dataclass(frozen=True)
class Config:
    """Alle Einstellungen aus ``config.toml``."""

    poll_interval_seconds: int
    request_timeout_seconds: int
    delay_threshold_seconds: int
    api_url: str
    database_path: Path
    log_path: Path
    chart_dir: Path
    lines: list[LineConfig]

    def stop_ids(self) -> list[int]:
        """Alle verschiedenen stopIds, sortiert. Damit fragen wir die API ab."""
        return sorted({line.stop_id for line in self.lines})


def load_config(path: str | Path = "config.toml") -> Config:
    """Liest die TOML-Datei und gibt ein ``Config``-Objekt zurück.

    Relative Pfade (Datenbank, Log, Diagramme) werden relativ zum
    Ordner der Config-Datei aufgelöst.

    Args:
        path: Pfad zur Config-Datei.

    Returns:
        Die eingelesene Konfiguration.
    """
    path = Path(path)
    with open(path, "rb") as f:
        raw = tomllib.load(f)

    base_dir = path.parent
    return Config(
        poll_interval_seconds=raw["poll_interval_seconds"],
        request_timeout_seconds=raw["request_timeout_seconds"],
        delay_threshold_seconds=raw["delay_threshold_seconds"],
        api_url=raw["api_url"],
        database_path=base_dir / raw["database_path"],
        log_path=base_dir / raw["log_path"],
        chart_dir=base_dir / raw["chart_dir"],
        lines=[LineConfig(**entry) for entry in raw["lines"]],
    )
