"""Verify archived data, selection and scores without loading executable models."""
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import json
import math
from common import (FEATURES, TARGET, FAMILIES, ML, NumericCase, archive_data,
                    number, percentile, read_json, rows, scores)


class ExternalDataArchiveTests(NumericCase):
    def test_archive_hash_cleaning_and_dates(self):
        raw, valid, eligible, csv_hash = archive_data()
        audit = read_json(ML / "data_audit.json")
        self.assertEqual((len(raw), len(valid), len(eligible)), (9471, 9357, 7344))
        self.assertEqual(csv_hash, audit["csv_sha256"])
        self.assertEqual(len({r["timestamp"] for r in valid}), len(valid))
        self.assertEqual(str(valid[0]["timestamp"]), "2004-03-10 18:00:00")
        self.assertEqual(str(valid[-1]["timestamp"]), "2005-04-04 14:00:00")
        self.assertEqual(sum(math.isnan(r[TARGET]) for r in valid), 1683)
        self.assertEqual(sum(math.isfinite(r[TARGET]) and all(math.isnan(r[k]) for k in FEATURES) for r in valid), 330)
        self.assertEqual(sum(math.isnan(r[k]) for r in eligible for k in FEATURES), 0)
        expected = {"raw_csv_rows": len(raw), "valid_timestamp_rows": len(valid),
                    "invalid_or_blank_timestamp_rows": len(raw)-len(valid), "eligible_rows": len(eligible)}
        for key, value in expected.items():
            self.assertEqual(audit[key], value, key)
        cleaned = rows(ML / "cleaned_observations_with_flags.csv")
        self.assertEqual(len(cleaned), len(valid))
        eligible_lines = {r["source_row"] for r in eligible}
        for got, expected_row in zip(cleaned, valid):
            self.assertEqual(int(got["source_row"]), expected_row["source_row"])
            self.assertEqual(datetime.fromisoformat(got["timestamp"]), expected_row["timestamp"])
            self.assertEqual(got["eligible"], str(expected_row["source_row"] in eligible_lines))
            for key in [TARGET] + FEATURES:
                self.assertClose(number(got[key]), expected_row[key], context=key)

    def test_chronological_split_has_no_overlap_or_reference_gas_predictors(self):
        eligible = archive_data()[2]
        a, b = int(.70 * len(eligible)), int(.85 * len(eligible))
        self.assertEqual((a, b-a, len(eligible)-b), (5140, 1102, 1102))
        saved = rows(ML / "split_assignments.csv")
        self.assertEqual(len(saved), len(eligible))
        for i, (got, actual) in enumerate(zip(saved, eligible)):
            self.assertEqual(int(got["source_row"]), actual["source_row"])
            self.assertEqual(datetime.fromisoformat(got["timestamp"]), actual["timestamp"])
            self.assertEqual(got["split"], "train" if i < a else "validation" if i < b else "test")
        self.assertLess(eligible[a-1]["timestamp"], eligible[a]["timestamp"])
        self.assertLess(eligible[b-1]["timestamp"], eligible[b]["timestamp"])
        protocol = read_json(ML / "benchmark_protocol.json")
        self.assertEqual(protocol["features"], FEATURES)
        self.assertEqual(protocol["target"], TARGET)
        self.assertTrue(set(FEATURES).isdisjoint({TARGET, "NMHC(GT)", "C6H6(GT)", "NOx(GT)", "NO2(GT)"}))
        self.assertEqual(protocol["random_seed"], 20260915)
        self.assertFalse(protocol["HGB_fixed"]["early_stopping"])

    def test_frozen_selection_matches_validation_only(self):
        search = rows(ML / "validation_search.csv")
        self.assertEqual(len(search), 21)
        self.assertEqual(Counter(r["family"] for r in search),
                         {"DummyMean": 1, "Ridge": 6, "RandomForest": 6, "HistGradientBoosting": 8})
        frozen = read_json(ML / "frozen_selection.json")
        best = {}
        for row in search:
            family = row["family"]
            if family not in best or float(row["validation_RMSE"]) < float(best[family]["validation_RMSE"]):
                best[family] = row  # Strict comparison preserves first-on-tie policy.
        winner = min(FAMILIES, key=lambda f: float(best[f]["validation_RMSE"]))
        self.assertEqual(winner, "Ridge")
        self.assertEqual(frozen["selected_family"], winner)
        self.assertEqual(frozen["models"]["Ridge"]["parameters"], {"alpha": 10.0})
        for family, row in best.items():
            selected = frozen["models"][family]
            self.assertEqual(selected["candidate"], int(row["candidate"]))
            self.assertEqual(selected["parameters"], json.loads(row["parameters"]))
            self.assertClose(selected["validation"]["RMSE"], row["validation_RMSE"])
        metrics = rows(ML / "metrics.csv")
        self.assertEqual([r["model"] for r in metrics if r["selected_by_validation"] == "True"], [winner])
        # The archived test ranking differs; it must not silently replace the validation winner.
        self.assertEqual(min(metrics, key=lambda r: float(r["test_RMSE"]))["model"], "RandomForest")

    def test_frozen_test_targets_and_all_point_scores(self):
        eligible = archive_data()[2]
        test = eligible[int(.85 * len(eligible)):]
        predictions = rows(ML / "test_predictions.csv")
        metrics = {r["model"]: r for r in rows(ML / "metrics.csv")}
        self.assertEqual(len(predictions), 1102)
        for got, actual in zip(predictions, test):
            self.assertEqual(int(got["source_row"]), actual["source_row"])
            self.assertEqual(datetime.fromisoformat(got["timestamp"]), actual["timestamp"])
            self.assertClose(got[TARGET], actual[TARGET])
        truth = [r[TARGET] for r in test]
        for family in FAMILIES:
            pred = [float(r[family + "_prediction"]) for r in predictions]
            self.assertTrue(all(math.isfinite(p) for p in pred))
            for r, y, p in zip(predictions, truth, pred):
                self.assertClose(r[family + "_residual"], p-y)
            for key, expected in scores(truth, pred).items():
                self.assertClose(metrics[family]["test_" + key], expected, context=family + key)
            self.assertEqual(int(metrics[family]["test_n"]), 1102)
        train = eligible[:int(.70 * len(eligible))]
        train_mean = math.fsum(r[TARGET] for r in train) / len(train)
        for row in predictions:
            self.assertClose(row["DummyMean_prediction"], train_mean)

    def test_block_structure_and_archived_percentile_intervals(self):
        predictions = rows(ML / "test_predictions.csv")
        days = Counter(datetime.fromisoformat(r["timestamp"]).date() for r in predictions)
        self.assertEqual((len(days), min(days.values()), max(days.values())), (48, 10, 24))
        results = read_json(ML / "results.json")
        self.assertEqual(results["bootstrap_repetitions"], 2000)
        metrics = {r["model"]: r for r in rows(ML / "metrics.csv")}
        boot = {}
        for family in FAMILIES:
            boot[family] = rows(ML / ("bootstrap_" + family + ".csv"))
            self.assertEqual(len(boot[family]), 2000)
            for key in ["MAE", "RMSE", "R2", "Bias"]:
                values = [float(r[key]) for r in boot[family]]
                self.assertTrue(all(math.isfinite(v) for v in values))
                self.assertClose(metrics[family]["test_" + key + "_lo"], percentile(values, .025))
                self.assertClose(metrics[family]["test_" + key + "_hi"], percentile(values, .975))
        paired = [float(a["RMSE"])-float(b["RMSE"]) for a, b in zip(boot["DummyMean"], boot["Ridge"])]
        for q, expected in zip([.025, .975], results["paired_test_RMSE_gain_vs_mean_baseline"]["percentile_95"]):
            self.assertClose(percentile(paired, q), expected)

    def test_daily_plot_keeps_sparse_and_missing_days_missing(self):
        predictions = rows(ML / "test_predictions.csv")
        by_day = defaultdict(list)
        for row in predictions:
            by_day[datetime.fromisoformat(row["timestamp"]).date()].append(row)
        trace = rows(ML / "test_daily_trace.csv")
        expected_days = (max(by_day)-min(by_day)).days + 1
        self.assertEqual(len(trace), expected_days)
        for i, row in enumerate(trace):
            day = min(by_day) + timedelta(days=i)
            self.assertEqual(row["timestamp"], str(day))
            observed = by_day[day]
            self.assertEqual(int(row["observed_hours"]), len(observed))
            for key in [TARGET, "Ridge_prediction"]:
                expected = math.fsum(float(r[key]) for r in observed)/len(observed) if len(observed) >= 12 else math.nan
                self.assertClose(number(row[key]), expected)

    def test_coverage_and_humidity_graph_summaries(self):
        _, valid, eligible, _ = archive_data()
        total = Counter(r["timestamp"].strftime("%Y-%m-01") for r in valid)
        available = Counter(r["timestamp"].strftime("%Y-%m-01") for r in eligible)
        coverage = rows(ML / "monthly_data_coverage.csv")
        self.assertEqual(len(coverage), len(total))
        for row in coverage:
            self.assertEqual(int(row["total"]), total[row["timestamp"]])
            self.assertEqual(int(row["available"]), available[row["timestamp"]])
        predictions = rows(ML / "test_predictions.csv")
        for row in rows(ML / "test_residual_RH_bins.csv"):
            lo, hi = float(row["RH_bin_low"]), float(row["RH_bin_high"])
            error = [float(r[row["model"] + "_prediction"])-float(r[TARGET]) for r in predictions if lo <= float(r["RH"]) < hi]
            self.assertEqual(len(error), int(row["n"]))
            self.assertGreaterEqual(len(error), 20)
            self.assertClose(row["residual_mean"], math.fsum(error)/len(error))
            self.assertClose(row["residual_q25"], percentile(error, .25))
            self.assertClose(row["residual_q75"], percentile(error, .75))
