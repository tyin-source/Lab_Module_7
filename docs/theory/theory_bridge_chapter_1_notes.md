# Module 7, Part I: Thermal Transport Foundations — Notes

Short answers to the Part I reading questions (Lienhard Section 1.3, pp. 11–26) and a
dimensional equation sheet, kept for A4, the C5 oral check, and A5.

## Reading questions

Page numbers are the printed page numbers of Lienhard, 6th ed. (PDF page − 14).

### 1. Why is Fourier's law a phenomenological constitutive law, and what does its minus sign say about the direction of heat flow? (pp. 11–13, Eqs. 1.8–1.9)

**Phenomenological and constitutive.** Fourier's law is a **constitutive law** because it
describes how a specific material responds to a driving force (a temperature gradient). It
is **phenomenological** because it is stated as an empirical law based on macroscopic
physical observation ("'Experience'—that is, physical observation", p. 50), rather than
being derived from first principles such as molecular dynamics. The constant of
proportionality, the thermal conductivity $k$, must be measured experimentally.

**The minus sign.** In $q=-k\ dT/dx$ (Eq. 1.8), the minus sign indicates that the heat flux
$q$ points in the direction opposite to the temperature gradient: heat flows spontaneously
from higher to lower temperature.

### 2. Distinguish $T$, $\dot Q_x$, and $q_x$. Give the physical meaning and units of $k$, $\alpha$, and $h$. (pp. 11–19)

- **$T$ (temperature):** the driving potential for heat transfer. Units: K or °C.
- **$\dot Q_x$ (heat-transfer rate):** the total heat energy transferred per unit time.
  Units: W (J/s).
- **$q_x$ (heat flux):** the heat-transfer rate per unit area, $q_x=\dot Q_x/A$.
  Units: W/m².
- **$k$ (thermal conductivity):** a material property indicating how well a material
  conducts heat. Units: W/(m K).
- **$\alpha$ (thermal diffusivity):** $\alpha\equiv k/(\rho c)$. It measures how quickly a
  material can carry heat away from a hot source relative to its ability to store heat.
  Units: m²/s.
- **$h$ (heat-transfer coefficient):** a parameter, not a material property, that
  characterizes convective heat transfer; it depends on the fluid properties, the flow
  conditions, and the geometry. Units: W/(m² K).

### 3. On pp. 14–16, why does a larger $k$ lead to a smaller temperature gradient for the same heat flux?

Rearranging Fourier's law $q=-k\ dT/dx$ for the magnitude of the gradient (Eq. 1.10,
p. 13):

$$
\left|\frac{dT}{dx}\right|=\frac{q}{k}.
$$

For a given heat flux $q$, the temperature gradient is inversely proportional to $k$. A
material with a larger $k$, such as copper, transfers heat easily, so it needs a smaller
temperature gradient (a smaller temperature difference) to push the same heat through.
Example 1.2 (pp. 16–17) illustrates this: copper ($k$ = 387 W/(m K)) conducts more than
20 times better than stainless steel ($k$ = 17 W/(m K)), so for the same heat flux the
temperature difference across the copper layer is $\Delta T_{\mathrm{Cu}}$ = 9.57 K,
compared with $\Delta T_{\mathrm{s.s.}}$ = 145 K across each steel layer.

### 4. In Lienhard Eq. (1.12), what physical quantity is being calculated? (p. 17)

Equation (1.12) calculates the **net rate of heat conduction out of a slice** of thickness
$\delta x$: the heat flowing out at $x+\delta x$ minus the heat flowing in at $x$,
approximated as $-kA\ (\partial^2T/\partial x^2)\ \delta x$.

### 5. In Lienhard Eq. (1.13), what physical quantity is being stored? (p. 17)

Equation (1.13) gives the **rate of change of internal energy** of the slice. By the First
Law, the net heat entering the slice equals the rate of energy storage,
$\rho cA\ (\partial T/\partial t)\ \delta x$. What is stored is **energy, not "heat"**: as the
Part I page puts it (section 1, "Heat And Temperature"), heat is energy transferred across
a boundary because of a temperature difference, and the transferred energy changes the
internal energy $U$ stored in the object.

### 6. Why does combining Eq. (1.12) and Eq. (1.13) produce an equation for $T(x,t)$ instead of an equation for $q$? (pp. 17–18)

Fourier's law has already replaced $q$ in Eq. (1.12) by a temperature gradient, and
Eq. (1.13) expresses the energy storage through $\partial T/\partial t$. Setting the net heat
conducted out equal to the negative of the storage rate therefore eliminates $q$
completely. The resulting equation (1.14) contains only one unknown: the temperature
distribution $T(x,t)$.

