"""Diagramme mit matplotlib.  [Mo]

Alle Funktionen speichern ein PNG und zeigen nichts am Bildschirm an.
So läuft das auch auf einem Rechner ohne Bildschirm (z. B. Raspberry Pi).
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # ohne Bildschirm zeichnen, nur in Dateien
import matplotlib.pyplot as plt  # noqa: E402

from tramcheck import models  # noqa: E402
from tramcheck.analysis import LineStats  # noqa: E402
from tramcheck.models import Trip  # noqa: E402


# Feste Farbe pro Linie, damit eine Linie in jedem Diagramm gleich aussieht
LINE_COLORS = {"2": "#2a78d6", "5": "#eb6834", "12": "#1baf7a", "31": "#eda100"}
TEXT_COLOR = "#52514e"
GRID_COLOR = "#e4e3df"


def sort_lines(lines) -> list[str]:
    """Liniennummern numerisch sortieren: 2, 5, 12, 31 statt 12, 2, 31, 5."""
    return sorted(lines, key=lambda line: int(line) if line.isdigit() else 999)


def style_axes(ax) -> None:
    """Dezente Achsen: nur unten und links, helles Gitter hinter den Daten."""
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID_COLOR)
    ax.tick_params(colors=TEXT_COLOR)
    ax.yaxis.grid(True, color=GRID_COLOR, linewidth=0.8)
    ax.set_axisbelow(True)


def plot_delayed_share(stats: dict[str, LineStats], output_path: Path, threshold_seconds: int = 180) -> None:
    """Balkendiagramm: Anteil verspäteter Fahrten pro Linie (in Prozent)."""
    lines = [line for line in sort_lines(stats) if stats[line].delayed_share is not None]
    shares = [stats[line].delayed_share * 100 for line in lines]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(lines, shares, width=0.6, color=[LINE_COLORS.get(line, "#888888") for line in lines])
    ax.bar_label(bars, labels=[f"{share:.1f} %" for share in shares], padding=3, color=TEXT_COLOR)

    ax.set_xlabel("Linie")
    ax.set_ylabel("Anteil verspätet (%)")
    ax.set_title(f"Anteil verspäteter Fahrten (verspätet = mehr als {threshold_seconds // 60} min)")
    ax.set_ylim(0, max(shares + [10]) * 1.15)
    style_axes(ax)

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_delay_distribution(trips: list[Trip], output_path: Path) -> None:
    """Boxplot: Verteilung der Verspätung (in Minuten) pro Linie.

    Nur Fahrten mit Status "ok" werden verwendet.
    """
    by_line = {}
    for trip in trips:
        if trip.status == models.STATUS_OK:
            by_line.setdefault(trip.line, []).append(trip.delay_seconds / 60)
    lines = sort_lines(by_line)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    if lines:
        boxes = ax.boxplot([by_line[line] for line in lines], patch_artist=True, widths=0.5)
        ax.set_xticks(range(1, len(lines) + 1), lines)
        for patch, line in zip(boxes["boxes"], lines):
            patch.set_facecolor(LINE_COLORS.get(line, "#888888"))
            patch.set_alpha(0.6)
        for median in boxes["medians"]:
            median.set_color("#0b0b0b")
    ax.axhline(0, color=TEXT_COLOR, linewidth=0.8, linestyle="--")

    ax.set_xlabel("Linie")
    ax.set_ylabel("Verspätung (min), negativ = zu früh")
    ax.set_title("Verteilung der Verspätung pro Linie")
    style_axes(ax)

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_delay_by_hour(trips: list[Trip], output_path: Path) -> None:
    """Durchschnittliche Verspätung nach Tageszeit (Stunde 0–23), eine Linie pro Bim-Linie."""
    sums = {}
    for trip in trips:
        if trip.status == models.STATUS_OK:
            hours = sums.setdefault(trip.line, {})
            hours.setdefault(trip.time_planned.hour, []).append(trip.delay_seconds / 60)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    for line in sort_lines(sums):
        hours = sorted(sums[line])
        means = [sum(sums[line][h]) / len(sums[line][h]) for h in hours]
        color = LINE_COLORS.get(line, "#888888")
        ax.plot(hours, means, color=color, linewidth=2, marker="o", markersize=4, label=f"Linie {line}")
        ax.annotate(f"{line}", (hours[-1], means[-1]), xytext=(6, 0), textcoords="offset points",
                    color=TEXT_COLOR, va="center")

    ax.set_xlim(0, 23)
    ax.set_xticks(range(0, 24, 2))
    ax.set_xlabel("Uhrzeit (Stunde, geplante Abfahrt)")
    ax.set_ylabel("mittlere Verspätung (min)")
    ax.set_title("Verspätung nach Tageszeit")
    if sums:
        ax.legend(frameon=False)
    style_axes(ax)

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
