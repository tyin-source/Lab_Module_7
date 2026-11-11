# Phys 39 Module 7: self-test of the rod acquisition GUI without hardware
#
# Runs module_07_rod_acquisition_gui.py off screen against a simulated Arduino
# that prints the Module 7 DATA records: a one-lump TEC (tau = 70 s) driven by the
# last SET PWM command, and five rod sensors that follow it with growing lags and
# shrinking amplitudes. Checks:
#   1. the header, start-up text, and safety messages are not counted, malformed
#      DATA lines are counted as rejected, and the program keeps running
#   2. the raw CSV has exactly the eleven DATA columns and one row per accepted
#      record, identical to the fields the Arduino sent (nan included)
#   3. a PI step from 20 C to 45 C on the TEC thermistor settles near 45 C and
#      the GUI sends SETPOINT before each SET PWM
#   4. a SHUTDOWN record stops control and sends SET PWM 0 and SETPOINT OFF
#   5. "New data file" starts a new CSV and metadata file, and a second file
#      created in the same second gets a new name instead of overwriting
# Data files go to a temporary folder, not data/module_07/.
#
# Usage (from the repository root):
#   python python/module_07_gui_selftest.py

import contextlib
import csv
import io
import os
import sys
import tempfile
import time
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6 import QtWidgets
import pyqtgraph as pg

import module_07_rod_acquisition_gui as gui_module
from module_07_common import DATA_COLUMNS

T_AMB = 20.0
TAU_TEC = 70.0                       # s
CHI = 0.30                           # C per PWM count, both directions
ROD_GAIN = [0.95, 0.80, 0.69, 0.61, 0.56]   # steady fraction of the TEC excess
ROD_TAU = [40.0, 90.0, 160.0, 230.0, 300.0]  # s, slower farther along the rod


class SimulatedArduino:
    """Fake serial link and simulated TEC + rod in one object."""

    def __init__(self):
        self.pwm, self.heat, self.sent = 0, True, []
        self.t = 0.0
        self.tec = T_AMB
        self.rod = [T_AMB] * 5
        self.setpoint = "nan"
        self.missing = set()          # rod indices that read nan (unplugged)

    # serial link interface used by the GUI
    def readline(self):
        time.sleep(0.05)
        return b""

    def write_line(self, text):
        self.sent.append(text)
        words = text.split()
        if words[0] == "SETPOINT":
            self.setpoint = "nan" if words[1] == "OFF" else f"{float(words[1]):.2f}"
        else:
            self.pwm, self.heat = int(words[2]), words[4] == "HEAT"

    def close(self):
        pass

    # one ~1 s average with the last command applied, then one DATA record
    def record(self, safety="OK"):
        u = self.pwm if self.heat else -self.pwm
        for _ in range(100):
            self.tec += 0.01 / TAU_TEC * (T_AMB + CHI * u - self.tec)
            for i in range(5):
                target = T_AMB + ROD_GAIN[i] * (self.tec - T_AMB)
                self.rod[i] += 0.01 / ROD_TAU[i] * (target - self.rod[i])
        self.t += 1.0
        rods = ["nan" if i in self.missing else f"{v:.2f}" for i, v in enumerate(self.rod)]
        fields = [f"{self.t:.2f}", f"{self.tec:.2f}", *rods, str(self.pwm),
                  str(int(self.heat)), self.setpoint, safety]
        return "DATA," + ",".join(fields)


def feed(app, gui, lines):
    sent_records = []
    with contextlib.redirect_stdout(io.StringIO()):
        for line in lines:
            gui.on_line(line)
            if line.startswith("DATA,") and not line.startswith("DATA,time_s"):
                sent_records.append(line)
            app.processEvents()
    return sent_records


def run_records(app, gui, arduino, n, **kw):
    return feed(app, gui, (arduino.record(**kw) for _ in range(n)))


