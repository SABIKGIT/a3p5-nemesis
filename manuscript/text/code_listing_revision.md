# Code listing insertion: Section 10.2

**Exact placement:** At the end of Section 10.2, after the paragraph ending “it does not establish the best possible algorithm or exhaust every nonlinear calibration strategy”, and before Section 10.3. Retain the listing under Section 10.2 with its introduction and caption.

## Manuscript prose before the listing

Listing 1 exposes the evaluation core used for the external-data benchmark. Its inputs are the eligible observations defined in Section 10.1, the eight permitted predictors and the ordered sequence of 21 prespecified candidate estimators. Each candidate is cloned before fitting. The pipeline estimates the imputer statistics and, for Ridge, the scaling statistics from the training partition alone; validation observations are transformed by those stored operations. The strict less-than comparison preserves the first candidate when validation scores tie. All family choices and the overall winner are frozen before any test predictions are produced. Returning predictions for every selected family preserves the complete comparison without using the test ranking to revise the winner.

!CODE[analysis/compact_ml_evaluation.py|Chronological model-selection and frozen-test evaluation core. The runnable companion supplies the NumPy/scikit-learn imports, original-data cleaning and fixed candidate grid. No training-plus-validation refit is performed.]

## Manuscript prose after the listing

The executable companion reparses the archived CSV, applies the documented eligibility rule and constructs the exact candidate sequence. Re-execution reproduced all 21 saved validation RMSE values and every family’s four test metrics to an absolute tolerance of 10⁻¹². The selected family remained Ridge. Calendar-day resampling is applied afterward to these frozen hourly predictions, as specified in Section 10.3; it does not refit the pipelines or modify the selection. This implementation provides an inspectable reference for the reported protocol, while deployment on the rover still requires new reference measurements and validation on the intended hardware.

## Reproduction and audit notes (supplement, not body)

- Displayed source: `analysis/compact_ml_evaluation.py`, 24 lines, maximum line width 73 characters.
- Runnable companion: `text/code_listing_revision.py`; this contains imports, exact original input hash, cleaning, all 21 candidate constructors, and comparisons against saved results. Run using the recorded dependencies.
- Fresh independent graph-data audit: `analysis/recheck_numerics_and_graph_data.py`; output `analysis/code_graph_recheck.json`. All 188 check groups / 68,752 scalar comparisons passed, covering all 9 engineering CSV tables; the existing 65-check ledger; frozen model predictions and train-only fitted transformations; all 2,000 paired bootstrap replicates for all four model families; confidence-interval endpoints; daily traces, RH-bin summaries, model bytes and validation-only permutation sensitivity.
- No original analysis outputs, models, graphs or manuscript sources were overwritten. Historical timing measurements were not replaced by fresh timings.
- No substantive numerical/ML-result correction was found. Existing warnings about external-data transfer and conditional intervals remain necessary.
