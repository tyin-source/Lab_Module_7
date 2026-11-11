# Phys 39 Module 7, Part III Phase 5: fit the stationary rod profile
#
# Reads one raw run CSV from python/module_07_rod_acquisition_gui.py, checks the
# steady-state criterion at the end of the run, averages each rod sensor over the
# final interval, and fits the excess temperature theta with
#   finite insulated tip:  theta(x) = theta0 cosh[m(L - x)] / cosh(mL)
#   semi-infinite:         theta(x) = theta0 exp(-m x)
# (both with theta0 and m free). It reports m and 1/m with uncertainties, the
# reduced chi-squared and residuals of both fits, how much m shifts when the
# finite end is ignored, the self-consistency check Bi_perp = (m d / 4)^2, and
# eps_T at every sensor from the fitted m. Figures go to docs/figures/module_07/.
#
# Uncertainty of each averaged theta_i (added in quadrature):
#   - standard error of the mean over the averaging interval,
#   - a floor for the thermistor/ADC resolution (--sigma-floor),
#   - position uncertainty dx converted with the fitted slope |dtheta/dx| dx.
#
# theta can be measured from either reference:
#   --baseline START,END  each channel's own mean over an interval (Arduino time, s)
#                         with the TEC off and the whole rod at room temperature, so
#                         theta_i = T_i(final) - T_i(baseline). A constant offset of a
#                         channel cancels, and the baseline's standard error is added
#                         to the uncertainty. The baseline is taken from the run file
#                         itself unless --baseline-file names another file recorded
#                         with the same wiring (e.g. after the rod cooled back to room
#                         temperature). Channels that drift by more than the
#                         steady-state criterion during the baseline are flagged.
#   --t-inf T             one room temperature for all channels, theta_i = T_i - T_inf.
#                         It is taken as exact; its uncertainty shifts every theta_i
#                         together and should be discussed separately.
# --exclude T3,T4 leaves faulty rod channels out of the fits (they are still plotted in
# the time history, marked "excluded").
#
# Usage (from the repository root), for example:
#   python python/analysis/module_07_stationary_fit.py data/module_07/rod_20261111-101500.csv \
#       --baseline 60,660 --positions-cm 0,5.0,10.2,15.3,20.4 --length-cm 26.90

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from module_07_common import MODULE7_FIG_DIR, ROD_COLUMNS, SENSOR_LABELS, TEMPERATURE_COLUMNS, read_rod_csv  # noqa: E402


def finite_model(x, theta0, m, length):
    return theta0 * np.cosh(m * (length - x)) / np.cosh(m * length)


def semi_infinite_model(x, theta0, m):
    return theta0 * np.exp(-m * x)


def eps_t(x, m, length):
    tf = np.cosh(m * (length - x)) / np.cosh(m * length)
    return np.abs(tf - np.exp(-m * x)) / tf


def parse_args():
    p = argparse.ArgumentParser(description="Fit the stationary rod profile (Module 7, Phase 5).")
    p.add_argument("csv", type=Path, help="raw run CSV from the acquisition GUI")
    ref = p.add_mutually_exclusive_group(required=True)
    ref.add_argument("--baseline", default=None,
                     help="START,END of a TEC-off interval (Arduino time, s): each channel's "
                          "mean there is its own room-temperature reading")
    ref.add_argument("--t-inf", type=float, default=None,
                     help="room temperature T_inf (C), measured away from the apparatus")
    p.add_argument("--baseline-file", type=Path, default=None,
                   help="take the --baseline interval from this file (same wiring) "
                        "instead of the run file")
    p.add_argument("--positions-cm", default="0,5.0,10.2,15.3,20.4",
                   help="x of rod1..rod5 from the first hole (cm), comma-separated")
    p.add_argument("--dx-mm", type=float, default=1.3, help="position uncertainty (mm)")
    p.add_argument("--length-cm", type=float, default=26.90,
                   help="analyzed length L, first hole to tip (cm)")
    p.add_argument("--diameter-mm", type=float, default=12.70, help="rod diameter d (mm)")
    p.add_argument("--diameter-err-mm", type=float, default=0.02, help="uncertainty of d (mm)")
    p.add_argument("--t-end", type=float, default=None,
                   help="end of the analysis (Arduino time, s); default: last record")
    p.add_argument("--average-min", type=float, default=5.0,
                   help="length of the final averaging interval (min)")
    p.add_argument("--steady-min", type=float, default=10.0,
                   help="window for the steady-state check before t_end (min)")
    p.add_argument("--steady-rate", type=float, default=0.02,
                   help="steady-state criterion |dT/dt| (C/min)")
    p.add_argument("--sigma-floor", type=float, default=0.05,
                   help="resolution floor added to each sensor's uncertainty (K)")
    p.add_argument("--eps-max", type=float, default=0.05, help="eps_T criterion")
    p.add_argument("--exclude", default="",
                   help="rod channels to leave out of the fits, e.g. T3,T4")
    p.add_argument("--fig-dir", type=Path, default=MODULE7_FIG_DIR)
    return p.parse_args()


