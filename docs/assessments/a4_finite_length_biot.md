# A4: Finite-Rod Model and Validity Checks

Tianren Yin · Phys 39, Fall 2026 · A4 (individual, 10 points) · Moodle PDF `A4_Yin.pdf`

- **Date:** November 11, 2026
- **Repository:** <https://github.com/tyin-source/__Lab_Module_7__>
- **Git commit:** `94ede0416ea097463bf811f10fbb121f1848e46b`
- **PDF:** `docs/assessments/a4_latex/A4_Yin.pdf` (REVTeX source `A4_Yin.tex` in the same folder)

Organized under the four headings of the Module 7, Part III handout ("A4: Finite-Rod
Model And Validity Checks"). Parts 3 and 4 are provisional predictions recorded before
heating the rod: they use the measured rod geometry, the planned sensor positions, a
literature range for $k$, and the planning value $h = 10\ \mathrm{W\ m^{-2}K^{-1}}$.

## Part 1. Apply Fourier's law: Lienhard Problem 1.3

### Problem statement

A flat slab of thickness $L=0.01\ \mathrm{m}$ carries a steady heat flux
$q=5000\ \mathrm{W/m^2}$ from its hot side to its cold side. The cold side is held at
$T_c=-40\ ^\circ\mathrm{C}$. For each material in the table, compute the temperature
drop $\Delta T$ across the slab, find the hot-side temperature $T_h=T_c+\Delta T$, and
state whether the case is physically reasonable and why.

### Derivation from Fourier's law

Start from the one-dimensional Fourier law:

$$
q_x=-k\frac{dT}{dx}.
$$

Assumptions:

1. **Steady state** — no time dependence, $\partial T/\partial t=0$;
2. **One-dimensional conduction** — $T=T(x)$ only;
3. **Constant $k$** — thermal conductivity independent of temperature over the range;
4. **No internal heat generation**.

With no source and steady state, the energy balance on a slice gives

$$
\frac{dq_x}{dx}=0
\quad\Longrightarrow\quad
q_x=q=\text{constant}.
$$

Then

$$
\frac{dT}{dx}=-\frac{q}{k}=\text{constant},
$$

so the temperature profile is **linear in $x$**. This linearity is a *result* of the
steady, source-free, constant-$k$ assumptions, not an extra assumption. Integrating from
$x=0$ (hot side) to $x=L$ (cold side):

$$
T(L)-T(0)=-\frac{qL}{k}.
$$

Defining $\Delta T=T_h-T_c=T(0)-T(L)$:

$$
\boxed{\Delta T=\frac{qL}{k}}
\qquad
\boxed{T_h=T_c+\frac{qL}{k}}.
$$

### Unit check

$$
\frac{\mathrm{W/m^2}\cdot\mathrm{m}}{\mathrm{W/(m\cdot K)}}
= \frac{\mathrm{W/m}}{\mathrm{W/(m\cdot K)}}
= \mathrm{K}.
$$

A temperature difference in kelvin equals the same difference in $^\circ\mathrm{C}$, so
$T_h$ can be reported in $^\circ\mathrm{C}$.

### Worked example: silver

For silver, $k=427\ \mathrm{W/(m\cdot K)}$. With $q=5000\ \mathrm{W/m^2}$ and
$L=0.01\ \mathrm{m}$:

$$
\Delta T
= \frac{(5000\ \mathrm{W/m^2})(0.01\ \mathrm{m})}{427\ \mathrm{W/(m\cdot K)}}
= \frac{50}{427}\ \mathrm{K}
\approx 0.117\ \mathrm{K}.
$$

Hence

$$
T_h
= -40\ ^\circ\mathrm{C}+0.117\ \mathrm{K}
\approx -39.88\ ^\circ\mathrm{C}.
$$

The hot side stays far below silver's melting point, and the temperature range is tiny,
so constant-$k$, steady, one-dimensional conduction is an excellent approximation.

### Table calculation for all materials

For every material the same formula applies:

$$
\Delta T=\frac{qL}{k}=\frac{50}{k}\ \mathrm{K},
\qquad
T_h=-40\ ^\circ\mathrm{C}+\Delta T.
$$

| Material | $k$ (W/(m K)) | Source (Lienhard) | $\Delta T$ (K) | $T_h$ (°C) | Reasonable? |
| --- | ---: | --- | ---: | ---: | --- |
| Pure silver (99.99+ %) | 427 | Table A.1, 20 °C | 0.117 | −39.88 | Yes — tiny $\Delta T$, far from any limit |
| Pure aluminum | 237 | Table A.1, 20 °C | 0.211 | −39.79 | Yes — tiny $\Delta T$, far from any limit |
| Mild steel (0.5 % carbon) | 54 | Table A.1, 20 °C | 0.926 | −39.07 | Yes — tiny $\Delta T$, far from any limit |
| Ice | 2.215 | Table A.2, 0 °C | 22.6 | −17.4 | Yes — $T_h<0$ °C, ice stays solid |
| Spruce | 0.11 | Table A.2, 20 °C | 455 | 415 | **No** — wood chars/ignites well below this |
| Insulation (85 % magnesia, *not* MgO) | 0.067 | Table A.2, 38 °C | 746 | 706 | **No** — far above its service limit |
| Silica aerogel | 0.024 | Table A.2, 0 °C | 2083 | 2043 | **No** — above the $\mathrm{SiO_2}$ melting point |

Values from `python/analysis/a4_problem_1_3.py`. The metals use the 20 °C column, as the
book's silver answer does. With $k$ interpolated to −40 °C, silver gives 0.1165 K and
aluminum 0.2097 K, a change below 1 %.

### Which cases are unreasonable, and why

**(a) Compare $T_h$ with each material's physical or service limit.**

- **Ice:** $T_h\approx-17.4\ ^\circ\mathrm{C}$, still below the $0\ ^\circ\mathrm{C}$
  melting point. Ice remains solid — consistent.
- **Spruce:** $T_h\approx415\ ^\circ\mathrm{C}$. Wood chars and ignites roughly around
  $250\text{–}300\ ^\circ\mathrm{C}$, so spruce cannot exist at this temperature.
  **Unreasonable.**
- **85 % magnesia:** $T_h\approx706\ ^\circ\mathrm{C}$. The $k=0.067\ \mathrm{W/(m\cdot K)}$
  entry is **not** "MgO"; Lienhard Table A.2 lists "85 % magnesia" separately from
  "Magnesium oxide, polycrystalline" ($k=48\ \mathrm{W/(m\cdot K)}$). 85 % magnesia is a
  magnesium-carbonate-based pipe insulation with a documented service limit of
  **up to 315 °C**.[^magnesia] The computed hot side is more than twice that limit, so
  this case is **unreasonable**.
- **Aerogel:** $T_h\approx2043\ ^\circ\mathrm{C}$. Silica aerogel is a porous
  $\mathrm{SiO_2}$ network. The melting point of $\mathrm{SiO_2}$ is about
  **1710 °C**,[^sio2-mp] with reported values roughly **1600–1725 °C**.[^sio2-range]
  $2043\ ^\circ\mathrm{C}$ is above the melting point of the solid skeleton itself, which
  is a stronger objection than sintering. **Unreasonable.**

**(b) Is constant $k$ still credible when $\Delta T$ is hundreds or thousands of kelvin?**

For the three metals and ice, $\Delta T$ is at most a few tens of kelvin, so constant $k$
is fine. For spruce, 85 % magnesia, and aerogel, $\Delta T$ is several hundred to over two
thousand kelvin. Over such ranges $k$ is not constant — it varies with temperature, and
for porous insulators radiation across pores adds a strongly temperature-dependent
contribution. The linear profile derived above no longer holds, so the computed $T_h$ is
only a nominal estimate.

The 85 % magnesia entry makes this concrete: Lienhard Table A.2 gives $k=0.067$ at
$38\ ^\circ\mathrm{C}$ and $k=0.08$ at $204\ ^\circ\mathrm{C}$. Even within the material's
rated range, $k$ rises by about 20 %. Extrapolating a single constant $k=0.067$ to
$706\ ^\circ\mathrm{C}$ is therefore not defensible.

**(c) Connection to TEC over-temperature protection.**

A thermoelectric cooler uses the Peltier effect to **pump heat from the cold side to the
hot side**. The element's low $k$ is actually helpful for the cooling function: it reduces
heat conduction back from the hot side to the cold side. The over-temperature risk is
**not** that the element's own $k$ is low; it is on the **heat-rejection path** on the hot
side.

The hot side must reject both the pumped heat and the electrical power through the heat
sink. If the thermal resistance of that path becomes large — a failed fan, poor thermal
contact, a blocked heatsink — the hot-side temperature rise is

$$
\Delta T_{\text{hot side}}\approx \dot Q_{\text{reject}}\ R_{\text{path}}.
$$

This has the **same form** as the slab result $\Delta T=qL/k$: a fixed heat flow through a
large thermal resistance produces a large temperature rise. This is exactly why Module 4
includes a series thermal switch that opens around $70\ ^\circ\mathrm{C}$: it interrupts
the path before the hot side overheats. The slab calculation is a minimal illustration of
the same warning — a large $\Delta T$ can appear when a fixed heat flux is forced through
a high-thermal-resistance path.

[^magnesia]: Asbestos Safety and Eradication Agency (Australia), "85% Magnesia
    insulation," <https://products.asbestossafety.gov.au/insulation/85-magnesia-insulation/>.

[^sio2-mp]: WebElements, "Silicon dioxide,"
    <https://www.webelements.com/compounds/silicon/silicon_dioxide.html>.

[^sio2-range]: Wikipedia, "Silicon dioxide" (archived 13 November 2013),
    <https://eresources.nlb.gov.sg/webarchives/wayback/20131113210036/https://en.wikipedia.org/wiki/Silica>.

## Part 2. Build the stationary finite-rod model

### 2.1 Stationary fin equation

#### Assumptions

1. Steady state: $\partial T/\partial t=0$, so no slice stores energy.
2. No internal heat generation in the rod.
3. $k$, $A$, and $P$ are constant along the rod (a uniform cylinder).
4. $h$ is uniform over the side surface and $T_\infty$ is constant. Radiation is
   neglected or linearized into $h$.
5. Each cross section has a single temperature $T(x)$. This requires a small transverse
   Biot number, $\mathrm{Bi_\perp}=h(A/P)/k\ll1$. For a circular rod,
   $A/P=(\pi d^2/4)/(\pi d)=d/4=r/2$, so $\mathrm{Bi_\perp}=hr/(2k)\ll1$.

#### Energy balance

Take a slice $[x,\ x+\delta x]$:

- Heat conducted in through the left face (**Fourier's law**, $q=-k\ dT/dx$, over the
  area $A$): $-kA\ \dfrac{dT}{dx}\Big|_x$
- Heat conducted out through the right face (**Fourier's law**):
  $-kA\ \dfrac{dT}{dx}\Big|_{x+\delta x}$
- Heat lost from the side (**Newton's law of cooling**, $q=h(T-T_\infty)$, over the side
  area $P\ \delta x$): $hP\ \delta x\ (T-T_\infty)$

**Conservation of energy** for the slice at steady state (no storage, no generation):
setting in − out − side loss = 0 gives

$$
\left(-kA\frac{dT}{dx}\right)_x-\left(-kA\frac{dT}{dx}\right)_{x+\delta x}-hP\ \delta x\ (T-T_\infty)=0
\tag{4.28}
$$

Dividing by $\delta x$ and letting $\delta x\to0$:

$$
kA\ \frac{d^2T}{dx^2}=hP\ (T-T_\infty)
$$

Because $T_\infty$ is constant, $\dfrac{d^2T}{dx^2}=\dfrac{d^2(T-T_\infty)}{dx^2}$. Therefore

$$
\frac{d^2(T-T_\infty)}{dx^2}=m^2\ (T-T_\infty),\qquad m^2=\frac{hP}{kA}
\tag{4.30}
$$

For a circular rod, $m^2=4h/(kd)$.

#### Unit check

Every term in (4.28) has units of W:

- Conduction term: $kA\ \dfrac{dT}{dx}$ has units
  $[\mathrm{W\ m^{-1}K^{-1}}][\mathrm{m^2}][\mathrm{K\ m^{-1}}]=\mathrm{W}$.
- Side-loss term: $hP\ \delta x\ (T-T_\infty)$ has units
  $[\mathrm{W\ m^{-2}K^{-1}}][\mathrm{m}][\mathrm{m}][\mathrm{K}]=\mathrm{W}$.

Both sides of $kA\ d^2T/dx^2=hP\ (T-T_\infty)$ are heat flow per unit length,
$\mathrm{W\ m^{-1}}$:

- Left: $[\mathrm{W\ m^{-1}K^{-1}}][\mathrm{m^2}][\mathrm{K\ m^{-2}}]=\mathrm{W\ m^{-1}}$.
- Right: $[\mathrm{W\ m^{-2}K^{-1}}][\mathrm{m}][\mathrm{K}]=\mathrm{W\ m^{-1}}$.

Both sides of (4.30) have units of $\mathrm{K\ m^{-2}}$:

- The left side is $\mathrm{K\ m^{-2}}$.
- On the right, $m^2$ has units
  $\dfrac{[\mathrm{W\ m^{-2}K^{-1}}][\mathrm{m}]}{[\mathrm{W\ m^{-1}K^{-1}}][\mathrm{m^2}]}=\mathrm{m^{-2}}$,
  and multiplying by K gives $\mathrm{K\ m^{-2}}$.

$1/m$ has units of m and is the decay length. In an infinite rod, $T-T_\infty$ falls to
$1/e$ of its value over each distance $1/m$.

### 2.2 Boundary conditions and their physical meaning

A second-order equation needs two boundary conditions. The course rod uses a Dirichlet
condition at the base and a Neumann condition at the tip.

**Base (Dirichlet):** $T(0)=T_0$. Physically, this fixes the temperature at $x=0$ to a
known value. On the course rod, $x=0$ is the first thermistor hole, and $T_0$ is the
temperature that thermistor measures. It is not the TEC setpoint, because the contact
interface and a length of rod lie between the TEC and the first hole, so the two
temperatures differ. Nor is $x=0$ the physical end of the rod. Choosing this interior
plane as the analysis base is valid because the equation holds for any section of rod
from that plane to the tip.

**Tip (Neumann, adiabatic):** $\dfrac{dT}{dx}\Big|_{x=L}=0$ (4.31b). Physically, no heat
crosses the end face: $\dot Q(L)=-kA\ \dfrac{dT}{dx}\Big|_L=0$. This is an approximation.
The real end face also loses heat by convection, which is described by the Robin
condition (4.31a):

$$
-kA\ \frac{dT}{dx}\Big|_{x=L}=h_L A\ [T(L)-T_\infty]
$$

The approximation is reasonable because the ratio of end-face area to side area is

$$
\frac{\pi d^2/4}{\pi d L}=\frac{d}{4L}\ll1,
$$

so the end face carries only a small fraction of the total heat loss. Part 3 quantifies
the difference between the two solutions (Example 4.8 and Problem 4.20).

### 2.3 Finite insulated-tip solution

#### Nondimensionalization

Let $\Theta=\dfrac{T-T_\infty}{T_0-T_\infty}$ and $\xi=x/L$. Then (4.30) becomes

$$
\frac{d^2\Theta}{d\xi^2}=(mL)^2\ \Theta
\tag{4.34}
$$

The boundary conditions become $\Theta(0)=1$ and
$\dfrac{d\Theta}{d\xi}\Big|_{\xi=1}=0$.

The general solution and its derivative are

$$
\Theta=C_1e^{mL\xi}+C_2e^{-mL\xi},\qquad
\frac{d\Theta}{d\xi}=mL\left(C_1e^{mL\xi}-C_2e^{-mL\xi}\right)
$$

#### Solving for the constants

The base condition gives

$$
C_1+C_2=1
\tag{a}
$$

The tip condition gives

$$
mL\left(C_1e^{mL}-C_2e^{-mL}\right)=0\ \Rightarrow\ C_2=C_1e^{2mL}
\tag{b}
$$

Substituting (b) into (a):

$$
C_1\left(1+e^{2mL}\right)=1\ \Rightarrow
C_1=\frac{1}{1+e^{2mL}}=\frac{e^{-mL}}{e^{-mL}+e^{mL}}=\frac{e^{-mL}}{2\cosh mL}
$$

Returning to (b):

$$
C_2=C_1e^{2mL}=\frac{e^{mL}}{2\cosh mL}
$$

#### Combining into a hyperbolic cosine

$$
\Theta=\frac{e^{-mL}e^{mL\xi}+e^{mL}e^{-mL\xi}}{2\cosh mL}
=\frac{e^{-mL(1-\xi)}+e^{mL(1-\xi)}}{2\cosh mL}
=\frac{\cosh\big[mL(1-\xi)\big]}{\cosh mL}
\tag{4.41}
$$

In dimensional form:

$$
T(x)-T_\infty=(T_0-T_\infty)\ \frac{\cosh\big[m(L-x)\big]}{\cosh mL}
$$

#### Verification

- Differential equation:
  $\dfrac{d^2\Theta}{d\xi^2}=(mL)^2\dfrac{\cosh[mL(1-\xi)]}{\cosh mL}=(mL)^2\Theta$ $\checkmark$
- Base condition: $\Theta(0)=\dfrac{\cosh mL}{\cosh mL}=1$ $\checkmark$
- Tip condition: $\dfrac{d\Theta}{d\xi}=-mL\ \dfrac{\sinh[mL(1-\xi)]}{\cosh mL}$, which at
  $\xi=1$ equals $-mL\ \dfrac{\sinh 0}{\cosh mL}=0$ $\checkmark$

#### Base heat rate and tip temperature

The base heat rate is

$$
\dot Q_0=-kA\frac{dT}{dx}\Big|_0=-\frac{kA(T_0-T_\infty)}{L}\frac{d\Theta}{d\xi}\Big|_0
=kAm\ (T_0-T_\infty)\tanh mL=\sqrt{hPkA}\ (T_0-T_\infty)\tanh mL
$$

Unit check: $\sqrt{hPkA}$ has units
$\sqrt{[\mathrm{W\ m^{-2}K^{-1}}][\mathrm{m}][\mathrm{W\ m^{-1}K^{-1}}][\mathrm{m^2}]}=\mathrm{W\ K^{-1}}$,
and multiplying by K gives W $\checkmark$

The tip temperature is

$$
\Theta(1)=\frac{1}{\cosh mL}
$$

## Part 3. Provisional finite-length prediction

### 3.1 Problem 4.12: the semi-infinite limit

Problem 4.12 asks for Eq. (4.50) from the general solution (4.35), using the boundary
conditions $T(x=0)=T_0$ and $T(x=L)=T_\infty$. The far end is held at room temperature;
it is not insulated. With $\theta=T-T_\infty$, these are $\theta(0)=\theta_0$ and
$\theta(L)=0$, and the fin equation $\theta''=m^2\theta$ has the general solution

$$
\theta=C_1e^{mx}+C_2e^{-mx}.
$$

The two conditions give $C_1+C_2=\theta_0$ and $C_1e^{mL}+C_2e^{-mL}=0$. The second gives
$C_2=-C_1e^{2mL}$; substituting into the first,

$$
C_1=-\frac{\theta_0\ e^{-mL}}{2\sinh mL},
\qquad
C_2=\frac{\theta_0\ e^{mL}}{2\sinh mL},
$$

so

$$
\frac{\theta(x)}{\theta_0}
=\frac{e^{m(L-x)}-e^{-m(L-x)}}{2\sinh mL}
=\frac{\sinh\big[m(L-x)\big]}{\sinh mL}.
$$

This satisfies $\theta(0)/\theta_0=1$ and $\theta(L)=0$. For fixed $x$, write it as

$$
\frac{\theta(x)}{\theta_0}
=e^{-mx}\ \frac{1-e^{-2m(L-x)}}{1-e^{-2mL}}
\ \xrightarrow{\ L\to\infty\ }
e^{-mx},
\tag{4.50}
$$

the semi-infinite profile.

**Physical meaning.** The far-end condition enters only through the factor
$e^{-2m(L-x)}$, which decays exponentially with the distance from the far end measured in
units of $1/m$. A few decay lengths away from the far end, the temperature no longer
depends on what happens there: the insulated tip (Part 2,
$\cosh[m(L-x)]/\cosh mL$) and the room-temperature tip ($\sinh[m(L-x)]/\sinh mL$) both
approach $e^{-mx}$. The far-end condition is effectively forgotten, which is why (4.50) is
a limit of the finite solution rather than a new physical law.

### 3.2 Example 4.8 and Problem 4.20: the tip-boundary approximation

For a convecting tip with coefficient $h_L$, the exact solution (Lienhard Eqs. 4.48 and
4.49) is

$$
\Theta=\frac{\cosh\big[mL(1-\xi)\big]+\dfrac{\mathrm{Bi_{tip}}}{mL}\sinh\big[mL(1-\xi)\big]}
{\cosh mL+\dfrac{\mathrm{Bi_{tip}}}{mL}\sinh mL},
\qquad
\frac{\dot Q_0}{\sqrt{hPkA}\ (T_0-T_\infty)}
=\frac{\tanh mL+h_L/(mk)}{1+\big(h_L/(mk)\big)\tanh mL},
$$

with $\mathrm{Bi_{tip}}=h_LL/k$ (Lienhard's $\mathrm{Bi_{ax}}$) and
$\mathrm{Bi_{tip}}/(mL)=h_L/(mk)$. Setting $h_L\to0$ recovers the insulated-tip
results (4.41) and (4.44).

**Example 4.8.** An aluminum rod with $d=2.0$ cm, $k=205\ \mathrm{W/(m\ K)}$, and
$L=8.0$ cm protrudes from a 150 °C wall into 26 °C air with $h=h_L=120\ \mathrm{W/(m^2\ K)}$. Then $mL=0.8656$, $\mathrm{Bi_{ax}}=0.0468$, and
$h/(mk)=0.0468/0.8656=0.0541$. The exact tip temperature is
$\Theta_{\mathrm{tip}}=0.6886$ ($T_{\mathrm{tip}}=111.4$ °C), while the insulated tip gives
$\Theta_{\mathrm{tip}}=1/\cosh(0.8656)=0.7150$ ($T_{\mathrm{tip}}=114.7$ °C). The insulated
tip overpredicts the tip excess temperature by about 3.8 %.

**Problem 4.20.** With $M=\sqrt{hPkA}\ (T_0-T_\infty)$, an insulated tip gives
$\dot Q_{\mathrm{ins}}=M\tanh(mL)$, and a convecting tip gives

$$
\dot Q_{\mathrm{conv}}
=M\ \frac{\sinh(mL)+\frac{h}{mk}\cosh(mL)}{\cosh(mL)+\frac{h}{mk}\sinh(mL)}.
$$

Numerically,

$$
\frac{\dot Q_{\mathrm{ins}}}{M}=\tanh(0.8656)=0.6992,
\qquad
\frac{\dot Q_{\mathrm{conv}}}{M}
=\frac{\sinh(0.8656)+0.0541\cosh(0.8656)}{\cosh(0.8656)+0.0541\sinh(0.8656)}=0.7258,
$$

so the insulated-tip approximation underpredicts the exact heat flow by

$$
\frac{\dot Q_{\mathrm{conv}}-\dot Q_{\mathrm{ins}}}{\dot Q_{\mathrm{conv}}}
=\frac{0.7258-0.6992}{0.7258}=0.0367,
$$

or **3.67 %**, with the approximate heat flow slightly lower than the exact value.

**Course rod.** The same comparison with $h_L=h=10\ \mathrm{W/(m^2\ K)}$, $k=167\ \mathrm{W/(m\ K)}$, and the inputs of 3.3 gives $mL=1.168$,
$\mathrm{Bi_{tip}}=hL/k=0.0161$, and $h/(mk)=0.0138$, four times smaller than in
Example 4.8:

| Quantity | Insulated tip | Convecting tip | Difference |
| --- | ---: | ---: | ---: |
| $\Theta_{\mathrm{tip}}$ | 0.5671 | 0.5607 | insulated 1.1 % high |
| $\dot Q_0/M$ | 0.8236 | 0.8280 | insulated 0.53 % low |

The insulated-tip boundary condition therefore changes the predicted course-rod profile by
about 1 % at most, at the tip itself.

### 3.3 Inputs

| Input | Value | Source |
| --- | --- | --- |
| Rod diameter $d$ | 12.70 ± 0.02 mm | measured with digital calipers (0.01 mm resolution) |
| Overall rod length | 28.66 ± 0.05 cm | measured with a ruler (1 mm divisions) |
| Hole diameter | 2.50–2.55 mm (mean 2.525 mm) | measured with calipers |
| First-hole offset $s$ | $16.38\ \mathrm{mm}+\tfrac12(2.525\ \mathrm{mm})=17.64$ mm | calipers, from the TEC end of the rod to the near edge of the first hole, plus half the hole diameter to reach its center |
| Analyzed length $L$ | $28.66\ \mathrm{cm}-1.764\ \mathrm{cm}=26.90\pm0.05$ cm | first-hole center to the tip |
| Hole positions $x$ | 0, 1.2, 2.4, 3.7, 5.0, 7.6, 10.2, 15.3, 20.4 cm | measured from the first hole |
| Planned sensors | T1–T5 at $x=0$, 5.0, 10.2, 15.3, 20.4 cm | chosen below |
| Position uncertainty $\delta x$ | ±1.3 mm | half the hole diameter: a sensor can sit anywhere in its hole |
| Side coefficient $h$ | 10 $\mathrm{W/(m^2\ K)}$ | Part III planning value for still room air; not a measurement |
| Conductivity $k$ | 167 W/(m K); range 166–172 W/(m K) | 6061-T6, Lienhard Table A.1: 20 °C value; range from the 0 °C and 100 °C values |
| Error criterion | $\epsilon_T<5$ % at every sensor used | Part III handout's suggested starting criterion |

**Planned sensor positions.** T1–T5 go in the holes at $x=0$, 5.0, 10.2, 15.3, and
20.4 cm. The reasons, using the predictions of 3.4 for $L=26.90$ cm and
$h=10\ \mathrm{W/(m^2\ K)}$:

1. T1 must be at $x=0$: the first hole is the analysis base defined in the handout.
2. The farthest hole, 20.4 cm, is essential. The decay length $1/m\approx23$ cm is longer
   than the measured region, and even there the predicted $\Theta$ is only about 0.59, so
   the whole available range is needed to measure a large enough temperature decay.
3. The points are spread evenly on a plot of $\ln\theta$ against $x$, as the handout asks,
   rather than clustered at one end: the spacings are all about 5 cm, and the predicted
   $\ln\Theta$ values are 0, −0.17, −0.33, −0.45, and −0.53.
4. The set tests the difference between the finite and semi-infinite models: 5.0 cm is the
   last hole that meets the 5 % criterion ($\epsilon_T=4.6$ %), while at 10.2, 15.3, and
   20.4 cm $\epsilon_T$ is 11 %, 20 %, and 30 %, so the two fits should differ visibly in
   their residuals.
5. The holes at 1.2 and 2.4 cm are not used: their 1.2 cm spacing is only about ten times
   the ±1.3 mm position uncertainty, and neighboring points would differ little in
   temperature, adding little information.
6. The farthest sensor still has a large signal: with the base about 25 K above room
   temperature, the predicted excess temperature at 20.4 cm is about 15 K, far above the
   noise.

### 3.4 $m$, $mL$, and $\epsilon_T(x)$ at each planned sensor

For the circular rod, $P/A=4/d$, so

$$
m=\sqrt{\frac{4h}{kd}}
=\sqrt{\frac{4(10\ \mathrm{W\ m^{-2}K^{-1}})}{(167\ \mathrm{W\ m^{-1}K^{-1}})(0.01270\ \mathrm{m})}}
=4.34\ \mathrm{m^{-1}}.
$$

| Quantity | Value |
| --- | ---: |
| $m$ | 4.343 $\mathrm{m^{-1}}$ |
| $1/m$ | 23.0 cm |
| $mL$ | 1.168 |
| $\mathrm{Bi_\parallel}=(mL)^2$ | 1.364 |

Over $k=166$–172 W/(m K), $m=4.279$–4.356 $\mathrm{m^{-1}}$ and $mL=1.151$–1.172; this
range changes the results below by much less than their rounding.

**Error formula.** Dividing the insulated-tip solution by the semi-infinite one,

$$
\frac{\Theta_{\mathrm{finite}}}{\Theta_\infty}
=\frac{\cosh[m(L-x)]}{\cosh(mL)\ e^{-mx}}
=\frac{1+e^{-2m(L-x)}}{1+e^{-2mL}}\ \ge\ 1,
$$

so the insulated tip keeps the rod warmer than the semi-infinite model predicts, and the
difference is largest near the tip. The relative error of the semi-infinite model is
therefore

$$
\epsilon_T(x)
=\frac{\Theta_{\mathrm{finite}}-\Theta_\infty}{\Theta_{\mathrm{finite}}}
=1-\frac{1+e^{-2mL}}{1+e^{-2m(L-x)}},
$$

which increases monotonically from 0 at the base. Setting $\epsilon_T=5$ % gives the
farthest position at which the criterion holds, $x^{\ast}=5.4$ cm.

| Hole $x$ (cm) | $L-x$ (cm) | $\Theta_{\mathrm{finite}}$ | $\Theta_\infty$ | $\epsilon_T$ | $\epsilon_T$ for $x\pm\delta x$ | $\epsilon_T<5$ %? |
| ---: | ---: | ---: | ---: | ---: | ---: | :---: |
| 0.0 | 26.90 | 1.0000 | 1.0000 | 0.00 % | — | yes |
| 1.2 | 25.70 | 0.9584 | 0.9492 | 0.96 % | 0.85–1.07 % | yes |
| 2.4 | 24.50 | 0.9194 | 0.9010 | 2.00 % | 1.89–2.12 % | yes |
| 3.7 | 23.20 | 0.8800 | 0.8516 | 3.23 % | 3.11–3.36 % | yes |
| 5.0 | 21.90 | 0.8434 | 0.8048 | 4.58 % | 4.44–4.71 % | yes |
| 7.6 | 19.30 | 0.7782 | 0.7189 | 7.62 % | 7.46–7.78 % | no |
| 10.2 | 16.70 | 0.7228 | 0.6421 | 11.16 % | 10.98–11.35 % | no |
| 15.3 | 11.60 | 0.6406 | 0.5146 | 19.67 % | 19.44–19.91 % | no |
| 20.4 | 6.50 | 0.5898 | 0.4123 | 30.09 % | 29.82–30.37 % | no |

For the planned sensors (with an illustrative base excess temperature
$\theta_0=25$ K):

| Sensor | $x$ (cm) | $\Theta_{\mathrm{finite}}$ | $\ln\Theta_{\mathrm{finite}}$ | $\theta$ (K) | $\epsilon_T$ |
| --- | ---: | ---: | ---: | ---: | ---: |
| T1 | 0.0 | 1.0000 | 0.000 | 25.0 | 0.00 % |
| T2 | 5.0 | 0.8434 | −0.170 | 21.1 | 4.58 % |
| T3 | 10.2 | 0.7228 | −0.325 | 18.1 | 11.16 % |
| T4 | 15.3 | 0.6406 | −0.445 | 16.0 | 19.67 % |
| T5 | 20.4 | 0.5898 | −0.528 | 14.7 | 30.09 % |

Values from `python/analysis/a4_part3_finite_length.py`.

Because $h$ is only a planning value, the script also varies it at $k=167$ W/(m K):

| $h$ ($\mathrm{W/(m^2\ K)}$) | $1/m$ (cm) | $mL$ | $x^{\ast}$ (cm) |
| ---: | ---: | ---: | ---: |
| 5 | 32.6 | 0.826 | 4.6 |
| 10 | 23.0 | 1.168 | 5.4 |
| 15 | 18.8 | 1.431 | 6.4 |
| 20 | 16.3 | 1.652 | 7.4 |

### 3.5 Prediction: length

With the criterion $\epsilon_T<5$ % at every sensor used, the semi-infinite model is
adequate at T1 ($x=0$) and T2 (5.0 cm, $\epsilon_T=4.6$ %, still below 5 % at the edge
of the ±1.3 mm position uncertainty), but not at T3, T4, and T5 (10.2, 15.3, and 20.4 cm),
where $\epsilon_T$ is 11 %, 20 %, and 30 %. Among all the holes, only those at
$x\le5.0$ cm meet the criterion ($x^{\ast}=5.4$ cm). The whole rod is far from the
"infinitely long" regime: $mL=1.17$, compared with Lienhard's guideline $mL\gtrsim5$.

Three of the five planned sensors lie beyond $x^{\ast}$, so I expect the course rod **not** to
be adequately semi-infinite over the measured region.
The stationary profile should be analyzed with the finite insulated-tip model; the
semi-infinite fit is a comparison that should show a systematic residual at the far
sensors. The tip boundary condition itself matters much less: replacing the insulated tip
by a convecting one changes the prediction by about 1 % (3.2).

This prediction depends on the planned sensor positions and $L=26.90$ cm in 3.3,
$h=10\ \mathrm{W/(m^2\ K)}$, $k=166$–172 W/(m K), and the 5 % criterion. It is not
sensitive to $k$. For any $h$ from 5 to 20 $\mathrm{W/(m^2\ K)}$, $x^{\ast}$ stays between 4.6
and 7.4 cm, so T3, T4, and T5 fail in every case. Only T2 at 5.0 cm is marginal: it passes for $h\ge10\ \mathrm{W/(m^2\ K)}$ but fails if $h$ is as low as
5 $\mathrm{W/(m^2\ K)}$.

## Part 4. Provisional one-dimensional prediction

### 4.1 Transverse Biot number

#### Definition and meaning

The transverse (radial) Biot number is defined as (Lienhard Eq. 4.27)

$$
\mathrm{Bi_\perp}=\frac{h(A/P)}{k},
$$

where $A/P$, the cross-sectional area divided by the perimeter, is the characteristic
length for conduction across the section. It represents the ratio of the internal radial
conduction resistance to the external surface convection resistance:

$$
\mathrm{Bi_\perp}\sim\frac{R_{\mathrm{radial\ conduction}}}{R_{\mathrm{surface\ convection}}}.
$$

#### Form for a cylindrical rod

For a rod of diameter $d$,

$$
\frac{A}{P}=\frac{\pi d^2/4}{\pi d}=\frac{d}{4},
$$

so

$$
\boxed{\mathrm{Bi_\perp}=\frac{hd}{4k}}.
$$

#### Numerical value and unit check

Using $h=10\ \mathrm{W/(m^2\ K)}$, $d=0.01270$ m, and $k=167$ W/(m K):

$$
\mathrm{Bi_\perp}=\frac{(10)(0.01270)}{4(167)}=1.90\times10^{-4}.
$$

If $k$ is taken from Lienhard's range of 166–172 W/(m K), then
$\mathrm{Bi_\perp}=1.85\times10^{-4}$ to $1.91\times10^{-4}$. Units:

$$
\frac{[\mathrm{W\ m^{-2}\ K^{-1}}][\mathrm{m}]}{[\mathrm{W\ m^{-1}\ K^{-1}}]}=1,
$$

so $\mathrm{Bi_\perp}$ is dimensionless.

#### Conversion to a temperature difference

The temperature difference between the center of the cross section and its surface is
approximately

$$
\Delta T_{\mathrm{center-surface}}\approx\mathrm{Bi_\perp}\ \theta,
$$

where $\theta$ is the temperature difference between the rod surface and the ambient air.
With the illustrative $\theta\approx25$ K of 3.4,

$$
\Delta T\approx(2\times10^{-4})(25\ \mathrm{K})\approx0.005\ \mathrm{K},
$$

about ten times smaller than the scatter of single thermistor readings (standard
deviation 0.03–0.05 °C in the stationary interval of the rod runs).

#### Inverse calculation: what $h$ would break the radial lumped assumption?

Setting $\mathrm{Bi_\perp}=0.1$:

$$
h=\frac{0.4k}{d}=\frac{0.4(167)}{0.0127}\approx5300\ \mathrm{W/(m^2\ K)}.
$$

Lienhard Table 1.1 (p. 21) lists 4.2–29 W/(m² K) for natural convection in air and
45–80 W/(m² K) for forced convection of air. The value 5300 W/(m² K) is about 500 times
the planning value and still about 65 times the largest forced-air value. Under the
experimental conditions, the assumption of radial temperature uniformity is therefore
very robust.

### 4.2 Prediction: radius

#### Criterion

Lienhard (p. 24): the lumped-capacity solution is normally accurate within about 3 % if
$\mathrm{Bi}<0.1$.

#### Conclusion

For this rod, $\mathrm{Bi_\perp}\approx2\times10^{-4}\ll0.1$. Therefore each cross section
can be represented by a single temperature $T(x)$. This conclusion depends on

$$
h=10\ \mathrm{W/(m^2\ K)},\qquad k=166\text{–}172\ \mathrm{W/(m\ K)},\qquad d=12.70\ \mathrm{mm}.
$$

#### Distinction from 3.4 and 3.5

$\mathrm{Bi_\perp}$ answers the approximation question in the **radial** direction;
$\mathrm{Bi_\parallel}=(mL)^2$ in 3.4 and the prediction in 3.5 answer it in the
**length** direction. They are independent: for this rod $\mathrm{Bi_\perp}$ is very
small, but $(mL)^2=1.36$ is not. The temperature is uniform across each section, yet it
still decays noticeably along the rod.

#### Status of this prediction

This is a prediction made *before* heating. After $m$ is fitted, the self-consistency
check

$$
\mathrm{Bi_\perp}=\left(\frac{md}{4}\right)^2
$$

will confirm whether the experimentally extracted $m$ is consistent with a small
$\mathrm{Bi_\perp}$.

### 4.3 Application: heat sink in still and forced air

#### Larger $h$ in forced air

Forced airflow continuously sweeps away the heated air near the surface, thinning the
thermal boundary layer, and thus significantly increases the convective heat transfer
coefficient $h$. Lienhard Table 1.1 gives 4.2–29 W/(m² K) for natural convection in air
and 45–80 W/(m² K) for forced convection of air (illustrative values; the actual $h$
depends on velocity and geometry).

#### Relation between the decay length $1/m$ and $h$

From $m=\sqrt{hP/(kA)}$,

$$
\frac{1}{m}=\sqrt{\frac{kA}{hP}}=\sqrt{\frac{kd}{4h}}\propto h^{-1/2}.
$$

With $k=167$ W/(m K) and $d=0.01270$ m:

| $h$ ($\mathrm{W/(m^2\ K)}$) | $1/m$ (cm) |
| ---: | ---: |
| 5 | 32.6 |
| 10 | 23.0 |
| 15 | 18.8 |
| 20 | 16.3 |

When $h$ is quadrupled, $1/m$ is halved. The forced-air heat sink therefore has the
shorter decay length.

#### Physical meaning

A shorter decay length means that heat leaves through the sides before it can travel far
along the fin, so the far end of the fin is closer to the ambient air temperature. The
total heat dissipation,

$$
\dot Q_0=\sqrt{hPkA}\ \theta_0\tanh(mL),
$$

still increases with $h$. $\mathrm{Bi_\perp}\propto h$ also increases with $h$, but it
remains $\ll1$ in air.

## Git checkpoint and AI use

The PDF is built from commit `94ede0416ea097463bf811f10fbb121f1848e46b` of
<https://github.com/tyin-source/__Lab_Module_7__>; the LaTeX source is
`docs/assessments/a4_latex/A4_Yin.tex`.

- **Part 1:** The derivation, the reasonableness discussion, and the choice of references
  are my own. Claude Code (an AI coding assistant) wrote `python/analysis/a4_problem_1_3.py`,
  which computes the table from the Lienhard Table A.1 and A.2 values, reviewed my drafts,
  and formatted the references.

- **Part 2:** The calculations are my own. Claude Code (an AI coding assistant) organized
  and formatted this part: it wrote a first draft for comparison, reviewed my version, and
  fixed its LaTeX formatting.
- **Part 3:** The Problem 4.12 derivation, the Example 4.8 and Problem 4.20
  calculations, and the choice of sensor holes with its reasons are my own. The
  course-rod numbers in 3.2–3.4 ($m$, $mL$, $\epsilon_T$ at each hole, $x^{\ast}$, the
  planned-sensor table, the tip comparison, and the $h$ sensitivity) were computed by
  `python/analysis/a4_part3_finite_length.py`, which Claude Code wrote from my
  measurements; I checked $m$, $mL$, and $\epsilon_T$ at 7.6 cm by hand. Claude Code also
  organized and formatted Part 3: it made the tables,
  translated my notes into English, and drafted the text of 3.4 and 3.5.
- **Part 4:** The text and calculations are my own. Claude Code (an AI coding assistant) checked the numbers
  and the Lienhard citations against the textbook, corrected the page of the 3 % statement
  (p. 24), the "two orders of magnitude" comparison, and the reading-noise value (now the
  measured scatter), and converted the math to GitHub format.
- **This PDF:** Claude Code converted the repository Markdown to the REVTeX document and
  drafted its abstract.
