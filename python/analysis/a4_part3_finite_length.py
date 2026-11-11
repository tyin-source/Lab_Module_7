# Phys 39 Module 7, A4 Part 3: provisional finite-length prediction
#
# Before heating, predict how well the semi-infinite model e^{-mx} describes the course
# rod at each thermistor hole. The stationary fin equation d^2(theta)/dx^2 = m^2 theta
# with m^2 = hP/(kA) = 4h/(kd) for a circular rod gives, for an insulated tip at x = L,
#   Theta_finite(x) = cosh[m(L - x)] / cosh(mL),          (Lienhard Eq. 4.41)
# and the semi-infinite limit
#   Theta_inf(x) = exp(-m x).                              (Lienhard Eq. 4.50)
# The relative error of the semi-infinite model at a sensor is
#   eps_T(x) = |Theta_finite - Theta_inf| / Theta_finite
#            = 1 - (1 + e^{-2mL}) / (1 + e^{-2m(L - x)}),
# which grows toward the tip. Solving eps_T(x*) = EPS_MAX gives the farthest position
# x* at which the semi-infinite model still meets the error criterion.
#
# The script also compares the insulated tip with a convecting tip (h_L = h) on the
# course rod (Lienhard Eqs. 4.44, 4.45, 4.48, 4.49), reproduces Example 4.8 and
# Problem 4.20 as a check, and prints Bi_perp = hd/(4k) for Part 4.
#
# Inputs: h is the Part III planning value; k is Lienhard Table A.1 for 6061-T6 at
# 20 C, with the 0 C and 100 C values as the range; d, the overall rod length, and the
# hole positions were measured on the course rod, with x = 0 at the first thermistor
# hole. The analyzed length is L = overall length - s, where s is the distance from the
# TEC end of the rod to the center of the first hole. The calipers measured from the TEC
# end to the near edge of that hole, so s adds half the hole diameter.
#
# Usage (from the repository root):
#   python python/analysis/a4_part3_finite_length.py

import math

H = 10.0                    # W/(m^2 K), Part III planning value for still room air
K = 167.0                   # W/(m K), 6061-T6, Lienhard Table A.1, 20 C
K_RANGE = (166.0, 172.0)    # W/(m K), same table, 0 C and 100 C
D = 12.70e-3                # m, rod diameter (calipers)
OVERALL_LENGTH = 28.66e-2   # m, measured overall rod length
HOLE_DIAMETER = 2.525e-3    # m, thermistor hole, 2.50-2.55 mm (calipers)
EDGE_TO_END = 16.38e-3      # m, TEC end of the rod to the near edge of the first hole (calipers)
FIRST_HOLE_OFFSET = EDGE_TO_END + HOLE_DIAMETER / 2  # m, s: TEC end to first-hole center
L = OVERALL_LENGTH - FIRST_HOLE_OFFSET  # m, analyzed length, first hole to tip
HOLES_CM = [0.0, 1.2, 2.4, 3.7, 5.0, 7.6, 10.2, 15.3, 20.4]  # hole positions, x = 0 at first hole
SENSORS_CM = {"T1": 0.0, "T2": 5.0, "T3": 10.2, "T4": 15.3, "T5": 20.4}  # planned rod sensors
THETA0_EXAMPLE = 25.0       # K, illustrative base excess temperature (TEC near 45 C, room near 20 C)
DX = HOLE_DIAMETER / 2      # m, position uncertainty: the sensor can sit anywhere in its hole
EPS_MAX = 0.05              # error criterion for the semi-infinite model
H_SENSITIVITY = [5.0, 10.0, 15.0, 20.0]  # W/(m^2 K)

# Lienhard Example 4.8 (Problem 4.20 asks for the heat-flow error)
EX48 = dict(d=0.020, k=205.0, L=0.08, h=120.0, T0=150.0, Tinf=26.0)


def m_of(h, k, d):
    """Fin parameter for a circular rod, m = sqrt(hP/(kA)) = sqrt(4h/(kd)), in 1/m."""
    return math.sqrt(4.0 * h / (k * d))


def theta_finite(x, m, length):
    return math.cosh(m * (length - x)) / math.cosh(m * length)


def theta_inf(x, m):
    return math.exp(-m * x)


def eps_t(x, m, length):
    tf = theta_finite(x, m, length)
    return abs(tf - theta_inf(x, m)) / tf


def x_star(m, length, eps):
    """Farthest x with eps_T(x) <= eps."""
    u = (1.0 + math.exp(-2.0 * m * length)) / (1.0 - eps) - 1.0
    return length + math.log(u) / (2.0 * m)


def tip_comparison(m, length, ratio):
    """Insulated vs convecting tip; ratio = Bi_tip/(mL) = h_L/(k m).

    Returns tip Theta (insulated, convecting) and the base-heat-rate factor
    Q0 / (sqrt(kAhP) theta0) (insulated, convecting).
    """
    ml = m * length
    th_ins = 1.0 / math.cosh(ml)
    th_conv = 1.0 / (math.cosh(ml) + ratio * math.sinh(ml))
    q_ins = math.tanh(ml)
    q_conv = (ratio + math.tanh(ml)) / (1.0 + ratio * math.tanh(ml))
    return th_ins, th_conv, q_ins, q_conv


