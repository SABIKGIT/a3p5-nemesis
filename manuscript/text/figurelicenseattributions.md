# Figure captions and licence attributions

These are the complete manuscript-ready captions. The four journal figures are unmodified publisher assets; resizing to fit a page is permitted under the stated licences. All source-study measurements remain explicitly identified as external evidence. The five benchmark figures are newly generated plots from the public UCI dataset and the recorded analysis outputs. Figure numbering may be assigned during manuscript layout. Access and licence verification date: 15 September 2026.

## jayaratne2018_fig2.png

**Placement marker:** `[[FIGURE: research/licensed_figures/jayaratne2018_fig2.png]]`

**Full caption:** Humidity-dependent optical particle response in an external laboratory study. PMS1003 and DustTrak PM2.5 readings are shown as relative humidity increased in a chamber. These measurements illustrate a possible humidity artefact; they are not PMS7003 calibration coefficients or A3P5 observations. Reproduced without modification from Figure 2 of Rohan Jayaratne, Xiaoting Liu, Phong Thai, Matthew Dunbabin and Lidia Morawska (2018), “The influence of humidity on the performance of a low-cost air particle mass sensor and the effect of atmospheric fog,” Atmospheric Measurement Techniques, 11, 4883–4890. © Authors 2018. Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0).

- Article and credit link: https://doi.org/10.5194/amt-11-4883-2018
- Licence: https://creativecommons.org/licenses/by/4.0/
- Publisher image: https://amt.copernicus.org/articles/11/4883/2018/amt-11-4883-2018-f02-web.png
- Local file: `research/licensed_figures/jayaratne2018_fig2.png`
- Changes: none to the figure; the manuscript caption was newly written.

## patel2024_fig4.png

**Placement marker:** `[[FIGURE: research/licensed_figures/patel2024_fig4.png]]`

**Full caption:** External comparison of uncorrected and calibrated low-cost PM2.5 estimates against reference measurements at the Laney site, 2021–2022. The panels compare the correction approaches investigated by the source study and illustrate why environmental calibration must be evaluated under its intended conditions. These are published PMS5003-system observations, not A3P5 results. Reproduced without modification from Figure 4 of Milan Y. Patel, Pietro F. Vannucci, Jinsol Kim, William M. Berelson and Ronald C. Cohen (2024), “Towards a hygroscopic growth calibration for low-cost PM2.5 sensors,” Atmospheric Measurement Techniques, 17, 1051–1060. © Authors 2024. Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0).

- Article and credit link: https://doi.org/10.5194/amt-17-1051-2024
- Licence: https://creativecommons.org/licenses/by/4.0/
- Publisher image: https://amt.copernicus.org/articles/17/1051/2024/amt-17-1051-2024-f04-web.png
- Available publisher vector: https://amt.copernicus.org/articles/17/1051/2024/amt-17-1051-2024-f04-high-res.pdf
- Local file: `research/licensed_figures/patel2024_fig4.png`
- Changes: none to the figure; the manuscript caption was newly written.

## zheng2019_fig4.png

**Placement marker:** `[[FIGURE: research/licensed_figures/zheng2019_fig4.png]]`

**Full caption:** Published PM2.5 distributions across a Delhi monitoring network. The source figure compares 24 h reference-monitor concentrations and low-cost-node concentrations calibrated by an optimized Gaussian-process regression model, including site means and standard deviations. The network included PMS7003 sensors; its measurements and calibration results are external evidence and do not validate the A3P5 rover. Reproduced without modification from Figure 4 of Tongshu Zheng, Michael H. Bergin, Ronak Sutaria, Sachchida N. Tripathi, Robert Caldow and David E. Carlson (2019), “Gaussian process regression model for dynamically calibrating and surveilling a wireless low-cost particulate matter sensor network in Delhi,” Atmospheric Measurement Techniques, 12, 5161–5181. © Authors 2019. Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0).

- Article and credit link: https://doi.org/10.5194/amt-12-5161-2019
- Licence: https://creativecommons.org/licenses/by/4.0/
- Publisher image: https://amt.copernicus.org/articles/12/5161/2019/amt-12-5161-2019-f04-web.png
- Local file: `research/licensed_figures/zheng2019_fig4.png`
- Changes: none to the figure; the manuscript caption was newly written.

## barkjohn2021_fig4.png

**Placement marker:** `[[FIGURE: research/licensed_figures/barkjohn2021_fig4.png]]`

**Full caption:** External calibration-model errors for PurpleAir PM2.5 estimates under withheld-date and withheld-state evaluation. Mean absolute error and mean bias error are summarized for raw and corrected data using leave-out-by-date (LOBD) and leave-one-state-out (LOSO) evaluations. The figure motivates independent temporal and spatial validation; it contains no A3P5 measurements or benchmark results from the present study. Reproduced without modification from Figure 4 of Karoline K. Barkjohn, Brett Gantt and Andrea L. Clements (2021), “Development and application of a United States-wide correction for PM2.5 data collected with the PurpleAir sensor,” Atmospheric Measurement Techniques, 14, 4617–4637. © Authors 2021. Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0).

- Article and credit link: https://doi.org/10.5194/amt-14-4617-2021
- Licence: https://creativecommons.org/licenses/by/4.0/
- Publisher image: https://amt.copernicus.org/articles/14/4617/2021/amt-14-4617-2021-f04-web.png
- Local file: `research/licensed_figures/barkjohn2021_fig4.png`
- Changes: none to the figure; the manuscript caption was newly written.