### 7. What physical property does thermal diffusivity $\alpha$ describe? (p. 18)

The thermal diffusivity describes **how quickly a material can carry heat away from a hot
source**, i.e. how fast a temperature disturbance spreads. It is the ratio of the
material's ability to conduct heat ($k$) to its ability to store it ($\rho c$). A larger
$\alpha$ means that the material responds to temperature changes faster and evens out
its internal temperature more rapidly.

### 8. How does the ratio of conduction resistance to convection resistance produce the Biot number, and why does a small Biot number support a lumped-temperature model? (pp. 21–24, Fig. 1.10)

The internal conduction resistance is roughly $R_{\mathrm{cond}}\sim L_c/(k_bA)$ and the
external convection resistance is $R_{\mathrm{conv}}=1/(\bar hA)$. Their ratio is

$$
\frac{R_{\mathrm{cond}}}{R_{\mathrm{conv}}}=\frac{L_c/(k_bA)}{1/(\bar hA)}=\frac{\bar hL_c}{k_b}\equiv\mathrm{Bi}.
$$

When $\mathrm{Bi}\ll1$, the internal conduction resistance is much smaller than the
external convection resistance. Heat moves through the interior easily, so the internal
temperature differences are negligible compared with the drop to the surroundings
(Fig. 1.10), and the whole object can be treated as having one uniform temperature (the
lumped-capacity model).

### 9. In Lienhard's thermocouple example, why does checking Bi matter? (Example 1.4, pp. 24–26)

The time constant $\mathcal{T}=\rho cV/(\bar hA)$ and the exponential response are derived
**assuming a lumped capacity** (a uniform internal temperature). If $\mathrm{Bi}<0.1$ were
not satisfied, the bead would have significant internal temperature gradients and no single
temperature, and the calculated time constant and response would be unreliable. The check
$\mathrm{Bi}=0.00278$ (p. 26) justifies the assumption.

### 10. What two independent approximation questions must be answered before the long cylinder can be modeled as a one-dimensional, semi-infinite rod? State which calculation tests each approximation.

**Radius: is each cross section isothermal?** Can the temperature variation within a cross
section be ignored? Test: the transverse Biot number
$\mathrm{Bi_\perp}=\bar h(A/P)/k=\bar hR/(2k)=\bar hd/(4k)$ (Eq. 4.27) must be $\ll1$. For
the course rod it is about $2\times10^{-4}$ (A4, 4.1).

**Length: can the far end be ignored?** Test: compare $L$ with the decay length $1/m$. For a
steady fin the semi-infinite profile $e^{-mx}$ requires $mL\gg1$; Lienhard (p. 173) treats a
fin as infinitely long for its temperatures if $mL\gtrsim5$ (for $\dot Q_0$, if
$mL\gtrsim3$). The direct test is the error $\epsilon_T(x)$ of the semi-infinite profile at
each sensor (A4, 3.4: $mL$ = 1.17, so only sensors within about 5 cm of the base pass).
For transient conduction without side loss, the analogous test is that the penetration
depth $\delta_{99}=3.64\sqrt{\alpha t}$ (Eq. 5.51, p. 224) stays well below $L$.

The two questions are independent: the course rod passes the radius test easily but fails
the length test.

## Dimensional equation sheet

| Relation | Equation | Units |
| --- | --- | --- |
| Fourier's law (1D) | $q_x = -k\ \partial T/\partial x$ | W/m² = (W/(m K))(K/m) |
| Heat-transfer rate | $\dot Q_x = q_x A$ | W |
| Conduction resistance (slab) | $R_{\mathrm{cond}} = L/(kA)$ | K/W |
| Newton's law of cooling | $q = h(T_s - T_\infty)$ | W/m² = (W/(m² K))(K) |
| Convection resistance | $R_{\mathrm{conv}} = 1/(hA_s)$ | K/W |
| Heat equation (1D, no source) | $\rho c\ \partial T/\partial t = k\ \partial^2 T/\partial x^2$ | W/m³ |
| Thermal diffusivity | $\alpha = k/(\rho c)$ | m²/s |
| Biot number | $\mathrm{Bi} = hL_c/k$, $L_c = V/A_s$ | dimensionless |
| Lumped time constant | $\tau = \rho c V/(hA_s)$ | s |
| Rod with side loss | $\rho c A\ \partial\theta/\partial t = kA\ \partial^2\theta/\partial x^2 - hP\theta$ | W/m |
| Fin parameter | $m^2 = hP/(kA) = \nu/\kappa$ | 1/m² |
| Transverse Biot number | $\mathrm{Bi_\perp} = h(A/P)/k = hR/(2k)$ | dimensionless |
