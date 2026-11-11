# Phys 39 Module 7: sensor-map diagram of the rod instrument (Run 2 wiring onward)
#
# Draws the rod standing on the TEC with every thermistor hole, the five occupied holes
# (GUI label, lead label, Arduino input, divider resistor), the coordinate origin and
# direction, and the voltage divider used on every channel. The values come from
# docs/module_notes/module_07_rod_instrument.md, sections 1 and 2.
#
# Usage (from the repository root):
#   python python/analysis/module_07_sensor_map_diagram.py

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from module_07_common import MODULE7_FIG_DIR  # noqa: E402

HOLES_CM = [0.0, 1.2, 2.4, 3.7, 5.0, 7.6, 10.2, 15.3, 20.4]
L_CM = 26.90                 # first hole to tip
S_CM = 1.764                 # TEC end of the rod to the first hole center
D_CM = 1.270                 # rod diameter
# (GUI label, x in cm, lead label, Arduino input, measured divider resistor in kOhm)
SENSORS = [
    ("T1", 0.0, 2, "A1", 100.0),
    ("T2", 5.0, 6, "A2", 100.0),
    ("T3", 10.2, 3, "A3", 100.1),
    ("T4", 15.3, 4, "A4", 100.3),
    ("T5", 20.4, 5, "A5", 100.1),
]
TEC = ("TEC", 1, "A0", 100.0)

ROD = "#b8bec6"
EDGE = "#3d4450"
SENSOR = "#c0392b"
TAPE = "#9ecae1"
WIRE = "#2c3e50"


