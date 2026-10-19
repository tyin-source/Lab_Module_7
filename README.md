# Phys 39 Lab: Thermal Transport and the Rod Instrument (Module 7)

Module 7 moves from the lumped TEC models of Module 6 to the aluminum rod, whose
temperature depends on position and time, $T(x,t)$. Part I covers Fourier's law, the heat
equation, and the Biot number; Part II the finite and semi-infinite fin solutions; Part III
the rod instrument, step response, and stationary profile (S16–S17).

## Contents

| Path | What it is |
| --- | --- |
| `docs/assessments/a4_finite_length_biot.md` | A4 (individual): finite-length and small-Biot guided study |
| `docs/theory/theory_bridge_chapter_1_notes.md` | Part I reading questions and dimensional equation sheet |
| `python/analysis/a4_problem_1_3.py` | A4 Part I: Lienhard Problem 1.3 (temperature rise across a slab) |

Rod data, figures, and notes will go in `data/module_08/`, `docs/figures/module_08/`,
`docs/module_notes/module_08_rod_instrument.md`, and
`docs/module_notes/module_08_stationary_fin.md`, the names the Part III handout uses.

## How to run

```bash
pip install -r requirements.txt
python python/analysis/a4_problem_1_3.py
```

