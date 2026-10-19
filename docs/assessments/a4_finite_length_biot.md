# A4: Finite-Length and Small-Biot Guided Study

Tianren Yin · Phys 39, Fall 2026 · individual · due Wednesday 28 October, 9:05 AM
(Moodle PDF `A4_Yin.pdf`).

Required content (Module 7, Part III, "A4 Guided Self-Study"): Problem 1.3, the
stationary fin equation from conservation of energy, Fourier's law, and Newton's law of
cooling, the finite insulated-tip solution and its two boundary conditions, Problem 4.12
(semi-infinite limit), Example 4.8 and Problem 4.20 (tip-boundary approximation), $mL$
and $\epsilon_T(x)$ for each course-rod sensor, $\mathrm{Bi}_{\perp}$, dimensional
checks, and two separate conclusions (length and radius).

## 1. Lienhard Problem 1.3

**Problem.** The heat flux in a 1 cm thick slab is $q$ = 5000 W/m² and the temperature
on the cold side is −40 °C. Tabulate the temperature rise to the hot side for pure
silver, pure aluminum, mild steel (0.5 % carbon), ice, spruce, insulation (85 %
magnesia), and silica aerogel, and indicate which situations would be unreasonable and
why. (Book answer for silver: $\Delta T$ = 0.117 °C.)

**Sample calculation from Fourier's law.** *(to be written: start from
$q = -k\thinspace dT/dx$, state the assumptions, and work one material through with
units.)*

**Results.** $\Delta T = qL/k$ with $qL$ = 50 W/m; $k$ from Lienhard Appendix A
(`python/analysis/a4_problem_1_3.py`):

| Material | $k$ (W/(m K)) | Source (Lienhard) | $\Delta T$ (K) | Hot side (°C) |
| --- | ---: | --- | ---: | ---: |
| Pure silver (99.99+ %) | 427 | Table A.1, 20 °C | 0.117 | −39.88 |
| Pure aluminum | 237 | Table A.1, 20 °C | 0.211 | −39.79 |
| Mild steel (0.5 % carbon) | 54 | Table A.1, 20 °C | 0.926 | −39.07 |
| Ice | 2.215 | Table A.2, 0 °C | 22.6 | −17.4 |
| Spruce | 0.11 | Table A.2, 20 °C | 455 | 415 |
| Insulation (85 % magnesia) | 0.067 | Table A.2, 38 °C | 746 | 706 |
| Silica aerogel | 0.024 | Table A.2, 0 °C | 2083 | 2043 |

The metals use the 20 °C column, as the book's silver answer does. With $k$ interpolated
to −40 °C, silver gives 0.1165 K and aluminum 0.2097 K, a change below 1 %.

**Which situations are unreasonable, and why.** *(to be written.)*

## 2. The stationary fin equation

*(to be written: a slice of length $\Delta x$; axial conduction in and out by Fourier's
law, side loss by Newton's law of cooling, no storage at steady state.)*

## 3. Finite rod with an insulated tip

*(to be written: the two boundary conditions and the solution
$\theta(x)/\theta(0) = \cosh[m(L-x)]/\cosh(mL)$.)*

## 4. Problem 4.12: the semi-infinite limit

*(to be written.)*

## 5. Example 4.8 and Problem 4.20: the tip-boundary approximation

*(to be written.)*

## 6. $mL$ and $\epsilon_T(x)$ at each course-rod sensor

*(to be written once the rod geometry and sensor positions are available; until then
with stated parameter values.)*

## 7. Transverse Biot number

*(to be written: $\mathrm{Bi}_{\perp} = h(A/P)/k = hR/(2k)$ over a justified range of
$h$ and $k$.)*

## 8. Conclusions

- **Length:** *(may the rod be treated as semi-infinite?)*
- **Radius:** *(may it be treated as one-dimensional?)*

## Git checkpoint and AI use

*(commit cited in the PDF; AI use note.)*