def main():
    fig, ax = plt.subplots(figsize=(10.5, 8.2))
    ax.set_xlim(-9.5, 31.5)
    ax.set_ylim(-6.0, 33.5)
    ax.set_aspect("equal")
    ax.axis("off")

    r = D_CM / 2
    # heat sink, TEC, rod
    ax.add_patch(Rectangle((-4.5, -5.064), 9.0, 2.0, fc="#7f8c8d", ec=EDGE))
    for i in range(7):
        ax.add_patch(Rectangle((-4.2 + 1.3 * i, -5.664), 0.5, 0.6, fc="#7f8c8d", ec=EDGE))
    ax.add_patch(Rectangle((-2.2, -3.064), 4.4, 1.3, fc="#e6b0aa", ec=EDGE))
    ax.text(-2.5, -2.4, "TEC (thermistor in its base)", ha="right", va="center", fontsize=8.5)
    ax.text(4.9, -4.06, "heat sink", va="center", fontsize=9)
    rod_bottom = -S_CM
    ax.add_patch(Rectangle((-r, rod_bottom), D_CM, L_CM + S_CM, fc=ROD, ec=EDGE, lw=1.2))

    # holes
    for x in HOLES_CM:
        used = any(abs(x - s[1]) < 1e-6 for s in SENSORS)
        if used:
            ax.add_patch(Rectangle((-r - 0.15, x - 0.55), D_CM + 0.3, 1.1, fc=TAPE, ec="none",
                                   alpha=0.9, zorder=2))
        ax.plot(0, x, "o", ms=7 if used else 5, mfc=SENSOR if used else "white",
                mec=EDGE, zorder=3)
        ax.text(-1.0, x, f"{x:.1f}", ha="right", va="center", fontsize=8.5,
                color="black" if used else "#7f8c8d")

    # coordinate and dimensions (left side)
    ax.annotate("", xy=(-5.2, 6.0), xytext=(-5.2, 0.0),
                arrowprops=dict(arrowstyle="-|>", color="black", lw=1.4))
    ax.text(-5.6, 3.0, "$x$", ha="right", va="center", fontsize=12)
    ax.text(-5.6, 0.4, "$x=0$\n(T1, first hole)", ha="right", va="center", fontsize=8.5)
    ax.annotate("", xy=(-3.2, L_CM), xytext=(-3.2, 0.0),
                arrowprops=dict(arrowstyle="<->", color="#555", lw=1.0))
    ax.text(-3.45, 13.5, f"$L$ = {L_CM:.2f} cm", rotation=90, ha="right", va="center",
            fontsize=9)
    ax.annotate("", xy=(-2.3, 0.0), xytext=(-2.3, rod_bottom),
                arrowprops=dict(arrowstyle="<->", color="#555", lw=1.0, shrinkA=0, shrinkB=0))
    ax.text(-2.55, -1.5, "17.64 mm", ha="right", va="center", fontsize=8)
    ax.text(1.2, L_CM - 0.2, "tip, $x=L$ (insulated)\noverall rod length 28.66 cm\n"
            "$d$ = 12.70 mm", ha="left", va="top", fontsize=8.5)
    ax.text(-1.0, 22.6, "hole $x$ (cm)", ha="right", va="center", fontsize=8, color="#555")

    # Arduino block and wires
    box_x, box_w = 21.0, 9.2
    pins_y = {"A0": -2.4, "A1": 1.5, "A2": 5.5, "A3": 9.5, "A4": 13.5, "A5": 17.5}
    ax.add_patch(FancyBboxPatch((box_x, -4.0), box_w, 24.2, boxstyle="round,pad=0.3",
                                fc="#eaf2f8", ec=EDGE))
    ax.text(box_x + box_w / 2, 20.9, "Arduino Uno", ha="center", fontsize=10,
            weight="bold")
    for pin, y in pins_y.items():
        ax.plot(box_x, y, "s", ms=6, mfc="white", mec=EDGE, zorder=4)
        ax.text(box_x + 0.6, y, pin, va="center", fontsize=10, weight="bold")

    def label(y, text):
        ax.text(1.4, y, text, va="center", fontsize=8.8,
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#bbb", lw=0.6))

    for name, x, lead, pin, rk in SENSORS:
        label(x, f"{name}  lead {lead}  {rk:.1f} k$\\Omega$")
        ax.plot([9.9, 14.5, box_x], [x, pins_y[pin], pins_y[pin]], color=WIRE, lw=1.0)
    name, lead, pin, rk = TEC
    ax.plot([2.2, box_x], [-2.4, pins_y[pin]], color=WIRE, lw=1.0)
    ax.text(3.0, -1.9, f"TEC  lead {lead}  {rk:.1f} k$\\Omega$", va="bottom", fontsize=8.8)

    # divider inset inside the Arduino box
    cx = box_x + 3.2
    ax.text(cx, 4.1, "each channel:", ha="center", fontsize=8.5, color="#555")
    ax.plot([cx, cx], [-0.5, 2.5], color=WIRE, lw=1.0)
    ax.text(cx, 2.7, "+5 V", ha="center", va="bottom", fontsize=8.5)
    ax.add_patch(Rectangle((cx - 0.35, 0.9), 0.7, 1.2, fc="white", ec=WIRE))
    ax.text(cx + 0.6, 1.5, "$R_n$ ≈ 100 k$\\Omega$", va="center", fontsize=8)
    ax.plot([cx - 1.2, cx], [0.2, 0.2], color=WIRE, lw=1.0)
    ax.text(cx - 1.3, 0.2, "A$n$", ha="right", va="center", fontsize=8.5)
    ax.add_patch(Rectangle((cx - 0.35, -1.6), 0.7, 1.2, fc="#f5b7b1", ec=WIRE))
    ax.text(cx + 0.6, -1.0, "thermistor\n100 k$\\Omega$, $\\beta$ = 4540", va="center",
            fontsize=7.5)
    ax.plot([cx, cx], [-1.6, -2.4], color=WIRE, lw=1.0)
    ax.text(cx, -2.6, "GND", ha="center", va="top", fontsize=8.5)

    ax.text(-9.3, 33.2, "Module 7 rod sensor map (Run 2 wiring onward)", fontsize=12,
            weight="bold", va="top")
    ax.text(-9.3, 32.0, "Rod stands vertically on the TEC; $x$ increases upward. Filled "
            "circles: occupied holes (blue: tape band); open circles: unused holes.\n"
            "Lead label = permanent label on the thermistor lead; "
            "$R_n$ = measured divider resistor. Position uncertainty ±1.3 mm.",
            fontsize=8.5, va="top")

    MODULE7_FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = MODULE7_FIG_DIR / "rod_sensor_map_diagram.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    print(out)


if __name__ == "__main__":
    main()
