# Phys 39 Lab: Thermal Transport and the Rod Instrument (Module 7)

Module 7 moves from the lumped TEC models of Module 6 to the aluminum rod, whose
temperature depends on position and time, $T(x,t)$. Part I covers Fourier's law, the heat
equation, and the Biot number; Part II the finite and semi-infinite fin solutions; Part III
the rod instrument, step response, and stationary profile (S16–S17).

## Contents

| Path | What it is |
| --- | --- |
| `docs/assessments/a4_finite_length_biot.md` | A4 (individual): finite-rod model and validity checks |
| `docs/assessments/a4_latex/A4_Yin.tex`, `A4_Yin.pdf` | A4 as a REVTeX (PRL style) document and the submitted PDF |
| `docs/theory/theory_bridge_chapter_1_notes.md` | Part I reading questions and dimensional equation sheet |
| `python/analysis/a4_problem_1_3.py` | A4 Part 1: Lienhard Problem 1.3 (temperature rise across a slab) |
| `python/analysis/a4_part3_finite_length.py` | A4 Part 3: m, mL, and the finite vs semi-infinite error at each hole; tip-condition and h checks; Bi_perp for Part 4 |
| `arduino/module_07_rod_controller/module_07_rod_controller.ino` | Part III: six-thermistor acquisition (A0 TEC, A1–A5 rod), one `DATA` record per second, TEC safety limit and command timeout from Module 6 |
| `python/module_07_rod_acquisition_gui.py` | Part III: six-trace display, Module 6 P/PI control on the TEC thermistor, raw CSV and metadata file per run |
| `python/module_07_gui_selftest.py` | Offline test of the GUI against a simulated Arduino |
| `python/module_07_common.py` | Shared paths, `DATA` columns, and the raw-CSV reader |
| `python/analysis/module_07_sensor_map_diagram.py` | Draws the sensor-map diagram `docs/figures/module_07/rod_sensor_map_diagram.png` |
| `python/analysis/module_07_stationary_fit.py` | Phase 5: steady-state check, finite and semi-infinite fits, residuals, $m$, $1/m$, $\mathrm{Bi_\perp}$, $\epsilon_T$ |
| `docs/module_notes/module_07_rod_instrument.md` | Sensor map, geometry, checks, common-bath record, prediction record, run log |
| `docs/module_notes/module_07_stationary_fin.md` | Phase 5 analysis record (formative) |
| `data/module_07/` | Raw rod runs (see its README); figures go in `docs/figures/module_07/` |

## How to run

```bash
pip install -r requirements.txt
python python/analysis/a4_problem_1_3.py
python python/analysis/a4_part3_finite_length.py
cd docs/assessments/a4_latex && pdflatex A4_Yin.tex && pdflatex A4_Yin.tex && cd -   # A4 PDF

# Part III (set SERIAL_PORT at the top of the GUI first)
python python/module_07_rod_acquisition_gui.py
python python/module_07_gui_selftest.py          # no hardware needed
python python/analysis/module_07_stationary_fit.py data/module_07/<run>.csv --baseline <start>,<end>

# Final Phase 5 result (Run 2 with the room baseline recorded after it)
python python/analysis/module_07_stationary_fit.py data/module_07/rod_20261111-101158.csv \
    --baseline 534,834 --baseline-file data/module_07/rod_20261111-111314.csv --t-end 2230
```

Add `--positions-cm` with the hole of each `rod1_C`…`rod5_C` column, and `--exclude T3,T4`
to leave faulty channels out of the fits (Run 1 used both; see
`docs/module_notes/module_07_stationary_fin.md`).

Upload `arduino/module_07_rod_controller/module_07_rod_controller.ino` with the Arduino
IDE (the six divider resistors are 100 kΩ within ±1 %, so `SERIES_RESISTOR_OHM` keeps
the nominal value).

## AI use note

Claude Code (an AI coding assistant) set up this repository's structure, wrote
`python/analysis/a4_problem_1_3.py` with the conductivities looked up in Lienhard
Appendix A, wrote `python/analysis/a4_part3_finite_length.py`, and drafted the outlines of
the A4 and Part I notes. For Part III it wrote the Module 7 Arduino sketch and Python GUI
as extensions of my Module 6 code, the GUI self-test, the stationary-fit script, and the
templates of the two Module 7 notes; the sketch was compiled and exercised on a computer
with a stand-in for the Arduino library, and the GUI was tested off screen against a
simulated Arduino before both were run on our hardware (runs in `data/module_07/`). It
also ran the Phase 5 fits, made the figures, and wrote the numerical records in the two
Module 7 notes; the interpretive sections of `module_07_stationary_fin.md` (1, 7, 8),
the A4 text, and the reading-question answers are my own and were checked and formatted by
Claude Code. The A4 file's own AI-use section lists what it contributed to each part.
