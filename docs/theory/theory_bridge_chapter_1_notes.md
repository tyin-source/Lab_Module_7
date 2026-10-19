# Module 7, Part I: Thermal Transport Foundations — Notes

Short answers to the Part I reading questions (Lienhard Section 1.3, pp. 11–26) and a
dimensional equation sheet, kept for A4, the C5 oral check, and A5.

## Reading questions

1. **Why is Fourier's law a phenomenological constitutive law, and what does its minus
   sign say about the direction of heat flow?** *(to be written)*
2. **Distinguish $T$, $\dot Q_x$, and $q_x$; give the meaning and units of $k$,
   $\alpha$, and $h$.** *(to be written)*
3. **Why does a larger $k$ give a smaller temperature gradient for the same heat
   flux (pp. 14–16)?** *(to be written)*
4. **In Lienhard Eq. (1.12), what physical quantity is being calculated?** *(to be
   written)*
5. **In Lienhard Eq. (1.13), what physical quantity is being stored?** *(to be
   written)*
6. **Why does combining Eqs. (1.12) and (1.13) give an equation for $T(x,t)$ instead of
   one for $q$?** *(to be written)*
7. **What physical property does the thermal diffusivity $\alpha$ describe?** *(to be
   written)*
8. **How does the ratio of conduction to convection resistance produce the Biot number,
   and why does a small Biot number support a lumped model?** *(to be written)*
9. **In Lienhard's thermocouple example, why does checking Bi matter?** *(to be
   written)*
10. **What two independent approximation questions must be answered before the long
    cylinder can be modeled as a one-dimensional, semi-infinite rod, and which
    calculation tests each?** *(to be written)*

## Dimensional equation sheet

| Relation | Equation | Units |
| --- | --- | --- |
| Fourier's law (1D) | $q_x = -k\thinspace \partial T/\partial x$ | W/m² = (W/(m K))(K/m) |
| Heat-transfer rate | $\dot Q_x = q_x A$ | W |
| Conduction resistance (slab) | $R_{\mathrm{cond}} = L/(kA)$ | K/W |
| Newton's law of cooling | $q = h(T_s - T_\infty)$ | W/m² = (W/(m² K))(K) |
| Convection resistance | $R_{\mathrm{conv}} = 1/(hA_s)$ | K/W |
| Heat equation (1D, no source) | $\rho c\thinspace \partial T/\partial t = k\thinspace \partial^2 T/\partial x^2$ | W/m³ |
| Thermal diffusivity | $\alpha = k/(\rho c)$ | m²/s |
| Biot number | $\mathrm{Bi} = hL_c/k$, $L_c = V/A_s$ | dimensionless |
| Lumped time constant | $\tau = \rho c V/(hA_s)$ | s |
| Rod with side loss | $\rho c A\thinspace \partial\theta/\partial t = kA\thinspace \partial^2\theta/\partial x^2 - hP\theta$ | W/m |
| Fin parameter | $m^2 = hP/(kA) = \nu/\kappa$ | 1/m² |
| Transverse Biot number | $\mathrm{Bi}_{\perp} = h(A/P)/k = hR/(2k)$ | dimensionless |
