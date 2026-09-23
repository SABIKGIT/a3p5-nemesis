"""Opt-in scientific-dependency checks of trusted archived pipelines and code."""
from functools import lru_cache
import importlib.util
import os
import unittest
from common import (MANUSCRIPT, ML, FEATURES, TARGET, FAMILIES, NumericCase,
                    read_json, rows)

MODELS = os.environ.get("A3P5_VERIFY_MODELS") == "1"
REFIT = os.environ.get("A3P5_VERIFY_REFIT") == "1"


@lru_cache(maxsize=1)
def listing():
    spec = importlib.util.spec_from_file_location("a3p5_listing", MANUSCRIPT / "text/code_listing_revision.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@unittest.skipUnless(MODELS, "opt in with --models (scientific dependencies required)")
class ModelReplayTests(NumericCase):
    def test_recorded_software_versions(self):
        import numpy, pandas, scipy, sklearn, joblib
        recorded = read_json(ML / "results.json")["environment"]
        for name, module in [("numpy", numpy), ("pandas", pandas), ("scipy", scipy),
                             ("scikit_learn", sklearn), ("joblib", joblib)]:
            self.assertEqual(module.__version__, recorded[name],
                             f"Install the recorded dependencies before model replay: {name}")

    def test_model_predictions_preprocessing_and_validation_scores(self):
        import joblib
        import numpy as np
        import pandas as pd
        data = listing().load_eligible()
        a, b = int(.70*len(data)), int(.85*len(data))
        train, valid, test = data.iloc[:a], data.iloc[a:b], data.iloc[b:]
        stored = pd.read_csv(ML / "test_predictions.csv")
        metrics = pd.read_csv(ML / "metrics.csv").set_index("model")
        costs = pd.read_csv(ML / "desktop_costs.csv").set_index("model")
        for family in FAMILIES:
            artifact = ML / "models" / (family + ".joblib")
            pipeline = joblib.load(artifact)
            np.testing.assert_allclose(pipeline.predict(test[FEATURES]), stored[family + "_prediction"], rtol=0, atol=1e-9)
            np.testing.assert_allclose(pipeline["imputer"].statistics_, train[FEATURES].median(), rtol=0, atol=1e-10)
            if family == "Ridge":
                np.testing.assert_allclose(pipeline["scaler"].mean_, train[FEATURES].mean(), rtol=0, atol=1e-10)
                np.testing.assert_allclose(pipeline["scaler"].var_, train[FEATURES].var(ddof=0), rtol=1e-10)
            error = pipeline.predict(valid[FEATURES]) - valid[TARGET].to_numpy()
            self.assertClose(np.sqrt(np.mean(error**2)), metrics.loc[family, "validation_RMSE"], atol=1e-9)
            self.assertEqual(artifact.stat().st_size, costs.loc[family, "artifact_bytes_uncompressed_joblib"])

    def test_all_seeded_calendar_day_bootstrap_replicates(self):
        import numpy as np
        import pandas as pd
        data = pd.read_csv(ML / "test_predictions.csv", parse_dates=["timestamp"])
        dates = data.timestamp.dt.normalize().to_numpy()
        groups = [np.flatnonzero(dates == day) for day in pd.unique(dates)]
        rng = np.random.default_rng(20260915)
        truth = data[TARGET].to_numpy()
        prediction = np.array([data[f + "_prediction"].to_numpy() for f in FAMILIES])
        replay = np.empty((len(FAMILIES), 2000, 4))
        for repetition in range(2000):
            index = np.concatenate([groups[i] for i in rng.integers(len(groups), size=len(groups))])
            y = truth[index]
            residual = prediction[:, index] - y
            replay[:, repetition, :] = np.stack([
                np.mean(abs(residual), axis=1), np.sqrt(np.mean(residual**2, axis=1)),
                1 - np.sum(residual**2, axis=1)/np.sum((y-y.mean())**2),
                np.mean(residual, axis=1)], axis=1)
        for i, family in enumerate(FAMILIES):
            stored = pd.read_csv(ML / ("bootstrap_" + family + ".csv"))
            np.testing.assert_allclose(replay[i], stored[["MAE", "RMSE", "R2", "Bias"]], rtol=0, atol=1e-9)

    def test_test_targets_cannot_affect_fitting_or_selection(self):
        import numpy as np
        import pandas as pd
        from sklearn.dummy import DummyRegressor
        from sklearn.linear_model import Ridge
        code = listing()
        n = 100
        frame = pd.DataFrame({"timestamp": pd.date_range("2020-01-01", periods=n, freq="h"),
                              "x": np.arange(n, dtype=float), "target": np.arange(n, dtype=float)*2+1})
        frame.loc[4, "x"] = np.nan
        frame.loc[70:, "x"] += 1000  # Must not affect train-only imputer/scaler.
        candidates = [("DummyMean", DummyRegressor()), ("Ridge", Ridge(alpha=1))]
        first = code.temporal_benchmark(frame.sample(frac=1, random_state=4), ["x"], "target", candidates)
        changed = frame.copy()
        changed.loc[85:, "target"] += 1_000_000
        second = code.temporal_benchmark(changed, ["x"], "target", candidates)
        self.assertEqual(first[0], second[0])
        self.assertEqual(first[2], second[2])
        for family in first[3]:
            np.testing.assert_array_equal(first[3][family], second[3][family])
        pipeline = first[1]["Ridge"][1]
        expected_median = frame.iloc[:70]["x"].median()
        self.assertClose(pipeline["imputer"].statistics_[0], expected_median)
        self.assertClose(pipeline["scaler"].mean_[0], frame.iloc[:70]["x"].fillna(expected_median).mean())
        self.assertEqual(int(pipeline["scaler"].n_samples_seen_), 70)

    def test_exact_ties_retain_first_candidate(self):
        import numpy as np
        import pandas as pd
        from sklearn.dummy import DummyRegressor
        frame = pd.DataFrame({"timestamp": pd.date_range("2020-01-01", periods=100, freq="h"),
                              "x": np.arange(100), "target": np.ones(100)})
        candidates = [("Constant", DummyRegressor(strategy="constant", constant=0)),
                      ("Constant", DummyRegressor(strategy="constant", constant=2))]
        winner, selected, search, predictions, _ = listing().temporal_benchmark(frame, ["x"], "target", candidates)
        self.assertEqual(winner, "Constant")
        self.assertEqual(search, [("Constant", 1.0), ("Constant", 1.0)])
        self.assertEqual(selected["Constant"][1]["regressor"].constant, 0)
        np.testing.assert_array_equal(predictions["Constant"], np.zeros(15))


@unittest.skipUnless(REFIT, "opt in with --refit to retrain all 21 candidates")
class CandidateRefitTests(NumericCase):
    def test_full_candidate_search_reproduces_locked_archive(self):
        import numpy as np
        code = listing()
        winner, selected, search, prediction, y = code.temporal_benchmark(
            code.load_eligible(), FEATURES, TARGET, code.candidate_grid())
        saved = rows(ML / "validation_search.csv")
        self.assertEqual(len(search), 21)
        self.assertEqual(winner, "Ridge")
        self.assertEqual(selected["Ridge"][1]["regressor"].alpha, 10)
        for (family, score), row in zip(search, saved):
            self.assertEqual(family, row["family"])
            self.assertClose(score, row["validation_RMSE"], atol=1e-9)
        archived = rows(ML / "test_predictions.csv")
        for family in FAMILIES:
            np.testing.assert_allclose(prediction[family], [float(r[family + "_prediction"]) for r in archived], rtol=0, atol=1e-9)
