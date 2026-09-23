# Contributing to A3P5 NEMESIS

Corrections, clearer explanations and reproducibility reports are welcome. Start with the [paper](https://arxiv.org/abs/2609.18245), [reproduction guide](docs/reproduce.md) and [testing guide](docs/TESTING.md) to understand the study and its evidence.

## Report an issue

Use the [reproducibility report form](https://github.com/SABIKGIT/a3p5-nemesis/issues/new?template=reproducibility.yml) for failed checks, numerical discrepancies or unclear reproduction steps. Include the commit you used, operating system, Python and package versions, exact command, expected result and relevant output. For a paper correction, identify the equation, table or section and explain the proposed correction with a source or calculation.

For other suggestions, open a regular issue. Discuss substantial changes to the analysis protocol before implementing them so the intended comparison is clear.

## Prepare a change

1. Create a branch from the current default branch and keep the change focused.
2. Preserve the distinction between prototype photographs, analytical predictions, the historical external-data benchmark and proposed hardware tests. Passing numerical checks does not establish physical rover performance.
3. Retain data provenance and attribution. Keep the chronological train/validation/test split and validation-only selection intact when correcting the existing benchmark. Describe a changed protocol as a new experiment and preserve the original results for comparison.
4. Update the explanation alongside any changed equation, assumption or generated result. Inspect regenerated figures and rendered manuscript pages when those assets change.

Read [LICENSE_STATUS.md](LICENSE_STATUS.md), [DATA_SOURCES.md](DATA_SOURCES.md) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) before adding or reusing material. Original source code is covered by the [MIT License](LICENSE), copyright (c) 2026 Sabik Bin Sultan. The grant does not extend to the coauthored research or other non-code materials; source-specific rights and credits still apply. Preserve existing notices and do not change attribution, relicense excluded materials or redistribute external material without the relevant authorization.

## Check the change

Run commands from the repository root with Python 3.12. Before editing, check that your starting copy matches the distribution manifest:

```bash
python scripts/manifest.py --check
```

The default numerical checks need only the Python standard library:

```bash
python scripts/verify.py
```

Choose the additional checks that exercise your change after installing the recorded dependencies:

```bash
python -m pip install -r requirements.txt
python scripts/verify.py --models
python scripts/verify.py --refit --regenerate-engineering --json verification/local-full-results.json
```

| Mode | What it checks |
|---|---|
| Default | Archived data, engineering tables, partitions, selection records and numerical results |
| `--models` | Supplied trusted model replay, preprocessing, predictions, bootstrap results and leakage checks |
| `--refit` | All 21 declared candidates and agreement with archived validation scores and frozen test predictions; includes model replay |
| `--regenerate-engineering` | Engineering regeneration in a temporary directory and comparison with archived outputs |

These verification modes preserve the archived scientific outputs. Directly running the analysis builders replaces generated files; see the reproduction guide before doing that. Load serialized models only from a trusted repository copy and use the recorded package versions for replay.

After deliberately editing reviewed distribution files, inspect the diff, run the relevant checks, and update the integrity record:

```bash
python scripts/manifest.py --write
python scripts/manifest.py --check
```

Include the manifest update with the intentional changes. Do not refresh it to hide an unexplained mismatch. Save local reports with a `local-` filename under `verification/` so they stay outside the distribution manifest.

## Open a pull request

Explain the problem, the resulting change and the evidence supporting it. List the checks you ran, including any skipped optional modes or environment limitations. Link a related issue when one exists. For numerical changes, include the affected assumptions and before/after results; distinguish corrected archived calculations from new experiments or physical measurements.
