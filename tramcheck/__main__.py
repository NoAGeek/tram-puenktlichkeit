"""Einstiegspunkt: ``python -m tramcheck <befehl>``.

Befehle:
    collect      Daten sammeln (läuft endlos, beenden mit Strg+C)
                 --minutes N --database PFAD: so nutzt es GitHub Actions
    build-trips  Rohdaten aus data/raw/ übernehmen, dann Fahrten neu berechnen
    report       Kennzahlen ausgeben und Diagramme speichern
"""

import argparse
from pathlib import Path

from tramcheck import analysis, charts, collector, storage, trips
from tramcheck.config import load_config


def cmd_collect(config, args) -> None:
    collector.setup_logging(config.log_path)
    database_path = Path(args.database) if args.database else None
    collector.run_forever(config, database_path=database_path, max_minutes=args.minutes)


def cmd_build_trips(config, args) -> None:
    conn = storage.connect(config.database_path)
    raw_files = sorted(config.raw_dir.glob("*.db"))
    imported = sum(storage.import_database(conn, path) for path in raw_files)
    print(f"{len(raw_files)} Rohdaten-Dateien geprüft, {imported} neue Abfragen übernommen.")

    observations = storage.load_observations(conn)
    poll_times = storage.load_successful_poll_times(conn)
    new_trips = trips.build_trips(observations, poll_times)
    storage.replace_trips(conn, new_trips)
    print(f"{len(new_trips)} Fahrten berechnet.")


def cmd_report(config, args) -> None:
    conn = storage.connect(config.database_path)
    all_trips = storage.load_trips(conn)
    stats = analysis.compute_line_stats(all_trips, config.delay_threshold_seconds)
    for line in charts.sort_lines(stats):
        s = stats[line]
        share = f"{s.delayed_share * 100:.1f} %" if s.delayed_share is not None else "-"
        mean = f"{s.mean_delay_seconds / 60:+.1f} min" if s.mean_delay_seconds is not None else "-"
        print(
            f"Linie {line:>2}: {s.trips_evaluated:>5} ausgewertet, verspätet {share:>7}, "
            f"Schnitt {mean:>9} | ohne Echtzeit {s.trips_without_realtime}, unsicher {s.trips_unsure}"
        )

    config.chart_dir.mkdir(parents=True, exist_ok=True)
    charts.plot_delayed_share(stats, config.chart_dir / "anteil_verspaetet.png", config.delay_threshold_seconds)
    charts.plot_delay_distribution(all_trips, config.chart_dir / "verteilung.png", config.delay_threshold_seconds)
    charts.plot_delay_by_hour(all_trips, config.chart_dir / "nach_uhrzeit.png")
    print(f"Diagramme gespeichert in {config.chart_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="tramcheck", description="Pünktlichkeit Wiener Straßenbahnen")
    parser.add_argument("command", choices=["collect", "build-trips", "report"])
    parser.add_argument("--config", default="config.toml", help="Pfad zur Config-Datei")
    parser.add_argument("--minutes", type=float, help="collect: nach so vielen Minuten aufhören")
    parser.add_argument("--database", help="collect: in diese Datenbank statt der aus der Config schreiben")
    args = parser.parse_args()

    config = load_config(args.config)
    commands = {"collect": cmd_collect, "build-trips": cmd_build_trips, "report": cmd_report}
    commands[args.command](config, args)


if __name__ == "__main__":
    main()
