# Phys 39 Module 7 - shared definitions for the rod acquisition GUI and analysis
#
#   - repository paths for data and figures
#   - the DATA record fields sent by arduino/module_07_rod_controller
#   - reading one raw run CSV written by python/module_07_rod_acquisition_gui.py

import csv
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE7_DATA_DIR = REPO_ROOT / "data" / "module_07"
MODULE7_FIG_DIR = REPO_ROOT / "docs" / "figures" / "module_07"

# Fields of one Arduino DATA record, in order. These are also the CSV columns.
DATA_COLUMNS = [
    "time_s", "tec_C", "rod1_C", "rod2_C", "rod3_C", "rod4_C", "rod5_C",
    "pwm", "heat_cool", "setpoint_C", "safety",
]
TEMPERATURE_COLUMNS = ["tec_C", "rod1_C", "rod2_C", "rod3_C", "rod4_C", "rod5_C"]
ROD_COLUMNS = TEMPERATURE_COLUMNS[1:]
SENSOR_LABELS = {"tec_C": "TEC", "rod1_C": "T1", "rod2_C": "T2",
                 "rod3_C": "T3", "rod4_C": "T4", "rod5_C": "T5"}
ARDUINO_INPUTS = {"tec_C": "A0", "rod1_C": "A1", "rod2_C": "A2",
                  "rod3_C": "A3", "rod4_C": "A4", "rod5_C": "A5"}


def read_rod_csv(path: Path):
    """Read one raw run CSV into numpy arrays (nan for missing readings).

    The safety column is returned as a string array; every other column is float.
    """
    cols = {name: [] for name in DATA_COLUMNS}
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in DATA_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise ValueError(f"{path}: missing columns {missing}")
        for row in reader:
            for name in DATA_COLUMNS:
                cols[name].append(row[name])
    out = {}
    for name, values in cols.items():
        if name == "safety":
            out[name] = np.array(values)
        else:
            out[name] = np.array([float(v) for v in values])
    return out
