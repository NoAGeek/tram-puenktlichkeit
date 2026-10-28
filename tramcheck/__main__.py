"""Einstiegspunkt: ``python -m tramcheck <befehl>``.

Befehle:
    collect      Daten sammeln (läuft endlos, beenden mit Strg+C)
    build-trips  Fahrten aus den Rohdaten neu berechnen
    report       Kennzahlen ausgeben und Diagramme speichern
"""

import argparse

from tramcheck import analysis, charts, collector, storage, trips
from tramcheck.config import load_config


def cmd_collect(config) -> None:
    collector.setup_logging(config.log_path)
    collector.run_forever(config)


def cmd_build_trips(config) -> None:
    conn = storage.connect(config.database_path)
    observations = storage.load_observations(conn)
    poll_times = storage.load_successful_poll_times(conn)
    new_trips = trips.build_trips(observations, poll_times)
    storage.replace_trips(conn, new_trips)
    print(f"{len(new_trips)} Fahrten berechnet.")


def cmd_report(config) -> None:
    conn = storage.connect(config.database_path)
    all_trips = storage.load_trips(conn)
    stats = analysis.compute_line_stats(all_trips, config.delay_threshold_seconds)
    for line, s in stats.items():
        print(f"Linie {line}: {s}")

    config.chart_dir.mkdir(parents=True, exist_ok=True)
    charts.plot_delayed_share(stats, config.chart_dir / "anteil_verspaetet.png")
    charts.plot_delay_distribution(all_trips, config.chart_dir / "verteilung.png")
    print(f"Diagramme gespeichert in {config.chart_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="tramcheck", description="Pünktlichkeit Wiener Straßenbahnen")
    parser.add_argument("command", choices=["collect", "build-trips", "report"])
    parser.add_argument("--config", default="config.toml", help="Pfad zur Config-Datei")
    args = parser.parse_args()

    config = load_config(args.config)
    commands = {"collect": cmd_collect, "build-trips": cmd_build_trips, "report": cmd_report}
    commands[args.command](config)


if __name__ == "__main__":
    main()
