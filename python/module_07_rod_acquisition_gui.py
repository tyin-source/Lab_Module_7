# Phys 39 Module 7 - six-thermistor rod acquisition GUI with P/PI TEC control
# (copied from the Module 6 GUI, python/module6_pi_control_gui.py in the Module 6
# repository, which stays unchanged as the working checkpoint)
#
# Use with arduino/module_07_rod_controller/module_07_rod_controller.ino (9600 baud).
#
# Changes from Module 6:
#   - Parses only complete Arduino lines that begin with DATA:
#       DATA,time_s,tec_C,rod1_C,rod2_C,rod3_C,rod4_C,rod5_C,pwm,heat_cool,setpoint_C,safety
#     The header line, start-up messages, safety messages, and malformed lines
#     never stop the program. Visible counters show accepted and rejected DATA
#     lines (a rejected line starts with DATA but cannot be read).
#   - Plots all six temperatures against Arduino time with fixed labels and
#     colors (TEC thicker), checkboxes to hide or show each trace, and live
#     numbers for all six. The whole session stays on the plots, as in Module 6.
#   - Every accepted DATA record is written to a raw CSV with exactly the eleven
#     DATA columns, as the Arduino sent them (no calibration corrections). A new
#     file, data/module_07/rod_<YYYYmmdd-HHMMSS>.csv, is created when the GUI
#     starts and by the "New data file" button; an existing file is never
#     overwritten. The file is flushed after every record.
#   - Each CSV has a metadata file next to it (same name, _meta.txt): channel
#     map, sensor positions, serial settings, code files and Git commit, then
#     time-stamped events (control start and stop with gains and setpoints,
#     setpoint changes, Arduino restarts, safety messages) and typed notes.
#   - In control mode the GUI also sends SETPOINT <Tset> before each SET PWM, so
#     the Arduino's record shows the setpoint; SETPOINT OFF when control stops.
#   - The P/PI law (pi_control) is unchanged and uses the TEC thermistor only.
#     The rod thermistors are measurements and never enter the controller.
#   - Removed: the Module 4 susceptibility and one-lump damping display (the TEC
#     now drives the rod, so the Module 4 plant values no longer apply), the
#     per-run control files, and the baseline buffer (the raw CSV records
#     continuously, so the baseline is already in it).
#
# Two modes, as in Module 6:
#   MANUAL    - direction drop-down + PWM slider (open loop).
#   CONTROL   - on every new TEC temperature T_n, Python calculates
#                   e_n     = Tset - T_n
#                   q_{n+1} = q_n + e_n dt         (held if anti-windup applies)
#                   u       = clamp(Kp e_n + Ki q_{n+1}, -u_max, +u_max)
#               and sends  SET PWM <|u|> DIR HEAT  if u >= 0, else  DIR COOL.

import math
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

import serial
from PySide6 import QtCore, QtWidgets
import pyqtgraph as pg

from module_07_common import (ARDUINO_INPUTS, DATA_COLUMNS, MODULE7_DATA_DIR, REPO_ROOT,
                              SENSOR_LABELS, TEMPERATURE_COLUMNS)


# ------------------------------------------------------------------
# USER CONFIGURATION  (edit these near the top)
# ------------------------------------------------------------------
SERIAL_PORT = "/dev/cu.usbmodem1101"          # "/dev/cu.usbmodem1101" Mac. Windows example: "COM5"
BAUD_RATE = 9600

PLOT_UPDATE_MS = 100          # how often the plots redraw (ms)
SEND_DEBOUNCE_MS = 80         # manual mode: wait after the last change before sending
TEMP_MIN_Y_SPAN = 0.2         # smallest temperature-axis span (C)

PWM_MAX = 255                 # 8-bit PWM magnitude limit (also clamped by the Arduino)

# Setpoint range and the two setpoints of the Phase 4 step (20 C -> 45 C).
# Part III: never set the TEC above 55 C.
SETPOINT_MIN_C = 10.0
SETPOINT_MAX_C = 55.0
SETPOINT_LOW_DEFAULT_C = 20.0
SETPOINT_HIGH_DEFAULT_C = 45.0

KP_MAX = 100.0                # largest Kp the GUI accepts (PWM per C)
KP_DEFAULT = 0.5
KI_MAX = 5.0                  # largest Ki the GUI accepts (PWM per C s)
KI_DEFAULT = 0.0              # P only until Ki is set deliberately

DATA_DIR = MODULE7_DATA_DIR

# Sensor positions written to each metadata file: x measured from the first
# thermistor hole (x = 0) toward the tip. Update these to the MEASURED holes
# before a run; they are not used for any calculation in this program.
SENSOR_POSITIONS_CM = {"rod1_C": 0.0, "rod2_C": 5.0, "rod3_C": 10.2,
                       "rod4_C": 15.3, "rod5_C": 20.4}
POSITION_UNCERTAINTY_MM = 1.3

# Plot style for each channel: (color, line width). TEC is thicker.
TRACE_STYLE = {
    "tec_C": ("k", 3.0),
    "rod1_C": ((214, 39, 40), 1.6),
    "rod2_C": ((255, 127, 14), 1.6),
    "rod3_C": ((44, 160, 44), 1.6),
    "rod4_C": ((31, 119, 180), 1.6),
    "rod5_C": ((148, 103, 189), 1.6),
}
# ------------------------------------------------------------------