def main():
    m = m_of(H, K, D)
    ml = m * L
    print(f"Inputs: h = {H:g} W/(m^2 K), k = {K:g} W/(m K), d = {D * 1e3:.2f} mm, "
          f"overall length {OVERALL_LENGTH * 100:.2f} cm, s = {FIRST_HOLE_OFFSET * 1e3:.2f} mm, "
          f"L = {L * 1e2:.2f} cm, position uncertainty +/- {DX * 1e3:.1f} mm, "
          f"criterion eps_T < {EPS_MAX:.0%}\n")

    print("| Quantity | Value |")
    print("| --- | ---: |")
    print(f"| $m$ (1/m) | {m:.3f} |")
    print(f"| $1/m$ (cm) | {100 / m:.1f} |")
    print(f"| $mL$ | {ml:.3f} |")
    print(f"| $\\mathrm{{Bi}}_\\parallel=(mL)^2$ | {ml**2:.3f} |")
    print(f"| $x^*$ where $\\epsilon_T=5\\%$ (cm) | {x_star(m, L, EPS_MAX) * 100:.1f} |")
    lo, hi = (m_of(H, k, D) for k in reversed(K_RANGE))
    print(f"\nk = {K_RANGE[0]:g}-{K_RANGE[1]:g} W/(m K) gives m = {lo:.3f}-{hi:.3f} 1/m, "
          f"mL = {lo * L:.3f}-{hi * L:.3f}, x* = {x_star(lo, L, EPS_MAX) * 100:.1f}-"
          f"{x_star(hi, L, EPS_MAX) * 100:.1f} cm\n")

    print("| Hole $x$ (cm) | $L-x$ (cm) | $\\Theta_{\\mathrm{finite}}$ | $\\Theta_\\infty$ "
          "| $\\epsilon_T$ | $\\epsilon_T$ for $x\\pm\\delta x$ | $<5\\%$? |")
    print("| ---: | ---: | ---: | ---: | ---: | ---: | :---: |")
    for xc in HOLES_CM:
        x = xc / 100.0
        e = eps_t(x, m, L)
        e_lo = eps_t(max(x - DX, 0.0), m, L) if x > 0 else 0.0
        e_hi = eps_t(x + DX, m, L) if x > 0 else 0.0
        ok = "yes" if e < EPS_MAX else "no"
        print(f"| {xc:.1f} | {(L - x) * 100:.2f} | {theta_finite(x, m, L):.4f} | "
              f"{theta_inf(x, m):.4f} | {e:.2%} | {e_lo:.2%}-{e_hi:.2%} | {ok} |")

    print(f"\nPlanned sensors (theta for an illustrative theta0 = {THETA0_EXAMPLE:g} K):")
    print("| Sensor | $x$ (cm) | $\\Theta_{\\mathrm{finite}}$ | $\\ln\\Theta_{\\mathrm{finite}}$ "
          "| $\\theta$ (K) | $\\epsilon_T$ |")
    print("| --- | ---: | ---: | ---: | ---: | ---: |")
    for name, xc in SENSORS_CM.items():
        x = xc / 100.0
        tf = theta_finite(x, m, L)
        print(f"| {name} | {xc:.1f} | {tf:.4f} | {math.log(tf):.3f} | "
              f"{THETA0_EXAMPLE * tf:.1f} | {eps_t(x, m, L):.2%} |")

    ratio = H / (K * m)
    th_ins, th_conv, q_ins, q_conv = tip_comparison(m, L, ratio)
    print(f"\nCourse rod, convecting tip with h_L = h: Bi_tip = h L/k = {H * L / K:.4f}, "
          f"Bi_tip/(mL) = {ratio:.4f}")
    print(f"  Theta_tip insulated {th_ins:.4f}, convecting {th_conv:.4f} "
          f"(insulated is {(th_ins - th_conv) / th_conv:.2%} high)")
    print(f"  Q0 factor insulated {q_ins:.4f}, convecting {q_conv:.4f} "
          f"(insulated is {(q_conv - q_ins) / q_conv:.2%} low)")

    e = EX48
    m48 = m_of(e["h"], e["k"], e["d"])
    ml48 = m48 * e["L"]
    bi48 = e["h"] * e["L"] / e["k"]
    th_ins, th_conv, q_ins, q_conv = tip_comparison(m48, e["L"], bi48 / ml48)
    dT = e["T0"] - e["Tinf"]
    print(f"\nLienhard Example 4.8: mL = {ml48:.4f}, Bi_ax = {bi48:.4f}")
    print(f"  Theta_tip exact {th_conv:.4f} (T_tip = {e['Tinf'] + th_conv * dT:.1f} C), "
          f"insulated {th_ins:.4f} (T_tip = {e['Tinf'] + th_ins * dT:.1f} C)")
    print(f"Problem 4.20: heat-flow error of the insulated tip = {(q_conv - q_ins) / q_conv:.2%}")

    print("\nSensitivity to h (k = 167 W/(m K)):")
    print("| $h$ (W/(m² K)) | $m$ (1/m) | $1/m$ (cm) | $mL$ | $x^*$ (cm) | "
          f"$\\Theta_{{\\mathrm{{finite}}}}$ at {HOLES_CM[-1]:.1f} cm |")
    print("| ---: | ---: | ---: | ---: | ---: | ---: |")
    for h in H_SENSITIVITY:
        mh = m_of(h, K, D)
        print(f"| {h:g} | {mh:.3f} | {100 / mh:.1f} | {mh * L:.3f} | "
              f"{x_star(mh, L, EPS_MAX) * 100:.1f} | {theta_finite(HOLES_CM[-1] / 100, mh, L):.3f} |")
    print(f"(1/e = {1 / math.e:.3f})")

    print(f"\nPart 4: Bi_perp = h d/(4k) = {H * D / (4 * K):.2e} "
          f"(k range: {H * D / (4 * K_RANGE[1]):.2e}-{H * D / (4 * K_RANGE[0]):.2e})")


if __name__ == "__main__":
    main()
