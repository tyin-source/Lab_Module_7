# Phys 39 Module 7, A4 Part I: Lienhard Problem 1.3
#
# A 1 cm slab carries a steady heat flux q = 5000 W/m^2; its cold side is at -40 C.
# Fourier's law for steady one-dimensional conduction with constant k,
#   q = -k dT/dx  ->  q = k (T_hot - T_cold) / L,
# gives the temperature rise across the slab, Delta T = q L / k.
#
# Conductivities are from Lienhard, A Heat Transfer Textbook (v6), Appendix A:
# Table A.1 (metals, the 20 C column, as in the book's answer for silver) and
# Table A.2 (non-metals, at the temperature listed in the table). The script also
# repeats silver and aluminium with k interpolated to -40 C (Table A.1 gives
# -100 C and 0 C values) to show how little the reference temperature matters
# for the metals.
#
# Usage (from the repository root):
#   python python/analysis/a4_problem_1_3.py

Q_W_PER_M2 = 5000.0
L_M = 0.01
T_COLD_C = -40.0

MATERIALS = [  # (material, k in W/(m K), Lienhard table and temperature of that k)
    ("Pure silver (99.99+ %)", 427.0, "A.1, 20 °C"),
    ("Pure aluminum", 237.0, "A.1, 20 °C"),
    ("Mild steel (0.5 % carbon)", 54.0, "A.1, 20 °C"),
    ("Ice", 2.215, "A.2, 0 °C"),
    ("Spruce", 0.11, "A.2, 20 °C"),
    ("Insulation (85 % magnesia)", 0.067, "A.2, 38 °C"),
    ("Silica aerogel", 0.024, "A.2, 0 °C"),
]
LOW_T = [  # (material, k at -100 C, k at 0 C) from Table A.1
    ("Pure silver (99.99+ %)", 431.0, 428.0),
    ("Pure aluminum", 242.0, 236.0),
]


def delta_t(k):
    return Q_W_PER_M2 * L_M / k


def fmt(x):
    """Three significant figures without exponent notation."""
    return f"{x:.3f}" if abs(x) < 1 else f"{x:.1f}" if abs(x) < 100 else f"{x:.0f}"


def fmt_hot(dT):
    """Hot-side temperature, rounded like Delta T."""
    digits = 2 if dT < 1 else 1 if dT < 100 else 0
    return f"{T_COLD_C + dT:.{digits}f}"


def main():
    print(f"q = {Q_W_PER_M2:g} W/m^2, L = {L_M:g} m, cold side {T_COLD_C:g} C; "
          f"Delta T = q L / k = {Q_W_PER_M2 * L_M:g} W/m / k\n")
    print("| Material | k (W/(m K)) | Source (Lienhard) | Delta T (K) | Hot side (°C) |")
    print("| --- | ---: | --- | ---: | ---: |")
    for name, k, src in MATERIALS:
        dT = delta_t(k)
        print(f"| {name} | {k:g} | {src} | {fmt(dT)} | {fmt_hot(dT)} |")
    print("\nWith k interpolated linearly to -40 C:")
    for name, k100, k0 in LOW_T:
        k = k100 + (k0 - k100) * (-40.0 - -100.0) / 100.0
        print(f"  {name}: k = {k:.1f} W/(m K), Delta T = {delta_t(k):.4f} K")


if __name__ == "__main__":
    main()