# ------------------------------------------------------------------
# PI CONTROL LAW  (unchanged from Module 6)
# ------------------------------------------------------------------
class PIStep(NamedTuple):
    e: float            # error e_n = Tset - T_n                      [C]
    q: float            # integral state q_{n+1} after this step      [C s]
    u_p: float          # u_P = Kp e_n                                [PWM]
    u_i: float          # u_I = Ki q_{n+1}                            [PWM]
    u_req: float        # requested command u_P + u_I                 [PWM]
    u_applied: float    # clamped command, -u_max ... +u_max          [PWM]
    held: bool          # True if conditional integration kept q_n
    saturated: bool     # True if |u_req| > u_max
    direction: str      # "HEAT" if u_applied >= 0, else "COOL"
    pwm: int            # |u_applied| rounded, sent to the Arduino     [0-255]


def pi_control(t_set: float, temperature: float, q: float, dt: float,
               kp: float, ki: float, u_max: float, anti_windup: bool) -> PIStep:
    """One PI update for one accepted temperature (Module 6 handout, Part 7):
        q_{n+1} = q_n + e_n dt,    u_n = Kp e_n + Ki q_{n+1}.
    Ki = 0 gives P-only control (u_I = 0)."""
    e = t_set - temperature                      # error e_n = Tset - T_n           [C]

    # Integral state. Conditional integration (anti-windup): if the request
    # with the updated q is beyond the PWM limit and this error pushes it
    # farther, keep q_n on this step. Otherwise update q, including when the
    # error helps bring the command back out of saturation.
    q_next = q + e * dt                          # q_{n+1} = q_n + e_n dt           [C s]
    u_next = kp * e + ki * q_next
    held = anti_windup and ((u_next > u_max and e > 0) or (u_next < -u_max and e < 0))
    if held:
        q_next = q

    u_p = kp * e                                 # u_P = Kp e_n                     [PWM]
    u_i = ki * q_next                            # u_I = Ki q_{n+1}                 [PWM]
    u_req = u_p + u_i                            # requested command                [PWM]
    u_applied = max(-u_max, min(u_max, u_req))   # clamped (applied) command        [PWM]

    # Convert u to the Arduino command: the sign selects the direction,
    # the magnitude |u| becomes the integer PWM value.
    direction = "HEAT" if u_applied >= 0 else "COOL"
    pwm = min(int(abs(u_applied) + 0.5), PWM_MAX)
    saturated = abs(u_req) > u_max
    return PIStep(e, q_next, u_p, u_i, u_req, u_applied, held, saturated, direction, pwm)


# ------------------------------------------------------------------
# SERIAL LINK  (unchanged from Module 6)
# ------------------------------------------------------------------
# The reader thread reads lines and the GUI thread writes commands.
# pyserial allows one thread to read while another writes, so only the
# writes are serialised with a lock.
class SerialLink:
    def __init__(self, port: str, baud: int):
        self.ser = serial.Serial(port, baud, timeout=0.5)
        self.write_lock = threading.Lock()

    def readline(self) -> bytes:
        # Only the reader thread calls this, so no lock.
        return self.ser.readline()

    def write_line(self, text: str):
        with self.write_lock:
            self.ser.write((text + "\n").encode("ascii"))
            self.ser.flush()

    def close(self):
        # Callers stop the reader thread first (SerialReader.stop()).
        with self.write_lock:
            try:
                self.ser.close()
            except Exception:
                pass


# ------------------------------------------------------------------
# DATA RECORD PARSER
# ------------------------------------------------------------------
# classify_line() sorts every serial line into one of four kinds:
#   "record"   - a complete DATA line; returns (kind, raw_fields, values)
#   "header"   - the DATA,time_s,... header printed once at start-up
#   "rejected" - starts with DATA but is incomplete or unreadable
#   "other"    - anything else (start-up text, SAFETY or ERROR messages)
# raw_fields are the eleven strings exactly as the Arduino sent them (written to
# the CSV unchanged); values are the same fields converted to numbers.
def _to_float(text: str) -> float:
    value = float(text)                 # accepts "nan"
    if math.isinf(value):
        raise ValueError("infinite value")
    return value


def classify_line(line: str):
    if not line.startswith("DATA,"):
        return "other", None, None
    fields = [f.strip() for f in line.split(",")[1:]]
    if fields == DATA_COLUMNS:
        return "header", None, None
    if len(fields) != len(DATA_COLUMNS):
        return "rejected", None, None
    try:
        values = {
            "time_s": _to_float(fields[0]),
            "pwm": int(fields[7]),
            "heat_cool": int(fields[8]),
            "setpoint_C": _to_float(fields[9]),
            "safety": fields[10],
        }
        for i, name in enumerate(TEMPERATURE_COLUMNS):
            values[name] = _to_float(fields[1 + i])
    except ValueError:
        return "rejected", None, None
    if (math.isnan(values["time_s"]) or not 0 <= values["pwm"] <= PWM_MAX
            or values["heat_cool"] not in (0, 1)
            or values["safety"] not in ("OK", "SHUTDOWN")):
        return "rejected", None, None
    return "record", fields, values


class SerialReader(QtCore.QThread):
    line_received = QtCore.Signal(str)
    error = QtCore.Signal(str)

    def __init__(self, link):
        super().__init__()
        self.link = link
        self._stop = False

    def run(self):
        try:
            while not self._stop:
                raw = self.link.readline()
                if not raw:
                    continue
                line = raw.decode("utf-8", errors="replace").strip()
                if line:
                    self.line_received.emit(line)
        except Exception as e:
            self.error.emit(str(e))

    def stop(self):
        self._stop = True
        self.wait(1000)


