# Numerical verification

Use Python 3.12 from the repository root. The default checks use only Python's standard library:

```sh
python scripts/verify.py
```

This runs 16 read-only checks and explicitly skips seven optional scientific checks. It independently parses the pinned UCI archive, checks all nine engineering tables, verifies chronological partitions and validation-only selection records, recomputes all four families' held-out metrics, checks the saved bootstrap intervals, and reconstructs the plotted daily, monthly and humidity summaries. It does not load serialized models, download data, train a model or overwrite archived results.

## Replay and regenerate

Install the recorded scientific dependencies in the active environment:

```sh
python -m pip install -r requirements.txt
python scripts/verify.py --models
python scripts/verify.py --refit --regenerate-engineering
```

- `--models` loads the supplied trusted joblib artifacts, verifies train-only preprocessing and predictions, and replays all 2,000 paired calendar-day bootstrap replicates. Synthetic checks alter test targets and validation/test feature distributions to detect leakage; an exact-tie check verifies deterministic candidate selection.
- `--refit` includes `--models` and retrains all 21 declared candidates. It compares candidate validation scores and frozen test predictions to the archived outputs. It does not use test scores to select a replacement winner.
- `--regenerate-engineering` executes a copy of the analysis in a temporary directory, compares every numerical table cell, and confirms all eight PNG/SVG figure pairs were generated. The archived tables and figures remain unchanged.

All options can be combined. No personal directories, bundled interpreter or Blender installation is required by these tests. The scientific modes require NumPy, pandas, SciPy, scikit-learn and joblib; engineering regeneration additionally requires Matplotlib. Exact recorded library versions are checked before interpreting serialized-model replay as reproducibility.

To save a report or run from elsewhere:

```sh
python scripts/verify.py --refit --regenerate-engineering --json verification.json
python /path/to/repository/scripts/verify.py --root /path/to/repository
```

The exit code is zero only when all enabled checks pass. The JSON report distinguishes passed tests, explicitly skipped modes, failures and errors. Standard-library discovery is also supported:

```sh
python -m unittest discover -s tests -v
```

## What passing means

Passing establishes numerical agreement with the declared analytical scenarios and the historical external-data protocol. It does not establish rover payload, slope, braking, endurance, pollutant selectivity, autonomy or field performance. The archived desktop timing values are preserved, not tested as universal performance thresholds. Reproducible selection code and consistent saved records do not independently prove historical preregistration.

Default numerical comparisons allow floating-point rounding at approximately 1e-10; pipeline predictions and candidate refits allow absolute differences up to 1e-9. Raw dataset identity is exact SHA-256, and chronological membership is exact. Figure-pixel identity is not asserted because rendering can vary with fonts and plotting-library versions; this suite checks the numerical inputs and exported figure presence instead.
