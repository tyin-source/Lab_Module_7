# Module 7 rod data

Raw files written by `python/module_07_rod_acquisition_gui.py`. Never edit or overwrite
a raw file; corrections and analysis results go in separate files.

Which file is which:

| File | Role |
| --- | --- |
| `rod_20261111-101158.csv` | **Run 2, the principal stationary-profile run** (all five rod channels; step to 45 °C at 138.6 s) |
| `rod_20261111-111314.csv` | **Room-temperature baseline after Run 2** (TEC off, same wiring); reference for the final analysis |
| `rod_20261111-084156.csv` | Run 1 (A3 and A4 miswired; three valid channels; cross-check) |
| `rod_20261110-*.csv` | First GUI tests and channel checks |
| `rod_20261111-0958*`, `-1001*`, `-1004*` | Wiring checks before Run 2 |
| `rod_20261111-1101*`, `-1104*`, `-1105*`, `-1107*` | TEC off after Run 2, affected by power dropouts (not used) |

The analysis and its exact commands are in `docs/module_notes/module_07_stationary_fin.md`.

- `rod_<YYYYmmdd-HHMMSS>.csv` — every accepted Arduino `DATA` record, exactly as sent.
  A new file starts when the GUI starts and with the "New data file" button.
- `rod_<YYYYmmdd-HHMMSS>_meta.txt` — the matching metadata: serial settings, code files
  and Git commit, channel map with sensor positions, and time-stamped events (control
  start and stop with gains and setpoints, setpoint changes, Arduino restarts, safety
  messages, typed notes).

CSV columns:

| Column | Meaning | Unit |
| --- | --- | --- |
| `time_s` | Arduino time since its last reset | s |
| `tec_C` | TEC-base thermistor (A0), feedback and safety sensor | °C |
| `rod1_C` … `rod5_C` | rod thermistors T1–T5 (A1–A5); positions in the metadata file | °C |
| `pwm` | PWM the Arduino is applying | 0–255 |
| `heat_cool` | 1 = heating, 0 = cooling | — |
| `setpoint_C` | setpoint sent by the GUI under P/PI control, `nan` otherwise | °C |
| `safety` | `OK`, or `SHUTDOWN` while the 60 °C limit holds the TEC off | — |

Temperatures are raw readings. A missing or unplugged rod thermistor reads `nan`.
