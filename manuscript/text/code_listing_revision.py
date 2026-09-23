"""Executable companion to Listing 1; reproduces the locked existing ML protocol.
Run from any directory with the recorded dependencies; no downloads or writes to
benchmark outputs. Candidate order and settings match analysis/ml_benchmark.py.
"""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(key, '1')
import sys, json, io, zipfile, hashlib
from pathlib import Path
from itertools import product
BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / 'python_packages'))
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
SEED = 20260915
FEATURES = ['PT08.S1(CO)', 'PT08.S2(NMHC)', 'PT08.S3(NOx)',
            'PT08.S4(NO2)', 'PT08.S5(O3)', 'T', 'RH', 'AH']
TARGET = 'CO(GT)'

# BEGIN MANUSCRIPT LISTING
def temporal_benchmark(frame, features, target, candidates):
    data = frame.sort_values("timestamp", kind="stable")
    n = len(data)
    a, b = int(0.70 * n), int(0.85 * n)
    train, valid, test = data.iloc[:a], data.iloc[a:b], data.iloc[b:]
    Xtr, ytr = train[features], train[target].to_numpy()
    Xva, yva = valid[features], valid[target].to_numpy()
    selected, search = {}, []
    for family, prototype in candidates:
        steps = [("imputer", SimpleImputer(strategy="median"))]
        if family == "Ridge":
            steps.append(("scaler", StandardScaler()))
        model = Pipeline(steps + [("regressor", clone(prototype))])
        model.fit(Xtr, ytr)
        score = np.sqrt(mean_squared_error(yva, model.predict(Xva)))
        search.append((family, float(score)))
        previous = selected.get(family, (np.inf, None))[0]
        if score < previous:  # Retain the first candidate on exact ties.
            selected[family] = (float(score), model)
    winner = min(selected, key=lambda name: selected[name][0])
    Xte, yte = test[features], test[target].to_numpy()
    predictions = {name: fit.predict(Xte)
                   for name, (_, fit) in selected.items()}
    return winner, selected, search, predictions, yte
# END MANUSCRIPT LISTING

def candidate_grid():
    candidates = [('DummyMean', DummyRegressor(strategy='mean'))]
    candidates += [('Ridge', Ridge(alpha=a))
                   for a in [0.01, 0.1, 1., 10., 100., 1000.]]
    candidates += [('RandomForest', RandomForestRegressor(
        n_estimators=200, max_features=1., n_jobs=1, random_state=SEED,
        max_depth=d, min_samples_leaf=leaf))
        for d, leaf in product([10, None], [1, 5, 15])]
    candidates += [('HistGradientBoosting', HistGradientBoostingRegressor(
        max_iter=250, min_samples_leaf=20, early_stopping=False,
        random_state=SEED, learning_rate=lr, max_leaf_nodes=leaves,
        l2_regularization=penalty))
        for lr, leaves, penalty in product([0.05, 0.1], [15, 31], [0., 1.])]
    assert len(candidates) == 21
    return candidates

def load_eligible():
    archive = BASE / 'research' / 'air_quality.zip'
    expected = 'd4a64013fb385288a8a48d9d193ca7079b2e1bbddf6f8d458feb8c08ab2b8a2a'
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == expected
    with zipfile.ZipFile(archive) as z:
        raw = pd.read_csv(io.BytesIO(z.read('AirQualityUCI.csv')),
                          sep=';', decimal=',')
    raw['timestamp'] = pd.to_datetime(
        raw['Date'].fillna('') + ' ' + raw['Time'].fillna(''),
        format='%d/%m/%Y %H.%M.%S', errors='coerce')
    d = raw.loc[raw.timestamp.notna(), ['timestamp', TARGET] + FEATURES].copy()
    assert not d.timestamp.duplicated().any()
    d[[TARGET] + FEATURES] = d[[TARGET] + FEATURES].replace(-200, np.nan)
    keep = d[TARGET].notna() & ~d[FEATURES].isna().all(axis=1)
    return d.loc[keep].sort_values('timestamp', kind='stable').reset_index(drop=True)

if __name__ == '__main__':
    frame = load_eligible()
    winner, selected, search, predictions, y_test = temporal_benchmark(
        frame, FEATURES, TARGET, candidate_grid())
    scores = {family: {'MAE': float(mean_absolute_error(y_test, pred)),
                      'RMSE': float(np.sqrt(mean_squared_error(y_test, pred))),
                      'R2': float(r2_score(y_test, pred)),
                      'Bias': float(np.mean(pred - y_test))}
              for family, pred in predictions.items()}
    recorded = pd.read_csv(BASE / 'analysis/ml_outputs/metrics.csv').set_index('model')
    saved_search = pd.read_csv(BASE / 'analysis/ml_outputs/validation_search.csv')
    assert len(search) == len(saved_search) == 21
    for (family, score), row in zip(search, saved_search.itertuples()):
        assert family == row.family
        np.testing.assert_allclose(score, row.validation_RMSE, rtol=0, atol=1e-12)
    for family, metric in scores.items():
        for key, value in metric.items():
            np.testing.assert_allclose(value, recorded.loc[family, 'test_' + key],
                                       rtol=0, atol=1e-12)
    assert winner == 'Ridge'
    print(json.dumps({'status': 'PASS', 'eligible_rows': len(frame),
                      'candidates': len(search), 'selected_family': winner,
                      'test_metrics': scores,
                      'agreement_tolerance': 1e-12}, indent=2))
