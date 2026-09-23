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
