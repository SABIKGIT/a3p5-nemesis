"""Read-only helpers for checking the archived analytical study."""
from __future__ import annotations

import csv
from datetime import datetime
from functools import lru_cache
import hashlib
import io
import json
import math
import os
from pathlib import Path
import unittest
import zipfile

ROOT = Path(os.environ.get("A3P5_VERIFY_ROOT", Path(__file__).resolve().parents[1]))
MANUSCRIPT = ROOT / "manuscript"
ANALYSIS = MANUSCRIPT / "analysis"
ML = ANALYSIS / "ml_outputs"
FEATURES = ["PT08.S1(CO)", "PT08.S2(NMHC)", "PT08.S3(NOx)",
            "PT08.S4(NO2)", "PT08.S5(O3)", "T", "RH", "AH"]
TARGET = "CO(GT)"
ARCHIVE_SHA256 = "d4a64013fb385288a8a48d9d193ca7079b2e1bbddf6f8d458feb8c08ab2b8a2a"
FAMILIES = ["DummyMean", "Ridge", "RandomForest", "HistGradientBoosting"]


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def rows(path):
    with Path(path).open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def number(value):
    return float(value) if value not in ("", None) else math.nan


def percentile(values, q):
    """Linear interpolation, the convention used in the published analysis."""
    data = sorted(values)
    index = (len(data) - 1) * q
    lo = int(index)
    hi = min(lo + 1, len(data) - 1)
    return data[lo] + (index - lo) * (data[hi] - data[lo])


def scores(target, prediction):
    n = len(target)
    error = [p - y for p, y in zip(prediction, target)]
    squared = math.fsum(e * e for e in error)
    mean = math.fsum(target) / n
    total = math.fsum((y - mean) ** 2 for y in target)
    return {"MAE": math.fsum(map(abs, error)) / n,
            "RMSE": math.sqrt(squared / n),
            "R2": 1 - squared / total,
            "Bias": math.fsum(error) / n}


@lru_cache(maxsize=1)
def archive_data():
    """Parse the original CSV independently, without pandas or interpolation."""
    path = MANUSCRIPT / "research" / "air_quality.zip"
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != ARCHIVE_SHA256:
        raise AssertionError(f"Unexpected UCI archive SHA256: {digest}")
    with zipfile.ZipFile(path) as archive:
        data = archive.read("AirQualityUCI.csv")
    raw = list(csv.DictReader(io.StringIO(data.decode("utf-8-sig")), delimiter=";"))
    valid, eligible = [], []
    for line, record in enumerate(raw, start=2):
        try:
            stamp = datetime.strptime(record["Date"] + " " + record["Time"],
                                      "%d/%m/%Y %H.%M.%S")
        except ValueError:
            continue
        out = {"timestamp": stamp, "source_row": line}
        for key in [TARGET] + FEATURES:
            value = float(record[key].replace(",", ".")) if record[key] else math.nan
            out[key] = math.nan if value == -200 else value
        valid.append(out)
        if math.isfinite(out[TARGET]) and any(math.isfinite(out[k]) for k in FEATURES):
            eligible.append(out)
    valid.sort(key=lambda r: r["timestamp"])
    eligible.sort(key=lambda r: r["timestamp"])
    return raw, valid, eligible, hashlib.sha256(data).hexdigest()


class NumericCase(unittest.TestCase):
    def assertClose(self, actual, expected, *, atol=1e-10, rtol=1e-10, context=""):
        actual, expected = float(actual), float(expected)
        if math.isnan(expected):
            self.assertTrue(math.isnan(actual), context)
        else:
            self.assertTrue(math.isclose(actual, expected, abs_tol=atol, rel_tol=rtol),
                            f"{context}: actual={actual!r}, expected={expected!r}")
