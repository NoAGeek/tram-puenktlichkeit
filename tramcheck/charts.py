"""Diagramme mit matplotlib.  [Mo]

Alle Funktionen speichern ein PNG und zeigen nichts am Bildschirm an.
So läuft das auch auf einem Rechner ohne Bildschirm (z. B. Raspberry Pi).
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # ohne Bildschirm zeichnen, nur in Dateien
import matplotlib.pyplot as plt  # noqa: E402

from tramcheck.analysis import LineStats  # noqa: E402
from tramcheck.models import Trip  # noqa: E402


def plot_delayed_share(stats: dict[str, LineStats], output_path: Path) -> None:
    """Balkendiagramm: Anteil verspäteter Fahrten pro Linie (in Prozent).

    TODO (Mo):
        - ``fig, ax = plt.subplots()``
        - ``ax.bar(linien, prozente)``, Achsen beschriften, Titel setzen
        - Schwellenwert im Titel nennen, z. B. "verspätet = mehr als 3 min"
        - ``fig.savefig(output_path)`` und danach ``plt.close(fig)``
          (sonst wird bei vielen Diagrammen der Speicher voll)
    """
    raise NotImplementedError("TODO Mo: plot_delayed_share")


def plot_delay_distribution(trips: list[Trip], output_path: Path) -> None:
    """Boxplot: Verteilung der Verspätung (in Minuten) pro Linie.

    Nur Fahrten mit Status "ok" verwenden.

    TODO (Mo): ``ax.boxplot(...)`` mit einer Liste von Verspätungen pro Linie.
    """
    raise NotImplementedError("TODO Mo: plot_delay_distribution")


def plot_delay_by_hour(trips: list[Trip], output_path: Path) -> None:
    """Optional: durchschnittliche Verspätung nach Tageszeit (Stunde 0–23).

    TODO (Mo, optional): pro Linie eine Linie im Diagramm,
        x = Stunde von ``trip.time_planned``, y = mittlere Verspätung.
    """
    raise NotImplementedError("TODO Mo (optional): plot_delay_by_hour")