## 01_dataset_audit.png

**Placement marker:** `[[FIGURE: analysis/ml_outputs/figures/01_dataset_audit.png]]`

**Full caption:** Chronology, availability and distribution shifts in the external UCI Air Quality dataset. (a) Daily reference-CO means coloured by the chronological training, validation and test partitions; at least 12 observed hours are required per displayed daily mean. (b) Separately normalized CO distributions. (c) Timestamped and eligible observation counts by month. (d) Separately normalized relative-humidity distributions. The −200 sentinel is treated as missing, unavailable targets and complete predictor outages are excluded, and missing periods remain unfilled. This original figure was generated from the recorded analysis of Saverio Vito (2008), Air Quality, UCI Machine Learning Repository, https://doi.org/10.24432/C59K5F, licensed under CC BY 4.0, https://creativecommons.org/licenses/by/4.0/. The panels are newly computed summaries, not reproductions of a source-publication figure or measurements from A3P5.

**Files:** `analysis/ml_outputs/figures/01_dataset_audit.png` and `.svg`.

## 02_test_metrics.png

**Placement marker:** `[[FIGURE: analysis/ml_outputs/figures/02_test_metrics.png]]`

**Full caption:** Frozen-model performance on 1,102 chronological held-out observations from the external UCI Air Quality dataset: (a) mean absolute error, (b) root mean square error and (c) coefficient of determination. Error bars are 2.5th–97.5th percentiles from 2,000 paired resamples of complete observed calendar-day blocks; the same sampled indices are used for every model. These conditional score intervals preserve within-day dependence but exclude cross-day dependence and model-fitting uncertainty. An asterisk marks Ridge, selected using validation RMSE before test evaluation. All model families remain reported irrespective of test ranking. Original analysis figure using Saverio Vito (2008), Air Quality, UCI Machine Learning Repository, https://doi.org/10.24432/C59K5F, CC BY 4.0, https://creativecommons.org/licenses/by/4.0/. These are external-data benchmark results, not A3P5 field results.

**Files:** `analysis/ml_outputs/figures/02_test_metrics.png` and `.svg`.

## 03_selected_model_predictions.png

**Placement marker:** `[[FIGURE: analysis/ml_outputs/figures/03_selected_model_predictions.png]]`

**Full caption:** Predictions of the validation-selected Ridge model over the complete chronological test block. (a) Daily reference and predicted CO means; days with fewer than 12 observed hours are omitted from the trace. (b) Hourly predicted-versus-reference agreement shown as counts within hexagonal bins, with the identity line. (c) Hourly residual distribution, defining residual as prediction minus reference; the mean bias is −0.157 mg m⁻³. All aggregate performance scores are computed from hourly observations rather than the displayed daily means. Original analysis figure using Saverio Vito (2008), Air Quality, UCI Machine Learning Repository, https://doi.org/10.24432/C59K5F, CC BY 4.0, https://creativecommons.org/licenses/by/4.0/. The data are external fixed-station measurements; no points were simulated and no rover performance is implied.

**Files:** `analysis/ml_outputs/figures/03_selected_model_predictions.png` and `.svg`.

## 04_residual_humidity.png

**Placement marker:** `[[FIGURE: analysis/ml_outputs/figures/04_residual_humidity.png]]`

**Full caption:** Held-out CO residuals as a function of recorded relative humidity for the mean baseline, Ridge, random forest and histogram gradient boosting. Light points are individual hourly residuals. Dark markers show residual means within fixed 10-percentage-point RH bins containing at least 20 observations; vertical segments show their interquartile ranges and are not confidence intervals. Marker positions use the median RH within each eligible bin. Shared vertical limits support comparison among the frozen models. Original analysis figure using Saverio Vito (2008), Air Quality, UCI Machine Learning Repository, https://doi.org/10.24432/C59K5F, CC BY 4.0, https://creativecommons.org/licenses/by/4.0/. These descriptive associations neither establish humidity causality nor validate A3P5 sensors.

**Files:** `analysis/ml_outputs/figures/04_residual_humidity.png` and `.svg`.

## 05_desktop_cost_and_sensitivity.png

**Placement marker:** `[[FIGURE: analysis/ml_outputs/figures/05_desktop_cost_and_sensitivity.png]]`

**Full caption:** Computational footprint and validation-only predictor sensitivity for the external-data calibration benchmark. (a) Uncompressed serialized pipeline sizes in MiB on a logarithmic scale. (b) Median single-row prediction times with interquartile ranges across 21 warmed desktop repetitions, including preprocessing. (c) Increase in validation RMSE following permutation of each Ridge predictor; bars show means and error bars show standard deviations over ten repetitions. Correlated predictors can share importance, and permutation sensitivity is not a causal or chemical-selectivity estimate. Serialized size does not measure embedded RAM or flash; desktop latency does not establish onboard feasibility. Original analysis figure using Saverio Vito (2008), Air Quality, UCI Machine Learning Repository, https://doi.org/10.24432/C59K5F, CC BY 4.0, https://creativecommons.org/licenses/by/4.0/. No rover measurements are included.

**Files:** `analysis/ml_outputs/figures/05_desktop_cost_and_sensitivity.png` and `.svg`.