# ------------------------------------------------------------------
# RAW DATA FILE + METADATA
# ------------------------------------------------------------------
def git_commit() -> str:
    """Short commit hash of the repository, with '+uncommitted changes' if dirty."""
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT,
                                capture_output=True, text=True, timeout=5).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_ROOT,
                               capture_output=True, text=True, timeout=5).stdout.strip()
        return (commit or "unknown") + (" +uncommitted changes" if dirty else "")
    except Exception:
        return "unknown"


class RunFiles:
    """One raw CSV and its metadata file. Opened with mode 'x', so an existing
    file is never overwritten."""

    def __init__(self, data_dir: Path):
        data_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        suffix = 0
        while True:
            name = f"rod_{stamp}" + (f"_{suffix}" if suffix else "")
            self.csv_path = data_dir / f"{name}.csv"
            self.meta_path = data_dir / f"{name}_meta.txt"
            try:
                self.csv_file = open(self.csv_path, "x", newline="")
                break
            except FileExistsError:
                suffix += 1
        self.meta_file = open(self.meta_path, "x")
        self.rows = 0

        # CSV header: exactly the eleven DATA fields.
        self.csv_file.write(",".join(DATA_COLUMNS) + "\n")
        self.csv_file.flush()

        # Metadata: everything needed to interpret this file later.
        m = self.meta_file
        m.write(f"Raw data file: {self.csv_path.name}\n")
        m.write(f"Created: {datetime.now().isoformat(timespec='seconds')}\n")
        m.write(f"Serial port: {SERIAL_PORT} at {BAUD_RATE} baud\n")
        m.write("Arduino sketch: arduino/module_07_rod_controller/module_07_rod_controller.ino\n")
        m.write("Python GUI: python/module_07_rod_acquisition_gui.py\n")
        m.write(f"Git commit: {git_commit()}\n")
        m.write("Units: time_s in s (Arduino clock since its last reset); *_C in degrees C; "
                "pwm 0-255; heat_cool 1 = heat, 0 = cool; setpoint_C as sent by this GUI "
                "(nan when not under control); safety OK or SHUTDOWN.\n")
        m.write("Temperatures are raw readings (no calibration corrections).\n")
        m.write(f"Channel map (x from the first thermistor hole, +/- {POSITION_UNCERTAINTY_MM} mm):\n")
        for col in TEMPERATURE_COLUMNS:
            where = ("TEC base" if col == "tec_C"
                     else f"x = {SENSOR_POSITIONS_CM[col]:.1f} cm")
            m.write(f"  {col}: {SENSOR_LABELS[col]}, input {ARDUINO_INPUTS[col]}, {where}\n")
        m.write("Events (Arduino time, then wall-clock time):\n")
        m.flush()

    def write_record(self, raw_fields):
        self.csv_file.write(",".join(raw_fields) + "\n")
        self.csv_file.flush()             # flush every record so nothing is lost
        self.rows += 1

    def event(self, arduino_time, text: str):
        t = "    ---  " if arduino_time is None else f"{arduino_time:9.2f} s"
        self.meta_file.write(f"  [{t} | {datetime.now().strftime('%H:%M:%S')}] {text}\n")
        self.meta_file.flush()

    def close(self):
        for f in (self.csv_file, self.meta_file):
            try:
                f.close()
            except Exception:
                pass


