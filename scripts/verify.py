#!/usr/bin/env python3
"""Portable, read-only archive verification; optional numerical replay is explicit."""
from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import sys
import time
import unittest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1],
                        help="repository root (defaults to the parent of scripts/)")
    parser.add_argument("--models", action="store_true", help="replay trusted saved models and test leakage guards")
    parser.add_argument("--refit", action="store_true", help="also retrain all 21 candidates; implies --models")
    parser.add_argument("--regenerate-engineering", action="store_true", help="run the engineering analysis in a temporary directory")
    parser.add_argument("--json", type=Path, help="optional output path for the verification report")
    args = parser.parse_args()
    root = args.root.resolve()
    if not (root / "manuscript/analysis/analysis_results.json").is_file():
        parser.error("--root must contain manuscript/analysis/analysis_results.json")
    models = args.models or args.refit
    required = set()
    if models:
        required.update(["numpy", "pandas", "scipy", "sklearn", "joblib"])
    if args.regenerate_engineering:
        required.update(["numpy", "matplotlib"])
    missing = [name for name in sorted(required) if importlib.util.find_spec(name) is None]
    if missing:
        parser.error("Missing dependencies: " + ", ".join(missing) + ". Install requirements.txt in the active Python environment.")
    os.environ["A3P5_VERIFY_ROOT"] = str(root)
    os.environ["A3P5_VERIFY_MODELS"] = "1" if models else "0"
    os.environ["A3P5_VERIFY_REFIT"] = "1" if args.refit else "0"
    os.environ["A3P5_VERIFY_ENGINEERING"] = "1" if args.regenerate_engineering else "0"
    for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(name, "1")
    if models:
        recorded = json.loads((root / "manuscript/analysis/ml_outputs/results.json").read_text(encoding="utf-8"))["environment"]
        mismatched = []
        for module_name, recorded_name in [("numpy", "numpy"), ("pandas", "pandas"),
                                           ("scipy", "scipy"), ("sklearn", "scikit_learn"),
                                           ("joblib", "joblib")]:
            try:
                module = importlib.import_module(module_name)
            except Exception as error:
                parser.error(f"Cannot import {module_name} before model replay: {error}. "
                             "Run python -m pip install -r requirements.txt in the active Python environment.")
            actual = getattr(module, "__version__", "unknown")
            expected = recorded[recorded_name]
            if actual != expected:
                mismatched.append(f"{module_name} {actual} (required {expected})")
        if mismatched:
            parser.error("Model replay requires the exact recorded dependency versions: "
                         + "; ".join(mismatched)
                         + ". Run python -m pip install -r requirements.txt in the active Python environment.")
    tests = root / "tests"
    sys.path.insert(0, str(tests))
    suite = unittest.defaultTestLoader.discover(str(tests), pattern="test_*.py")
    started = time.perf_counter()
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {"status": "PASS" if result.wasSuccessful() else "FAIL",
              "tests_run": result.testsRun, "tests_passed": result.testsRun-len(result.skipped)-len(result.failures)-len(result.errors),
              "tests_skipped": [{"test": t.id(), "reason": why} for t, why in result.skipped],
              "failures": [{"test": t.id(), "detail": why} for t, why in result.failures],
              "errors": [{"test": t.id(), "detail": why} for t, why in result.errors],
              "elapsed_seconds": round(time.perf_counter()-started, 3), "python": platform.python_version(),
              "modes": {"models": models, "refit": args.refit, "regenerate_engineering": args.regenerate_engineering},
              "scope": "Analytical scenario and historical external-data reproducibility; no physical rover experiments."}
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ["status", "tests_run", "tests_passed", "elapsed_seconds", "modes"]}, indent=2))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