def main():
    a = parse_args()
    data = read_rod_csv(a.csv)
    t = data["time_s"]
    if np.any(np.diff(t) < 0):
        sys.exit("Arduino time goes back in this file (the Arduino restarted): "
                 "analyze one continuous part with --t-end, or split the file.")
    x = np.array([float(v) for v in a.positions_cm.split(",")]) / 100.0   # m
    if len(x) != len(ROD_COLUMNS):
        sys.exit("--positions-cm needs five values (rod1..rod5)")
    excluded = {v.strip() for v in a.exclude.split(",") if v.strip()}
    unknown = excluded - {SENSOR_LABELS[c] for c in ROD_COLUMNS}
    if unknown:
        sys.exit(f"--exclude: unknown channel(s) {sorted(unknown)}; use T1..T5")
    keep = [i for i, c in enumerate(ROD_COLUMNS) if SENSOR_LABELS[c] not in excluded]
    cols = [ROD_COLUMNS[i] for i in keep]       # rod channels used in the fits
    x = x[keep]
    if len(cols) < 3:
        sys.exit("at least three rod channels are needed for the two-parameter fits")
    length = a.length_cm / 100.0
    d, d_err = a.diameter_mm / 1000.0, a.diameter_err_mm / 1000.0
    dx = a.dx_mm / 1000.0
    t_end = t[-1] if a.t_end is None else a.t_end

    # ---- steady-state check over the last steady-min minutes ----
    in_check = (t > t_end - 60 * a.steady_min) & (t <= t_end)
    print(f"File: {a.csv.name}, {len(t)} records, t = {t[0]:.0f}-{t[-1]:.0f} s; "
          f"analysis ends at t = {t_end:.0f} s")
    if excluded:
        print(f"Left out of the fits: {', '.join(sorted(excluded))}")
    print()
    print(f"Steady-state check: slope of a straight-line fit over the last "
          f"{a.steady_min:g} min; criterion |dT/dt| < {a.steady_rate:g} C/min")
    print("| Sensor | dT/dt (C/min) | Steady? |")
    print("| --- | ---: | :---: |")
    steady_ok = True
    for col in TEMPERATURE_COLUMNS:
        ok_pts = in_check & ~np.isnan(data[col])
        slope = np.polyfit(t[ok_pts], data[col][ok_pts], 1)[0] * 60.0
        ok = abs(slope) < a.steady_rate
        steady_ok &= ok
        print(f"| {SENSOR_LABELS[col]} | {slope:+.4f} | {'yes' if ok else 'NO'} |")
    print(f"\nAll sensors steady: {'yes' if steady_ok else 'NO - use a later t_end or a longer run'}\n")

    # ---- reference temperature of each channel ----
    def mean_sem(col, mask, source=None):
        v = (data if source is None else source)[col][mask]
        v = v[~np.isnan(v)]
        if len(v) < 2:
            sys.exit(f"{SENSOR_LABELS[col]}: fewer than two readings in the interval")
        return v.mean(), v.std(ddof=1) / np.sqrt(len(v))

    if a.baseline is not None:
        b0, b1 = (float(v) for v in a.baseline.split(","))
        if a.baseline_file is None:
            base, base_name = data, a.csv.name
        else:
            base, base_name = read_rod_csv(a.baseline_file), a.baseline_file.name
        tb = base["time_s"]
        in_base = (tb >= b0) & (tb <= b1)
        if in_base.sum() < 2:
            sys.exit(f"fewer than two records in the baseline interval of {base_name}")
        ref = {col: mean_sem(col, in_base, base) for col in TEMPERATURE_COLUMNS}
        t1 = ref["rod1_C"][0]
        print(f"Baseline (TEC off): {base_name}, t = {b0:g}-{b1:g} s, "
              f"{int(in_base.sum())} records")
        print("| Sensor | baseline (C) | offset from T1 (C) | drift (C/min) |")
        print("| --- | ---: | ---: | ---: |")
        drifting = []
        for col in TEMPERATURE_COLUMNS:
            ok_pts = in_base & ~np.isnan(base[col])
            drift = np.polyfit(tb[ok_pts], base[col][ok_pts], 1)[0] * 60.0
            if abs(drift) >= a.steady_rate:
                drifting.append(SENSOR_LABELS[col])
            print(f"| {SENSOR_LABELS[col]} | {ref[col][0]:.3f} | {ref[col][0] - t1:+.3f} | "
                  f"{drift:+.4f} |")
        if drifting:
            print(f"WARNING: {', '.join(drifting)} drift by more than {a.steady_rate:g} C/min "
                  "during the baseline. Equal drifts on every channel mean the room "
                  "temperature was changing; unequal ones mean the rod was not yet at room "
                  "temperature. Either way the common reference for theta is uncertain.")
        print()
        where = "" if a.baseline_file is None else f" of {base_name}"
        ref_text = f"each channel's baseline at t = {b0:g}-{b1:g} s{where}"
    else:
        ref = {col: (a.t_inf, 0.0) for col in TEMPERATURE_COLUMNS}
        ref_text = f"T_inf = {a.t_inf:.2f} C"

    # ---- average each rod sensor over the final interval ----
    in_avg = (t > t_end - 60 * a.average_min) & (t <= t_end)
    theta, sigma_stat = [], []
    for col in cols:
        mean, sem = mean_sem(col, in_avg)
        theta.append(mean - ref[col][0])
        sigma_stat.append(np.hypot(sem, ref[col][1]))
    theta, sigma_stat = np.array(theta), np.array(sigma_stat)
    sigma0 = np.sqrt(sigma_stat**2 + a.sigma_floor**2)

    # ---- fits: preliminary fit for the slope, then with the position term ----
    def fit(model, sigma):
        p, cov = curve_fit(model, x, theta, p0=[theta[0], 5.0], sigma=sigma,
                           absolute_sigma=True, maxfev=10000)
        return p, np.sqrt(np.diag(cov))

    finite = lambda xx, th0, m: finite_model(xx, th0, m, length)  # noqa: E731
    p_fin, _ = fit(finite, sigma0)
    slope_x = np.abs(p_fin[0] * p_fin[1] * np.sinh(p_fin[1] * (length - x))
                     / np.cosh(p_fin[1] * length))                  # |dtheta/dx|, K/m
    sigma = np.sqrt(sigma0**2 + (slope_x * dx) ** 2)
    p_fin, e_fin = fit(finite, sigma)
    p_inf, e_inf = fit(semi_infinite_model, sigma)
    res_fin = theta - finite(x, *p_fin)
    res_inf = theta - semi_infinite_model(x, *p_inf)
    dof = len(x) - 2
    chi2_fin = np.sum((res_fin / sigma) ** 2)
    chi2_inf = np.sum((res_inf / sigma) ** 2)

    print(f"Stationary profile: mean of the last {a.average_min:g} min, theta from {ref_text}")
    print("| Sensor | x (cm) | theta (K) | sigma (K) | finite residual (K) | semi-inf residual (K) |")
    print("| --- | ---: | ---: | ---: | ---: | ---: |")
    for i, col in enumerate(cols):
        print(f"| {SENSOR_LABELS[col]} | {100 * x[i]:.1f} | {theta[i]:.3f} | {sigma[i]:.3f} | "
              f"{res_fin[i]:+.3f} | {res_inf[i]:+.3f} |")

    m_f, sm_f = p_fin[1], e_fin[1]
    m_i, sm_i = p_inf[1], e_inf[1]
    print("\n| Model | theta0 (K) | m (1/m) | 1/m (cm) | chi2/dof |")
    print("| --- | ---: | ---: | ---: | ---: |")
    for name, p, e, chi2 in (("Finite, insulated tip", p_fin, e_fin, chi2_fin),
                             ("Semi-infinite", p_inf, e_inf, chi2_inf)):
        print(f"| {name} | {p[0]:.3f} ± {e[0]:.3f} | {p[1]:.3f} ± {e[1]:.3f} | "
              f"{100 / p[1]:.1f} ± {100 * e[1] / p[1]**2:.1f} | {chi2 / dof:.2f} |")
    shift = m_i - m_f
    print(f"\nIgnoring the finite end shifts m by {shift:+.3f} 1/m "
          f"= {shift / sm_f:+.1f} times the finite-fit uncertainty.")

    bi = (m_f * d / 4) ** 2
    bi_err = 2 * bi * np.sqrt((sm_f / m_f) ** 2 + (d_err / d) ** 2)
    print(f"Self-consistency: Bi_perp = (m d / 4)^2 = {bi:.2e} ± {bi_err:.1e}")
    print(f"Finite-length check with the fitted m: mL = {m_f * length:.3f}")
    print("| Sensor | x (cm) | eps_T | < criterion? |")
    print("| --- | ---: | ---: | :---: |")
    for i, col in enumerate(cols):
        e = eps_t(x[i], m_f, length)
        print(f"| {SENSOR_LABELS[col]} | {100 * x[i]:.1f} | {e:.2%} | "
              f"{'yes' if e < a.eps_max else 'no'} |")

    # ---- figures ----
    a.fig_dir.mkdir(parents=True, exist_ok=True)
    stem = a.csv.stem

    fig, ax = plt.subplots(figsize=(8, 4.5))
    for col in TEMPERATURE_COLUMNS:
        label = SENSOR_LABELS[col] + (" (excluded)" if SENSOR_LABELS[col] in excluded else "")
        ax.plot(t / 60, data[col], lw=2.2 if col == "tec_C" else 1.2, label=label,
                ls=":" if SENSOR_LABELS[col] in excluded else "-")
    ax.axvspan((t_end - 60 * a.steady_min) / 60, t_end / 60, color="0.9", label="steady check")
    ax.axvspan((t_end - 60 * a.average_min) / 60, t_end / 60, color="0.75", label="average")
    ax.set_xlabel("Arduino time (min)")
    ax.set_ylabel("Temperature (°C)")
    ax.legend(ncol=4, fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    f1 = a.fig_dir / f"{stem}_time_history.png"
    fig.savefig(f1, dpi=150)
    plt.close(fig)

    xs = np.linspace(0, length, 300)
    fig, axs = plt.subplots(2, 2, figsize=(10, 6.5), sharex=True,
                            gridspec_kw={"height_ratios": [3, 1.3]})
    for col_i, scale in enumerate(("linear", "log")):
        ax = axs[0, col_i]
        ax.errorbar(100 * x, theta, yerr=sigma, xerr=100 * dx, fmt="ko", ms=4, label="data")
        for xi, yi, col in zip(x, theta, cols):
            ax.annotate(SENSOR_LABELS[col], (100 * xi, yi), textcoords="offset points",
                        xytext=(5, 5), fontsize=8)
        ax.plot(100 * xs, finite(xs, *p_fin), "C0-",
                label=f"finite, m = {m_f:.2f} ± {sm_f:.2f} 1/m")
        ax.plot(100 * xs, semi_infinite_model(xs, *p_inf), "C3--",
                label=f"semi-infinite, m = {m_i:.2f} ± {sm_i:.2f} 1/m")
        ax.set_yscale(scale)
        ax.set_ylabel(r"$\theta = T - T_\infty$ (K)")
        ax.grid(alpha=0.3, which="both")
        ax.legend(fontsize=8)
        ax.set_title("linear" if scale == "linear" else "semilog")
        r = axs[1, col_i]
        r.axhline(0, color="0.5", lw=1)
        r.errorbar(100 * x - 0.15, res_fin, yerr=sigma, fmt="C0o", ms=4, label="finite")
        r.errorbar(100 * x + 0.15, res_inf, yerr=sigma, fmt="C3s", ms=4, label="semi-infinite")
        r.set_xlabel("x from the first hole (cm)")
        r.set_ylabel("residual (K)")
        r.grid(alpha=0.3)
    axs[1, 0].legend(fontsize=8)
    fig.tight_layout()
    f2 = a.fig_dir / f"{stem}_profile_fits.png"
    fig.savefig(f2, dpi=150)
    plt.close(fig)
    print(f"\nFigures: {f1}\n         {f2}")


if __name__ == "__main__":
    main()