# ------------------------------------------------------------------
# GUI + PLOTS
# ------------------------------------------------------------------
class RodGUI(QtWidgets.QMainWindow):
    def __init__(self, link=None):
        super().__init__()
        self.setWindowTitle("Module 7 - Six-Thermistor Rod Acquisition with P/PI TEC Control")

        # ------- controller state (as in Module 6) -------
        self.control_on = False
        self.q = 0.0                 # integral state q (C s); zeroed only by the button
        self.t_prev = None           # Arduino time of the previous accepted record (s)
        self.t_offset = 0.0          # plot time = Arduino time + offset (grows if the Arduino resets)
        self.run = None              # gains and limits fixed for the current control run

        # ------- line counters -------
        self.n_accepted = 0
        self.n_rejected = 0

        # ------- in-memory data for the plots (whole session, never trimmed) -------
        self.ts = []                                       # plot time (s)
        self.temps = {col: [] for col in TEMPERATURE_COLUMNS}
        self.setpoints = []          # setpoint (C), NaN when control is off
        self.errors = []             # error (C), NaN when control is off
        self.u_ps = []               # u_P (PWM), NaN when control is off
        self.u_is = []               # u_I (PWM), NaN when control is off
        self.u_reqs = []             # requested command (PWM), NaN when control is off
        self.pwm_signed = []         # Arduino-reported signed PWM (cooling negative)

        # ------- open serial link (first, so a wrong port leaves no empty file) -------
        self.link = link if link is not None else SerialLink(SERIAL_PORT, BAUD_RATE)

        # ------- raw data file for this session -------
        self.files = RunFiles(DATA_DIR)
        print(f"[data] recording to {self.files.csv_path}")

        # ------- build the UI -------
        self._build_ui()
        self.update_file_label()

        # ------- start serial reader thread -------
        self.reader = SerialReader(self.link)
        self.reader.line_received.connect(self.on_line)
        self.reader.error.connect(self.on_serial_error)
        self.reader.start()

        # ------- plot update timer -------
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(PLOT_UPDATE_MS)

        # ------- manual command send debounce (as in Module 4) -------
        self.send_timer = QtCore.QTimer(self)
        self.send_timer.setSingleShot(True)
        self.send_timer.setInterval(SEND_DEBOUNCE_MS)
        self.send_timer.timeout.connect(self.send_manual_command)

        # Safety: PWM starts at zero (SET PWM 0 DIR HEAT at startup).
        self.schedule_send()

    # ---------------- build the GUI ----------------
    def _build_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)

        # --- manual controls (Module 4) ---
        manual_box = QtWidgets.QGroupBox("Manual (open loop)")
        row1 = QtWidgets.QHBoxLayout(manual_box)

        row1.addWidget(QtWidgets.QLabel("Direction:"))
        self.dir_combo = QtWidgets.QComboBox()
        self.dir_combo.addItems(["HEAT", "COOL"])
        self.dir_combo.currentIndexChanged.connect(self.schedule_send)
        row1.addWidget(self.dir_combo)

        row1.addSpacing(20)
        row1.addWidget(QtWidgets.QLabel("PWM:"))
        self.pwm_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.pwm_slider.setMinimum(0)
        self.pwm_slider.setMaximum(PWM_MAX)
        self.pwm_slider.setValue(0)
        self.pwm_slider.valueChanged.connect(self.on_slider_changed)
        row1.addWidget(self.pwm_slider, stretch=1)

        self.pwm_edit = QtWidgets.QLineEdit("0")
        self.pwm_edit.setFixedWidth(60)
        self.pwm_edit.editingFinished.connect(self.on_text_edited)
        row1.addWidget(self.pwm_edit)

        layout.addWidget(manual_box)

        # --- P/PI control (TEC thermistor only) ---
        pi_box = QtWidgets.QGroupBox(
            "P/PI control of the TEC thermistor:  u = Kp e + Ki q,   e = Tset - T_TEC,   q = sum of e dt")
        grid = QtWidgets.QGridLayout(pi_box)

        # setpoints: two fixed values, the active one can change during a run
        grid.addWidget(QtWidgets.QLabel("T low (C):"), 0, 0)
        self.low_spin = self._spin(SETPOINT_MIN_C, SETPOINT_MAX_C, 1, 0.5, SETPOINT_LOW_DEFAULT_C)
        grid.addWidget(self.low_spin, 0, 1)
        grid.addWidget(QtWidgets.QLabel("T high (C):"), 0, 2)
        self.high_spin = self._spin(SETPOINT_MIN_C, SETPOINT_MAX_C, 1, 0.5, SETPOINT_HIGH_DEFAULT_C)
        grid.addWidget(self.high_spin, 0, 3)
        grid.addWidget(QtWidgets.QLabel("Active Tset:"), 0, 4)
        self.low_button = QtWidgets.QPushButton("Tset = low")
        self.high_button = QtWidgets.QPushButton("Tset = high")
        self.setpoint_group = QtWidgets.QButtonGroup(self)
        for b in (self.low_button, self.high_button):
            b.setCheckable(True)
            self.setpoint_group.addButton(b)
        self.low_button.setChecked(True)
        self.setpoint_group.buttonClicked.connect(self.on_setpoint_selected)
        grid.addWidget(self.low_button, 0, 5)
        grid.addWidget(self.high_button, 0, 6)

        # gains, PWM limit, anti-windup
        grid.addWidget(QtWidgets.QLabel("Kp (PWM/C):"), 1, 0)
        self.kp_spin = self._spin(0.0, KP_MAX, 3, 0.1, KP_DEFAULT)
        grid.addWidget(self.kp_spin, 1, 1)
        grid.addWidget(QtWidgets.QLabel("Ki (PWM/(C s)):"), 1, 2)
        self.ki_spin = self._spin(0.0, KI_MAX, 3, 0.01, KI_DEFAULT)
        grid.addWidget(self.ki_spin, 1, 3)
        grid.addWidget(QtWidgets.QLabel("u_max (PWM):"), 1, 4)
        self.umax_spin = QtWidgets.QSpinBox()
        self.umax_spin.setRange(1, PWM_MAX)
        self.umax_spin.setValue(PWM_MAX)
        grid.addWidget(self.umax_spin, 1, 5)
        self.antiwindup_check = QtWidgets.QCheckBox("Anti-windup (conditional integration)")
        self.antiwindup_check.setChecked(True)
        grid.addWidget(self.antiwindup_check, 1, 6)

        self.zero_button = QtWidgets.QPushButton("Zero integral (q = 0)")
        self.zero_button.clicked.connect(self.zero_integral)
        grid.addWidget(self.zero_button, 2, 5)
        self.control_button = QtWidgets.QPushButton("Start control")
        self.control_button.clicked.connect(self.on_control_button)
        grid.addWidget(self.control_button, 2, 6)

        layout.addWidget(pi_box)

        # --- data file, line counters, notes ---
        file_box = QtWidgets.QGroupBox("Raw data")
        frow = QtWidgets.QHBoxLayout(file_box)
        self.lbl_file = QtWidgets.QLabel()
        frow.addWidget(self.lbl_file)
        self.lbl_counts = QtWidgets.QLabel("DATA accepted: 0   rejected: 0")
        frow.addWidget(self.lbl_counts)
        frow.addStretch(1)
        self.note_edit = QtWidgets.QLineEdit()
        self.note_edit.setPlaceholderText("Note for the metadata file (e.g. 'baseline at 20 C begins')")
        self.note_edit.setMinimumWidth(320)
        self.note_edit.returnPressed.connect(self.add_note)
        frow.addWidget(self.note_edit)
        self.note_button = QtWidgets.QPushButton("Add note")
        self.note_button.clicked.connect(self.add_note)
        frow.addWidget(self.note_button)
        self.new_file_button = QtWidgets.QPushButton("New data file")
        self.new_file_button.clicked.connect(self.new_data_file)
        frow.addWidget(self.new_file_button)
        layout.addWidget(file_box)

        # --- live values: six temperatures, then controller values ---
        row_t = QtWidgets.QHBoxLayout()
        self.lbl_temps = {}
        self.show_checks = {}
        for col in TEMPERATURE_COLUMNS:
            color, _ = TRACE_STYLE[col]
            check = QtWidgets.QCheckBox()
            check.setChecked(True)
            check.toggled.connect(self.update_trace_visibility)
            self.show_checks[col] = check
            lbl = QtWidgets.QLabel(f"{SENSOR_LABELS[col]}: --- C")
            css = color if isinstance(color, str) else "rgb({},{},{})".format(*color)
            lbl.setStyleSheet(f"color: {'black' if css == 'k' else css}; font-weight: bold;")
            self.lbl_temps[col] = lbl
            row_t.addWidget(check)
            row_t.addWidget(lbl)
            row_t.addSpacing(12)
        row_t.addStretch(1)
        layout.addLayout(row_t)

        row3 = QtWidgets.QHBoxLayout()
        self.lbl_tset = QtWidgets.QLabel("Tset: ---")
        self.lbl_error = QtWidgets.QLabel("e: ---")
        self.lbl_up = QtWidgets.QLabel("u_P: ---")
        self.lbl_ui = QtWidgets.QLabel("u_I: ---")
        self.lbl_ureq = QtWidgets.QLabel("u_req: ---")
        self.lbl_u = QtWidgets.QLabel("applied: ---")
        self.lbl_q = QtWidgets.QLabel("q: 0.0 C s")
        self.lbl_dt = QtWidgets.QLabel("dt: ---")
        self.lbl_state = QtWidgets.QLabel("")
        for lbl in (self.lbl_tset, self.lbl_error, self.lbl_up, self.lbl_ui,
                    self.lbl_ureq, self.lbl_u, self.lbl_q, self.lbl_dt, self.lbl_state):
            row3.addWidget(lbl)
        row3.addStretch(1)
        layout.addLayout(row3)

        row4 = QtWidgets.QHBoxLayout()
        self.lbl_pwm = QtWidgets.QLabel("Arduino PWM: ---")
        self.lbl_dir = QtWidgets.QLabel("Direction: ---")
        self.lbl_time = QtWidgets.QLabel("Time: --- s")
        self.lbl_safety = QtWidgets.QLabel("Safety: ---")
        for lbl in (self.lbl_pwm, self.lbl_dir, self.lbl_time, self.lbl_safety):
            row4.addWidget(lbl)
        row4.addStretch(1)
        row4.addWidget(QtWidgets.QLabel(
            "Plots: wheel = zoom (over an axis: that axis only), drag = pan, right-click = menu"))
        self.show_all_button = QtWidgets.QPushButton("Show all")
        self.show_all_button.clicked.connect(self.show_all)
        row4.addWidget(self.show_all_button)
        layout.addLayout(row4)

        # --- temperature plot: six channels and the setpoint ---
        self.temp_plot = pg.PlotWidget()
        self.temp_plot.setLabel("left", "Temperature (C)")
        self.temp_plot.addLegend(offset=(10, 10))
        self.temp_curves = {}
        for col in TEMPERATURE_COLUMNS:
            color, width = TRACE_STYLE[col]
            self.temp_curves[col] = self.temp_plot.plot(
                pen=pg.mkPen(color, width=width), connect="finite", name=SENSOR_LABELS[col])
        self.setpoint_curve = self.temp_plot.plot(
            pen=pg.mkPen("g", width=2, style=QtCore.Qt.DashLine),
            connect="finite", name="Tset",
        )
        self.temp_plot.getViewBox().setLimits(minYRange=TEMP_MIN_Y_SPAN)
        layout.addWidget(self.temp_plot, stretch=3)

        # --- command plot: u_P, u_I, requested, and the PWM the Arduino applied ---
        self.cmd_plot = pg.PlotWidget()
        self.cmd_plot.setLabel("left", "Signed PWM")
        self.cmd_plot.addLegend(offset=(10, 10))
        self.pwm_curve = self.cmd_plot.plot(pen=pg.mkPen("k", width=2),
                                            name="applied (Arduino; cooling negative)")
        self.up_curve = self.cmd_plot.plot(pen=pg.mkPen("b", width=1.5),
                                           connect="finite", name="u_P")
        self.ui_curve = self.cmd_plot.plot(pen=pg.mkPen((255, 140, 0), width=2),
                                           connect="finite", name="u_I")
        self.ureq_curve = self.cmd_plot.plot(
            pen=pg.mkPen((128, 128, 128), width=1.5, style=QtCore.Qt.DashLine),
            connect="finite", name="requested u_P + u_I")
        self.cmd_plot.addLine(y=0, pen=pg.mkPen((160, 160, 160), width=1)).setZValue(-10)
        self.umax_lines = []
        for sign in (1, -1):
            line = pg.InfiniteLine(pos=sign * PWM_MAX, angle=0,
                                   pen=pg.mkPen("r", width=1, style=QtCore.Qt.DotLine))
            self.cmd_plot.addItem(line, ignoreBounds=True)   # keep it out of auto-range
            self.umax_lines.append(line)
        layout.addWidget(self.cmd_plot, stretch=1)

        # --- error plot ---
        self.error_plot = pg.PlotWidget()
        self.error_plot.setLabel("bottom", "Arduino time (s)")
        self.error_plot.setLabel("left", "e = Tset - T_TEC (C)")
        self.error_plot.addLine(y=0, pen=pg.mkPen("k", width=1)).setZValue(-10)
        self.error_curve = self.error_plot.plot(pen=pg.mkPen("m", width=2), connect="finite")
        layout.addWidget(self.error_plot, stretch=1)

        # All three plots share the time axis. Auto-range shows the whole session;
        # zooming or panning one plot turns auto-range off until "Show all".
        self.plots = (self.temp_plot, self.cmd_plot, self.error_plot)
        for p in self.plots:
            p.showGrid(x=True, y=True, alpha=0.3)
            if p is not self.temp_plot:
                p.setXLink(self.temp_plot)

        self.resize(1300, 1000)

    def _spin(self, low, high, decimals, step, value):
        spin = QtWidgets.QDoubleSpinBox()
        spin.setRange(low, high)
        spin.setDecimals(decimals)
        spin.setSingleStep(step)
        spin.setValue(value)
        return spin

    # ---------------- data file, notes, counters ----------------
    def update_file_label(self):
        self.lbl_file.setText(f"File: {self.files.csv_path.name}  ({self.files.rows} rows)")

    def update_counts(self):
        self.lbl_counts.setText(
            f"DATA accepted: {self.n_accepted}   rejected: {self.n_rejected}")

    def add_note(self):
        text = self.note_edit.text().strip()
        if not text:
            return
        self.files.event(self.t_prev, f"NOTE: {text}")
        self.note_edit.clear()
        print(f"[note] {text}")

    def new_data_file(self):
        # Only while control is off (the button is disabled during a run).
        old = self.files
        self.files = RunFiles(DATA_DIR)
        old.event(self.t_prev, f"closed; continued in {self.files.csv_path.name}")
        old.close()
        self.files.event(self.t_prev, f"continues {old.csv_path.name}")
        self.update_file_label()
        print(f"[data] saved {old.csv_path.name} ({old.rows} rows); "
              f"now recording to {self.files.csv_path}")

    # ---------------- manual control callbacks ----------------
    def on_slider_changed(self, value: int):
        if self.pwm_edit.text() != str(value):
            self.pwm_edit.setText(str(value))
        self.schedule_send()

    def on_text_edited(self):
        text = self.pwm_edit.text().strip()
        try:
            value = int(text)
        except ValueError:
            value = self.pwm_slider.value()
        value = max(0, min(PWM_MAX, value))
        self.pwm_edit.setText(str(value))
        if self.pwm_slider.value() != value:
            self.pwm_slider.setValue(value)   # triggers on_slider_changed
        else:
            self.schedule_send()

    def schedule_send(self):
        self.send_timer.start()

    def send_manual_command(self, echo: bool = True):
        # Manual commands are ignored while the controller owns the output.
        if self.control_on:
            return
        pwm = self.pwm_slider.value()
        direction = self.dir_combo.currentText()
        self.send_line(f"SET PWM {pwm} DIR {direction}", echo)

    def send_line(self, cmd: str, echo: bool = True):
        try:
            self.link.write_line(cmd)
            if echo:
                print(f"[sent] {cmd}")
        except Exception as e:
            print(f"[send error] {e}")

    # ---------------- setpoint and integral ----------------
    def active_setpoint(self) -> float:
        if self.control_on:
            return self.run["low"] if self.low_button.isChecked() else self.run["high"]
        return self.low_spin.value() if self.low_button.isChecked() else self.high_spin.value()

    def on_setpoint_selected(self, _button):
        if self.control_on:
            t = self.t_prev if self.t_prev is not None else float("nan")
            print(f"[setpoint] t = {t:.2f} s: Tset -> {self.active_setpoint():.2f} C")
            self.files.event(self.t_prev, f"setpoint -> {self.active_setpoint():.2f} C")

    def zero_integral(self):
        # Only reachable while control is off (the button is disabled during a
        # run), i.e. with the controller's PWM already at 0.
        self.q = 0.0
        self.lbl_q.setText("q: 0.0 C s")
        print("[integral] q = 0")

    # ---------------- control start / stop ----------------
    def on_control_button(self):
        if self.control_on:
            self.stop_control("stopped by user")
        else:
            self.start_control()

    def start_control(self):
        if self.q != 0.0:
            QtWidgets.QMessageBox.warning(
                self, "Integral not zero",
                f"q = {self.q:.1f} C s from the previous run.\n"
                "Press 'Zero integral' before starting a new run.")
            return
        low, high = self.low_spin.value(), self.high_spin.value()
        if not low < high:
            QtWidgets.QMessageBox.warning(self, "Setpoints",
                                          "T low must be below T high.")
            return
        self.run = {
            "low": low, "high": high,
            "kp": self.kp_spin.value(), "ki": self.ki_spin.value(),
            "u_max": float(self.umax_spin.value()),
            "anti_windup": self.antiwindup_check.isChecked(),
        }
        self.control_on = True
        self.send_timer.stop()
        # Gains, limit, anti-windup, and the two setpoints stay fixed for the run;
        # only the active setpoint (low/high) can be switched.
        for w in (self.low_spin, self.high_spin, self.kp_spin, self.ki_spin,
                  self.umax_spin, self.antiwindup_check, self.zero_button,
                  self.dir_combo, self.pwm_slider, self.pwm_edit, self.new_file_button):
            w.setEnabled(False)
        for line, sign in zip(self.umax_lines, (1, -1)):
            line.setValue(sign * self.run["u_max"])
        self.control_button.setText("Stop control (PWM 0)")
        r = self.run
        text = (f"control START  Tset = {self.active_setpoint():.2f} C (low {low:g}, high {high:g}), "
                f"Kp = {r['kp']:g} PWM/C, Ki = {r['ki']:g} PWM/(C s), u_max = {r['u_max']:g}, "
                f"anti-windup {'on' if r['anti_windup'] else 'off'}")
        self.files.event(self.t_prev, text)
        print(f"[control] {text}")

    def stop_control(self, reason: str):
        if not self.control_on:
            return
        self.control_on = False
        self.send_line("SET PWM 0 DIR HEAT")
        self.send_line("SETPOINT OFF")
        self.files.event(self.t_prev, f"control STOP ({reason}); q = {self.q:.1f} C s")
        print(f"[control] STOP ({reason}). q = {self.q:.1f} C s.")

        # Back to manual mode at PWM 0. q keeps its value until "Zero integral".
        self.pwm_slider.blockSignals(True)
        self.pwm_slider.setValue(0)
        self.pwm_slider.blockSignals(False)
        self.pwm_edit.setText("0")
        self.dir_combo.blockSignals(True)
        self.dir_combo.setCurrentText("HEAT")
        self.dir_combo.blockSignals(False)
        for w in (self.low_spin, self.high_spin, self.kp_spin, self.ki_spin,
                  self.umax_spin, self.antiwindup_check, self.zero_button,
                  self.dir_combo, self.pwm_slider, self.pwm_edit, self.new_file_button):
            w.setEnabled(True)
        self.control_button.setText("Start control")
        for lbl, text in ((self.lbl_error, "e: ---"), (self.lbl_up, "u_P: ---"),
                          (self.lbl_ui, "u_I: ---"), (self.lbl_ureq, "u_req: ---"),
                          (self.lbl_u, "applied: ---"), (self.lbl_tset, "Tset: ---"),
                          (self.lbl_state, "")):
            lbl.setText(text)
        self.lbl_state.setStyleSheet("")

    # ---------------- one line received ----------------
    @QtCore.Slot(str)
    def on_line(self, line: str):
        kind, raw_fields, rec = classify_line(line)
        if kind == "other":
            # Start-up text, SAFETY and ERROR messages: print, and log the
            # safety and error messages in the metadata file.
            print(f"[arduino] {line}")
            if "SAFETY" in line.upper() or "ERROR" in line.upper():
                self.files.event(self.t_prev, f"Arduino: {line}")
            return
        if kind == "header":
            return
        if kind == "rejected":
            self.n_rejected += 1
            self.update_counts()
            print(f"[rejected] {line}")
            return

        # ---- an accepted DATA record: save it exactly as received ----
        self.n_accepted += 1
        self.files.write_record(raw_fields)
        self.update_counts()
        self.update_file_label()

        t = rec["time_s"]
        T = rec["tec_C"]
        pwm_ard = rec["pwm"]
        hc = rec["heat_cool"]
        safety = rec["safety"] == "SHUTDOWN"

        # dt = actual elapsed time since the previous accepted record (Arduino
        # clock). A reset Arduino starts its clock again; then no integration and
        # the plots continue to the right instead of drawing over earlier records.
        dt = 0.0 if self.t_prev is None else t - self.t_prev
        if dt < 0.0:
            print(f"[warning] Arduino time went back ({self.t_prev:.2f} -> {t:.2f} s): "
                  "the Arduino restarted; dt set to 0")
            self.files.event(t, f"Arduino restarted (time went back from {self.t_prev:.2f} s)")
            dt = 0.0
            if self.ts:
                self.t_offset = self.ts[-1] + 1.0 - t
        self.t_prev = t

        setpoint = error = u_p = u_i = u_req = float("nan")

        if self.control_on and math.isnan(T):
            # No valid TEC reading: the Arduino has shut the TEC off. Stop control.
            self.stop_control("no valid TEC reading")
        elif self.control_on:
            r = self.run
            setpoint = self.active_setpoint()
            step = pi_control(setpoint, T, self.q, dt, r["kp"], r["ki"],
                              r["u_max"], r["anti_windup"])
            self.q = step.q
            error, u_p, u_i, u_req = step.e, step.u_p, step.u_i, step.u_req

            if safety:
                # The Arduino has already forced PWM to 0. Do not keep
                # commanding the TEC: leave control and require a restart.
                self.stop_control("Arduino safety shutdown")
            else:
                self.send_line(f"SETPOINT {setpoint:.2f}", echo=False)
                self.send_line(f"SET PWM {step.pwm} DIR {step.direction}", echo=False)
                self.lbl_tset.setText(f"Tset: {setpoint:.2f} C")
                self.lbl_error.setText(f"e: {step.e:+.2f} C")
                self.lbl_up.setText(f"u_P: {step.u_p:+.1f}")
                self.lbl_ui.setText(f"u_I: {step.u_i:+.1f}")
                self.lbl_ureq.setText(f"u_req: {step.u_req:+.1f}")
                self.lbl_u.setText(f"applied: {step.u_applied:+.1f} (PWM {step.pwm} {step.direction})")
                flags = [name for name, on in (("SATURATED", step.saturated),
                                               ("INTEGRAL HELD", step.held)) if on]
                self.lbl_state.setText("  ".join(flags))
                self.lbl_state.setStyleSheet(
                    "color: white; background-color: darkorange; font-weight: bold; padding: 2px;"
                    if flags else "")
        else:
            if safety and self.pwm_slider.value() != 0:
                # Keep the Module 4 behaviour: after a safety shutdown the
                # TEC stays off until the user sets a new PWM.
                self.pwm_slider.blockSignals(True)
                self.pwm_slider.setValue(0)
                self.pwm_slider.blockSignals(False)
                self.pwm_edit.setText("0")
            # Re-send the manual command once per record so the Arduino's
            # command timeout does not stop an open-loop run.
            self.send_manual_command(echo=False)

        print(f"t = {t:.2f} s, " + ", ".join(
            f"{SENSOR_LABELS[c]} {rec[c]:.2f}" for c in TEMPERATURE_COLUMNS)
            + f" C, PWM {pwm_ard} {'HEAT' if hc else 'COOL'}, {rec['safety']}")

        # Store for the plots
        self.ts.append(t + self.t_offset)
        for col in TEMPERATURE_COLUMNS:
            self.temps[col].append(rec[col])
        self.setpoints.append(setpoint)
        self.errors.append(error)
        self.u_ps.append(u_p)
        self.u_is.append(u_i)
        self.u_reqs.append(u_req)
        self.pwm_signed.append(pwm_ard if hc == 1 else -pwm_ard)

        # Update the live labels
        for col in TEMPERATURE_COLUMNS:
            value = rec[col]
            text = "nan (check sensor)" if math.isnan(value) else f"{value:.2f} C"
            self.lbl_temps[col].setText(f"{SENSOR_LABELS[col]}: {text}")
        self.lbl_q.setText(f"q: {self.q:+.1f} C s")
        self.lbl_dt.setText(f"dt: {dt:.2f} s")
        self.lbl_pwm.setText(f"Arduino PWM: {pwm_ard}")
        self.lbl_dir.setText(f"Direction: {'HEAT' if hc == 1 else 'COOL'}")
        self.lbl_time.setText(f"Time: {t:.2f} s")
        if safety:
            self.lbl_safety.setText("SAFETY SHUTDOWN ACTIVE - PWM forced to 0")
            self.lbl_safety.setStyleSheet(
                "color: white; background-color: red; font-weight: bold; padding: 2px;"
            )
        else:
            self.lbl_safety.setText("Safety: OK")
            self.lbl_safety.setStyleSheet("")

    @QtCore.Slot(str)
    def on_serial_error(self, msg: str):
        print(f"[serial error] {msg}")
        self.files.event(self.t_prev, f"serial error: {msg}")
        if self.control_on:
            # The zero command may not reach the Arduino.
            self.stop_control("serial error")

    # ---------------- plot updates ----------------
    def update_trace_visibility(self):
        for col, check in self.show_checks.items():
            self.temp_curves[col].setVisible(check.isChecked())

    def update_plots(self):
        # The whole session is drawn. pyqtgraph auto-ranges to all of it until
        # the user zooms or pans; "Show all" turns auto-range back on.
        if not self.ts:
            return
        xs = self.ts
        for col in TEMPERATURE_COLUMNS:
            self.temp_curves[col].setData(xs, self.temps[col])
        self.setpoint_curve.setData(xs, self.setpoints)
        self.up_curve.setData(xs, self.u_ps)
        self.ui_curve.setData(xs, self.u_is)
        self.ureq_curve.setData(xs, self.u_reqs)
        self.pwm_curve.setData(xs, self.pwm_signed)
        self.error_curve.setData(xs, self.errors)

    def show_all(self):
        for p in self.plots:
            p.enableAutoRange()

    # ---------------- clean shutdown ----------------
    def closeEvent(self, event):
        self.stop_control("GUI closed")
        self.timer.stop()
        self.send_timer.stop()
        self.reader.stop()
        self.link.close()
        self.files.event(self.t_prev, "GUI closed")
        self.files.close()
        print(f"[data] saved {self.files.csv_path} ({self.files.rows} rows)")
        super().closeEvent(event)


# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------
def main():
    app = QtWidgets.QApplication(sys.argv)
    # Same white plot background as the earlier GUIs.
    pg.setConfigOptions(background="w", foreground="k")
    try:
        window = RodGUI()
    except serial.SerialException as e:
        # Wrong port name, Arduino unplugged, or the port is held by another
        # program (usually the Arduino Serial Monitor): list the ports and stop.
        from serial.tools import list_ports
        ports = [p.device for p in list_ports.comports()]
        print(f"\nCould not open SERIAL_PORT = {SERIAL_PORT!r}:\n  {e}")
        print("Serial ports on this computer: "
              + (", ".join(ports) if ports else "none (is the Arduino plugged in?)"))
        print("Set SERIAL_PORT at the top of this file to the Arduino's port "
              "(a Mac name starts with /dev/cu.), and close the Arduino Serial Monitor.")
        sys.exit(1)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
