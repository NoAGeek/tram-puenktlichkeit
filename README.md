# Straßenbahn-Pünktlichkeit rund um die FH Technikum Wien

Wir messen, wie oft vier Wiener Straßenbahnlinien verspätet sind. Ein Python-Programm fragt
über Tage bis Wochen jede Minute den Echtzeit-Monitor der Wiener Linien ab, speichert die
Abfahrten in SQLite und wertet sie danach aus.

| Linie | Haltestelle      | stopId | Richtung              |
|-------|------------------|--------|-----------------------|
| 2     | Höchstädtplatz   | 322    | Dornbach              |
| 31    | Höchstädtplatz   | 322    | Schottenring U        |
| 12    | Höchstädtplatz   | 319    | Josefstädter Straße U |
| 5     | Wallensteinplatz | 350    | Westbahnhof S U       |

Alle Linien fahren Richtung Zentrum. Die Linie 33 ist eingestellt und wird nicht verwendet.
Die stopIds stammen aus der offiziellen Liste
[`wienerlinien-ogd-haltepunkte.csv`](https://www.wienerlinien.at/ogd_realtime/doku/ogd/wienerlinien-ogd-haltepunkte.csv)
und wurden am 28.10.2026 mit echten Abfragen geprüft. Alle vier liefern Echtzeitdaten.

## Setup

Voraussetzung: **Python 3.11 oder neuer** (`python --version`).

```powershell
# 1. Virtuelle Umgebung anlegen und aktivieren
python -m venv .venv
.venv\Scripts\Activate.ps1          # macOS/Linux: source .venv/bin/activate

# 2. Bibliotheken installieren
pip install -r requirements.txt

# 3. Tests laufen lassen
pytest
```

Falls PowerShell das Aktivieren blockiert: einmalig
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` ausführen.

## Benutzung

```powershell
python -m tramcheck collect       # Daten sammeln (endlos, Strg+C zum Beenden)
python -m tramcheck build-trips   # Fahrten aus den Rohdaten berechnen
python -m tramcheck report        # Kennzahlen + Diagramme in data/charts/
```

Alle Einstellungen (Intervall, Schwellenwert, Linien) stehen in `config.toml`.

## Aufbau

```
tramcheck/
  models.py      Departure + Trip: Schnittstelle zwischen Omar und Mo  (gemeinsam)
  config.py      liest config.toml                                     (gemeinsam, fertig)
  api_client.py  HTTP-Abfrage, fängt alle Fehler ab                    (Omar)
  parser.py      JSON -> list[Departure]                               (Omar)
  collector.py   Schleife: abfragen -> parsen -> speichern             (Omar)
  storage.py     SQLite: polls, observations, trips                    (Mo)
  trips.py       Beobachtungen -> Fahrten mit endgültiger Verspätung   (Mo)
  analysis.py    Kennzahlen pro Linie                                  (Mo)
  charts.py      matplotlib-Diagramme                                  (Mo)
tests/
  fixtures/      echte API-Antworten vom 28.10.2026 + Sonderfälle
```

Datenfluss:

```
API -> api_client -> parser -> list[Departure] -> storage (polls + observations)
                                                       |
                                  build-trips:  trips.build_trips -> storage (trips)
                                                       |
                                  report:       analysis -> charts -> PNG
```

## Wer macht was

Die Grenze zwischen uns ist `models.py`: Omar liefert eine `list[Departure]`, Mo nimmt sie
entgegen. Dadurch kann jeder für sich arbeiten und testen, ohne auf den anderen zu warten.

### Omar: Datenabruf von der API

| Datei | Funktion | Test (`@todo` löschen, wenn fertig) |
|---|---|---|
| `parser.py` | [ ] `is_wanted` | über `test_parse_monitor_*` |
| `parser.py` | [ ] `parse_monitor` | `test_parser.py`: 5 Tests |
| `api_client.py` | [ ] `is_valid_response` | `test_empty_response_is_not_valid` |
| `api_client.py` | [ ] `fetch_monitor` | eigenen Test schreiben (mit `unittest.mock`) |
| `collector.py` | [ ] `poll_once` | erst wenn `storage.save_poll` von Mo fertig ist |
| `collector.py` | [ ] `run_forever` | per Hand: `python -m tramcheck collect` |

Empfohlene Reihenfolge: `parser.py` zuerst (geht komplett mit den Fixtures, ohne Internet).

### Mo: Speicherung, Statistik und Diagramme

| Datei | Funktion | Test (`@todo` löschen, wenn fertig) |
|---|---|---|
| `trips.py` | [ ] `group_by_trip` | eigenen Test schreiben |
| `trips.py` | [ ] `has_disappeared` | über `test_trip_is_unsure_*` |
| `trips.py` | [ ] `build_trip` | `test_trips.py`: 4 Tests |
| `trips.py` | [ ] `build_trips` | eigenen Test schreiben |
| `storage.py` | [ ] `save_poll`, `load_observations`, `load_successful_poll_times` | `test_storage.py`: 2 Tests |
| `storage.py` | [ ] `replace_trips`, `load_trips` | eigenen Test schreiben |
| `analysis.py` | [ ] `compute_line_stats` | `test_line_stats_counts_only_ok_trips` |
| `charts.py` | [ ] `plot_delayed_share`, `plot_delay_distribution` | per Hand: PNG anschauen |
| `charts.py` | [ ] `plot_delay_by_hour` (optional) | per Hand |

Empfohlene Reihenfolge: `trips.py` zuerst (das ist das fachliche Herzstück und geht ganz
ohne Datenbank und API).

### Gemeinsam

- [ ] `models.py` und `config.toml` gemeinsam durchgehen, danach nur noch gemeinsam ändern
- [ ] Sammeln starten, sobald Omars Teil und `storage.save_poll` fertig sind (je früher, desto mehr Daten!)
- [ ] Am Ende: `build-trips` + `report` laufen lassen und Ergebnisse gemeinsam interpretieren

## Fachliche Regeln

- `timeReal` ist eine **Prognose**. Darum fragen wir jede Minute ab und verfolgen jede Fahrt.
- Eine Fahrt erkennen wir an **Linie + Haltestelle + Richtung + geplanter Abfahrtszeit**.
- Die **endgültige Verspätung** ist der letzte `timeReal`-Wert, bevor die Fahrt aus dem Monitor verschwindet.
- **Verspätet** heißt mehr als `delay_threshold_seconds` (180 s = 3 min) zu spät. Verfrühte Fahrten gelten als pünktlich.
- Fahrten ohne `timeReal` (`no_realtime`), mit `realtimeSupported: false` (`not_supported`)
  und Fahrten, die nur wegen einer Datenlücke verschwunden sind (`unsure`), werden
  gekennzeichnet und **nicht** als pünktlich gezählt.
- Die Rohdaten (`observations`) werden nie verändert. Die Tabelle `trips` kann jederzeit
  mit `build-trips` neu berechnet werden.

## So arbeitet ihr am Gerüst weiter

1. Funktionen mit `raise NotImplementedError("TODO ...")` sind eure Aufgaben. Im Docstring
   steht jeweils, was sie tun sollen, und Tipps zum Vorgehen.
2. Zu fast jeder TODO-Funktion gibt es schon einen Test, der mit `@todo` markiert ist und
   deshalb übersprungen wird. Wenn ihr eine Funktion fertig habt: `@todo` darüber löschen
   und `pytest` laufen lassen.
3. `models.py` nur gemeinsam ändern.
4. Die Tests rufen nie die echte API auf. Neue Sonderfälle als JSON nach `tests/fixtures/` legen.

## Langzeitbetrieb

Zum Sammeln braucht ihr ein Gerät, das Tage bis Wochen durchläuft und **nicht in den
Ruhemodus geht** (Desktop-PC, Raspberry Pi, Server). Fehler wie Timeouts oder leere Antworten
landen in `data/collector.log` und beenden das Programm nicht.

## Datenquelle

Echtzeitdaten: Wiener Linien, [Open Government Data](https://www.data.gv.at/katalog/dataset/wiener-linien-echtzeitdaten-via-datendrehscheibe-wien),
Lizenz CC BY 4.0.
