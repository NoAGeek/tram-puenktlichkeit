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


# Stufen der Pünktlichkeit, von "zu früh" bis "verspätet".
# Blau = früh, Grau = pünktlich, Orange immer dunkler = immer später.
DELAY_BANDS = [
    ("mehr als 1 min zu früh", "#2a78d6", "white"),
    ("pünktlich (± 1 min)", "#c3c2b7", "#0b0b0b"),
    ("1 bis 3 min zu spät", "#f5a978", "#0b0b0b"),
    ("mehr als 3 min zu spät", "#c8441b", "white"),
]


def delay_band(delay_seconds: int, threshold_seconds: int) -> int:
    """In welche Stufe von ``DELAY_BANDS`` fällt eine Verspätung? (0 bis 3)"""
    if delay_seconds < -60:
        return 0
    if delay_seconds <= 60:
        return 1
    if delay_seconds <= threshold_seconds:
        return 2
    return 3


def ok_trips_by_line(trips: list[Trip]) -> dict[str, list[Trip]]:
    """Nur Fahrten mit sicher bestimmter Verspätung, nach Linie sortiert."""
    by_line = {}
    for trip in trips:
        if trip.status == models.STATUS_OK:
            by_line.setdefault(trip.line, []).append(trip)
    return by_line


def save(fig, output_path: Path) -> None:
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_delayed_share(stats: dict[str, LineStats], output_path: Path, threshold_seconds: int = 180) -> None:
    """Balkendiagramm: Wie viel Prozent der Fahrten waren verspätet? Eine Zahl pro Linie."""
    lines = [line for line in sort_lines(stats) if stats[line].delayed_share is not None]
    shares = [stats[line].delayed_share * 100 for line in lines]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar([f"Linie {line}" for line in lines], shares, width=0.6,
                  color=[LINE_COLORS.get(line, "#888888") for line in lines])
    labels = [
        f"{share:.1f} %\n{stats[line].trips_delayed} von {stats[line].trips_evaluated}"
        for line, share in zip(lines, shares)
    ]
    ax.bar_label(bars, labels=labels, padding=4, color=TEXT_COLOR)

    ax.set_ylabel("verspätete Fahrten (%)")
    ax.set_title(f"Wie oft ist die Bim mehr als {threshold_seconds // 60} Minuten zu spät?", loc="left")
    ax.set_ylim(0, max(shares + [5]) * 1.35)
    style_axes(ax)
    save(fig, output_path)


def plot_delay_distribution(trips: list[Trip], output_path: Path, threshold_seconds: int = 180) -> None:
    """Gestapelter Balken pro Linie: Von 100 Fahrten waren so viele früh, pünktlich, spät.

    Nur Fahrten mit Status "ok" werden verwendet.
    """
    by_line = ok_trips_by_line(trips)
    lines = sort_lines(by_line)[::-1]  # von oben nach unten: 2, 5, 12, 31

    fig, ax = plt.subplots(figsize=(9, 1.0 + 0.8 * max(len(lines), 1)))
    for row, line in enumerate(lines):
        counts = [0] * len(DELAY_BANDS)
        for trip in by_line[line]:
            counts[delay_band(trip.delay_seconds, threshold_seconds)] += 1
        total = sum(counts)

        left = 0.0
        for (name, color, text_color), count in zip(DELAY_BANDS, counts):
            width = count / total * 100
            ax.barh(row, width, left=left, height=0.6, color=color, edgecolor="white", linewidth=2,
                    label=name if row == 0 else None)
            if width >= 6:
                ax.text(left + width / 2, row, f"{width:.0f} %", ha="center", va="center",
                        color=text_color, fontsize=9)
            left += width

    ax.set_yticks(range(len(lines)), [f"Linie {line}" for line in lines])
    ax.set_xlim(0, 100)
    ax.set_xticks([])
    for side in ("top", "right", "bottom", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(colors=TEXT_COLOR, length=0)
    ax.set_title("Von 100 Fahrten waren ...", loc="left")
    if lines:
        ax.legend(ncols=len(DELAY_BANDS), loc="upper left", bbox_to_anchor=(0, 0), frameon=False, fontsize=9)
    save(fig, output_path)


def plot_delay_by_hour(trips: list[Trip], output_path: Path, min_trips: int = 20) -> None:
    """Balken pro Stunde: durchschnittliche Verspätung aller Linien zusammen.

    Stunden mit weniger als ``min_trips`` Fahrten werden weggelassen,
    weil der Durchschnitt dort vom Zufall abhängt.
    """
    by_hour = {}
    for line_trips in ok_trips_by_line(trips).values():
        for trip in line_trips:
            by_hour.setdefault(trip.time_planned.hour, []).append(trip.delay_seconds / 60)
    hours = sorted(h for h in by_hour if len(by_hour[h]) >= min_trips)
    means = [sum(by_hour[h]) / len(by_hour[h]) for h in hours]

    fig, ax = plt.subplots(figsize=(9, 4.5))
    colors = ["#c8441b" if m > 0 else "#2a78d6" for m in means]
    ax.bar(hours, means, width=0.7, color=colors)
    ax.axhline(0, color=TEXT_COLOR, linewidth=0.8)

    # Alle Stunden beschriften, damit Stunden ohne genug Daten als Lücke sichtbar bleiben
    ax.set_xlim(-0.6, 23.6)
    ax.set_xticks(range(24), [f"{h}" for h in range(24)])
    ax.set_xlabel(f"Uhrzeit (Stunde); Lücke = weniger als {min_trips} Fahrten gemessen")
    ax.set_ylabel("Ø Minuten (über 0 = zu spät, unter 0 = zu früh)")
    ax.set_title("Zu welcher Uhrzeit sind die Bims am unpünktlichsten? (alle Linien)", loc="left")
    style_axes(ax)
    save(fig, output_path)
