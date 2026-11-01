"""Tests für die Diagramme: es reicht zu prüfen, dass ein PNG entsteht."""

from conftest import t
from tramcheck import charts, models
from tramcheck.analysis import compute_line_stats


def make_trips():
    return [
        models.Trip(
            line=line, stop_id=322, direction="R", time_planned=t(hour, 0),
            final_time_real=None, delay_seconds=delay, status=models.STATUS_OK, observation_count=1,
        )
        for line, hour, delay in [("2", 8, 60), ("2", 9, 300), ("31", 8, -30), ("31", 17, 400)]
    ]


def test_all_charts_write_png_files(tmp_path):
    trips = make_trips()
    stats = compute_line_stats(trips, threshold_seconds=180)

    charts.plot_delayed_share(stats, tmp_path / "a.png", threshold_seconds=180)
    charts.plot_delay_distribution(trips, tmp_path / "b.png")
    charts.plot_delay_by_hour(trips, tmp_path / "c.png")

    for name in ["a.png", "b.png", "c.png"]:
        assert (tmp_path / name).stat().st_size > 0


def test_charts_survive_without_data(tmp_path):
    charts.plot_delayed_share({}, tmp_path / "a.png")
    charts.plot_delay_distribution([], tmp_path / "b.png")
    charts.plot_delay_by_hour([], tmp_path / "c.png")