def check(name, ok, detail=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {name}" + (f": {detail}" if detail else ""))
    return ok


def main():
    app = QtWidgets.QApplication(sys.argv)
    pg.setConfigOptions(background="w", foreground="k")
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        gui_module.DATA_DIR = Path(tmp)
        arduino = SimulatedArduino()
        with contextlib.redirect_stdout(io.StringIO()):
            gui = gui_module.RodGUI(link=arduino)
        first_csv = gui.files.csv_path

        # 1. start-up text, header, records, malformed lines, messages
        startup = ["Module 7 six-thermistor rod acquisition (P/PI control runs in Python)",
                   "DATA," + ",".join(DATA_COLUMNS)]
        feed(app, gui, startup)
        good = run_records(app, gui, arduino, 30)
        bad = ["DATA,31.00,24.1,23.9",                                    # too few fields
               "DATA,32.00,abc,20,20,20,20,20,0,1,nan,OK",                 # not a number
               "DATA,33.00,20,20,20,20,20,20,999,1,nan,OK",                # PWM out of range
               "DATA,34.00,20,20,20,20,20,20,0,1,nan,MAYBE",               # bad safety field
               "SAFETY: no command for 3.0 s. Both H-bridge PWM outputs set to 0."]
        feed(app, gui, bad)
        arduino.missing = {2}                                              # T3 unplugged
        good += run_records(app, gui, arduino, 5)
        arduino.missing = set()
        results.append(check("accepted and rejected counts",
                             gui.n_accepted == 35 and gui.n_rejected == 4,
                             f"accepted {gui.n_accepted}, rejected {gui.n_rejected}"))
        results.append(check("T3 nan shown without stopping",
                             "nan" in gui.lbl_temps["rod3_C"].text()))

        # 3. PI step 20 C -> 45 C on the TEC thermistor
        gui.low_spin.setValue(20.0)
        gui.high_spin.setValue(45.0)
        gui.kp_spin.setValue(6.0)
        gui.ki_spin.setValue(0.04)
        gui.high_button.click()
        with contextlib.redirect_stdout(io.StringIO()):
            gui.control_button.click()
        n_before = len(arduino.sent)
        good += run_records(app, gui, arduino, 1500)
        tec_final = arduino.tec
        sent = arduino.sent[n_before:]
        pairs_ok = all(a.startswith("SETPOINT 45.00") and b.startswith("SET PWM")
                       for a, b in zip(sent[0::2], sent[1::2]))
        results.append(check("PI step settles at 45 C", abs(tec_final - 45.0) < 0.3,
                             f"TEC {tec_final:.2f} C after 1500 s"))
        results.append(check("SETPOINT sent before each SET PWM", pairs_ok and len(sent) == 3000))

        # 4. safety shutdown record stops control
        n_before = len(arduino.sent)
        good += run_records(app, gui, arduino, 1, safety="SHUTDOWN")
        results.append(check("SHUTDOWN stops control",
                             not gui.control_on and
                             arduino.sent[n_before:] == ["SET PWM 0 DIR HEAT", "SETPOINT OFF"],
                             str(arduino.sent[n_before:])))

        # 2. raw CSV equals the accepted records
        gui.note_edit.setText("self-test note")
        with contextlib.redirect_stdout(io.StringIO()):
            gui.note_button.click()
            gui.new_data_file()
        second_csv = gui.files.csv_path
        with open(first_csv, newline="") as f:
            rows = list(csv.reader(f))
        expected = [line.split(",")[1:] for line in good]
        results.append(check("CSV header is the eleven DATA columns", rows[0] == DATA_COLUMNS))
        results.append(check("CSV rows identical to the accepted records",
                             rows[1:] == expected, f"{len(rows) - 1} rows"))
        meta = first_csv.with_name(first_csv.stem + "_meta.txt").read_text()
        results.append(check("metadata has channel map and events",
                             all(s in meta for s in ("rod3_C: T3, input A3, x = 10.2 cm",
                                                     "control START", "control STOP",
                                                     "NOTE: self-test note",
                                                     second_csv.name))))

        # 5. new file and no overwrite
        good2 = run_records(app, gui, arduino, 3)
        third = gui_module.RunFiles(Path(tmp))
        third.close()
        with contextlib.redirect_stdout(io.StringIO()):
            gui.close()
        with open(second_csv, newline="") as f:
            rows2 = list(csv.reader(f))
        results.append(check("new data file receives the next records",
                             second_csv != first_csv and len(rows2) == 1 + len(good2)))
        results.append(check("a file created in the same second is not overwritten",
                             third.csv_path not in (first_csv, second_csv),
                             third.csv_path.name))

    passed = all(results)
    print("PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
