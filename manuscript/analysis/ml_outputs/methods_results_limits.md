# Reproducible external-data CO calibration benchmark

## Methods

The archived UCI Air Quality dataset (DOI:10.24432/C59K5F) was reanalysed, with CO(GT) in mg/m³ as the target. Predictors were only the five PT08 sensor-response channels and T, RH and AH. Other analyzer-derived gases were excluded. Date/time served only chronological partitioning and plotting. The -200 sentinel was converted to missing; target values were never imputed and concentration outliers were not removed or clipped. Rows with all eight predictors missing were excluded as unavailable observations. The archive contains 9,471 parsed rows, of which 114 lack timestamps. Among 9,357 timestamped rows, 1,683 lacked reference CO and another 330 had no predictors, leaving 7,344 observations. There were 0 missing predictor cells in the final eligible data, so the prespecified median imputation was inert. Actual timestamps span 2004-03-10 18:00:00 to 2005-04-04 14:00:00; this differs from the repository summary and is reported from the CSV rather than silently corrected.

Chronological partitions contained 5,140 training, 1,102 validation and 1,102 test observations. Their exact dates and all source row IDs are retained. Every preprocessing step and fitted model used the first 70% only; no train-plus-validation refit was performed. Hyperparameters and family choice used validation RMSE only. The final 15% was scored after configuration freeze. All four families remain reported regardless of test ranking. The search spaces and seed 20260915 are saved in benchmark_protocol.json. Random forest used 200 trees and one worker; histogram boosting used 250 iterations with internal early stopping disabled. No time, gas-reference, or target-lag predictors were used.

Frozen predictions were assessed with MAE, RMSE, R² and mean bias. Uncertainty intervals are percentile 95% intervals from 2,000 paired resamples of 48 observed calendar-day clusters. All available hours in each sampled day were kept together; no missing hours were filled. Test days contain 10–24 eligible observations. These are conditional score intervals, not prediction intervals or full model-training uncertainty. Dependence across multiple days is not represented. No statistical significance claim is inferred from visual interval overlap.

## Results

The validation-selected family was **Ridge**. Test RMSE was **0.5020 mg/m³** (95% daily-cluster interval 0.4353–0.5688); MAE was **0.3574 mg/m³** and R² **0.8480**. Mean residual (prediction minus reference) was -0.1571 mg/m³. These results were actually computed from the public dataset and are not A3P5 field measurements.

| Model | Validation RMSE | Test MAE (95% interval) | Test RMSE (95% interval) | Test R² (95% interval) |
|---|---:|---:|---:|---:|
| Mean baseline | 1.5136 | 1.0463 (0.9818–1.1153) | 1.3059 (1.2159–1.3978) | -0.0283 (-0.0983–-0.0015) |
| Ridge [validation choice] | 0.6853 | 0.3574 (0.3135–0.4062) | 0.5020 (0.4353–0.5688) | 0.8480 (0.7971–0.8868) |
| Random forest | 0.6900 | 0.3194 (0.2688–0.3733) | 0.4871 (0.4117–0.5601) | 0.8569 (0.8041–0.8978) |
| Histogram boosting | 0.8202 | 0.3910 (0.3325–0.4547) | 0.5651 (0.4871–0.6412) | 0.8075 (0.7489–0.8571) |

All errors are in mg/m³; R² is unitless. The paired RMSE improvement versus the mean baseline was 0.8039 mg/m³ (95% interval 0.7014–0.9030). Configuration files show the validation decision, even if another model later has a better test score.

## Figures

1. `01_dataset_audit`: observed chronology, target/environment distribution shifts and monthly availability. Daily trace values require at least 12 observed hours; missing days remain gaps. Histogram density is normalized separately per partition.
2. `02_test_metrics`: all frozen families with 95% paired calendar-day bootstrap intervals; asterisk marks the validation-selected family.
3. `03_selected_model_predictions`: full held-out daily trace, hourly agreement and residual histogram for the validation-selected family; the scatter uses observed counts rather than fabricated points.
4. `04_residual_humidity`: hourly residuals, means and interquartile ranges within fixed 10%-RH bins containing at least 20 observations. These bars are descriptive spread, not confidence intervals.
5. `05_desktop_cost_and_sensitivity`: uncompressed serialized-pipeline sizes, 21 warmed single-row desktop timings, and validation-only permutation sensitivity (10 repeats, mean ± standard deviation). Permutation effects are not causal and can be shared across correlated predictors.

All figures are original analysis graphics from UCI data, with both 300-dpi PNG and editable vector SVG files.

## Desktop cost interpretation

Timing used one worker/thread setting and is measured on the current desktop with full preprocessing included. The selected-candidate fit time, batch-prediction median and quartiles, single-row median and quartiles, serialized artifact size and software environment are in desktop_costs.csv/results.json. Serialized bytes do not measure inference RAM, embedded flash requirements or energy. Neither desktop timings nor this dataset establish onboard Mega/ESP32 feasibility.

## Limits and transfer to Nemesis

This is a historical, single-site, fixed-station benchmark with different sensor materials and electronics. It does not validate MQ7/MQ4/MQ135 calibration, selective analyte detection, mobile plume localization, model transfer to Bangladesh, sensor aging robustness, mission success, or onboard execution. The temporal holdout tests this archive's particular seasonal/drift shift; it is not independent site validation. Excluding missing targets and all-sensor outages may induce selection bias. Bootstrap intervals omit cross-day dependence, model-selection uncertainty, calibration-reference error and missing-data uncertainty. R² can vary with the target's held-out variance. No performance number may be assigned to A3P5 without new rover-specific collocation and external validation.

## Reproduce

Run `ml_benchmark.py` from the analysis folder using Python with the versions recorded in results.json; it reads ../research/air_quality.zip and discovers ../python_packages. Exact raw archive SHA256: `d4a64013fb385288a8a48d9d193ca7079b2e1bbddf6f8d458feb8c08ab2b8a2a`. The script stores all selected fitted pipelines, raw test predictions, split assignments, candidate validation scores, complete bootstrap score distributions and the cleaning audit. Saved-artifact predictions were reloaded and verified against the frozen predictions to absolute tolerance 1e-12. Numerical scores are reproducible with the recorded versions/seed; desktop timing measurements naturally vary.

## Sources

- Vito, S. (2008), Air Quality dataset. UCI. https://doi.org/10.24432/C59K5F (accessed 15 September 2026). UCI currently displays CC BY 4.0 alongside legacy research-only wording; this analysis is research use.
- De Vito, S.; Massera, E.; Piga, M.; Martinotto, L.; Di Francia, G. (2008). On field calibration of an electronic nose for benzene estimation in an urban pollution monitoring scenario. Sensors and Actuators B: Chemical 129(2), 750–757. https://doi.org/10.1016/j.snb.2007.09.060. The current CO task is a new reanalysis, not reproduction of the original benzene result.
- scikit-learn SimpleImputer documentation: https://scikit-learn.org/stable/modules/generated/sklearn.impute.SimpleImputer.html
- scikit-learn RandomForestRegressor documentation: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html
