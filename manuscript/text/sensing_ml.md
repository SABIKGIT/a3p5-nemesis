# Environmental sensing and measurement assurance

## Measurement scope and traceability

The supplied A3P5 description identifies MQ135, MQ7, MQ4, PMS7003, GUVA and BMP180 devices, together with pH and turbidity sensing. These identifiers define the reported sensor inventory; they do not constitute a verified as-built bill of materials. Calibration, electrical interface revisions and analytical performance require separate identification. Accordingly, the environmental subsystem is specified as a collection of measurement chains, each retaining its raw response, conversion version, timestamp and quality flags. Concentration estimates require comparison with an independent reference. A numerical display alone does not establish analyte selectivity, traceability or suitability for regulatory monitoring. The following design provisions therefore define work required to convert the prototype inventory into defensible environmental observations.

## Gas sensing, heater scheduling and electrical integration

The three MQ channels should be interpreted jointly with operating conditions. MQ135 is a broadly responsive semiconductor sensor rather than a selective carbon-dioxide instrument; its response can arise from several gases and vapours. For a conventional divider, the sensing resistance is reconstructed from the measured load voltage:

$$
R_s=R_L\left(\frac{V_c}{V_L}-1\right).
$$

Here, R_s and R_L are sensing and load resistances in ohms, V_c is the divider supply in volts and V_L is the voltage across R_L. This expression requires the actual module topology and resistor value to be verified. The ratio R_s/R_0 is useful only when the reference condition defining R_0 is recorded. A manufacturer sensitivity curve supplies a starting model, not a substitute for unit-specific calibration with interfering gases (Winsen, 2021a).

Heater operation is part of the measurement, not merely a power requirement. The MQ-7B manual specifies a 60 s high-temperature phase at 5 V followed by a 90 s low-temperature phase at 1.5 V. Because the rover description says MQ7, the exact installed variant must be checked before applying that schedule. A compatible implementation would timestamp the phase, reject cleaning and transition readings, and log heater voltage alongside accepted samples. Initial conditioning and recovery after prolonged storage require separate procedures (Winsen, 2021b). For MQ4, the manufacturer's nominal methane range does not quantify accuracy or analyte selectivity (Winsen, 2021c). Experiments on another low-cost methane device demonstrate why temperature, humidity and cross-interference deserve explicit calibration terms, while providing no transferable MQ4 coefficients (Lin et al., 2023).

The proposed harness separates motor and heater returns from low-level measurement paths, with a defined connection at the power-distribution reference. Regulated sensor rails, protected inputs and local decoupling reduce the chance that acceleration or servo operation is interpreted as a chemical event. Every connector should be keyed, labelled and mechanically retained; flexible loops must accommodate steering and arm travel without loading terminals. Motor-state and supply-voltage logs should accompany commissioning data so that correlated electrical artefacts can be identified. Cable sleeves improve protection and appearance, but their contribution to measurement integrity depends on routing, termination and verified continuity.

## Optical particles, humidity and sensor identity

Optical particle readings depend on the sampled aerosol and its interaction with moisture. Jayaratne et al. (2018) observed substantial humidity and fog effects with a PMS1003; those measurements motivate humidity-aware quality control but are not PMS7003 calibration data. A collocated temperature–humidity instrument is therefore a proposed addition. The listed BMP180 measures pressure and temperature and cannot supply relative humidity. Its temperature reading may also reflect board heating rather than undisturbed ambient air (Bosch Sensortec, 2013). The sampling inlet should remain exposed to representative airflow while shielding direct rain and avoiding wheel-generated dust or enclosure exhaust.

[[FIGURE: research/licensed_figures/jayaratne2018_fig2.png]]

Caption provenance: external laboratory measurements; Jayaratne et al. (2018), original Figure 2, reproduced under CC BY 4.0. Full attribution is supplied separately.

A useful family of humidity corrections represents hygroscopic enhancement explicitly:

$$
\widehat{c}_{\mathrm{dry}}=c_{\mathrm{raw}}\frac{m}{1+\kappa/(100/H-1)},\qquad 0<H<100.
$$

Here, H is relative humidity in percent, c_raw and estimated dry concentration have matching mass-concentration units, and m and κ are fitted scale and growth parameters. Patel et al. (2024) investigated this structure with PMS5003 observations. It is presented as a candidate for testing, with numerical coefficients deliberately unspecified for A3P5. Behaviour near saturation and changes in aerosol composition require validation and quality flags rather than unrestricted extrapolation. Published comparisons between uncorrected, national and locally adjusted estimates illustrate the importance of evaluating the correction under the intended exposure conditions.

[[FIGURE: research/licensed_figures/patel2024_fig4.png]]

Caption provenance: external Laney-site observations from 2021–2022; Patel et al. (2024), original Figure 4, reproduced under CC BY 4.0.

## Temporal response and environmental mapping

Mobility introduces a mismatch between the location of acquisition and the air parcel influencing the sensor. A first-order approximation makes that limitation explicit:

$$
\tau\frac{dz(t)}{dt}+z(t)=c(t),\qquad d_{\mathrm{lag}}\approx v\tau.
$$

In this local approximation, z is a concentration-equivalent response, c is the input concentration, τ is the response time constant in seconds, v is rover speed in metres per second and d_lag is an approximate along-track displacement in metres. For a step input, the time to reach 90% of the final response is t₉₀ = τ ln(10), and the corresponding travel distance is d₉₀ = vτ ln(10). These threshold quantities differ from the characteristic lag length vτ: for τ = 15 s and v = 0.25 m/s, t₉₀ = 34.54 s and d₉₀ = 8.63 m. Actual semiconductor adsorption and recovery can be asymmetric, so τ requires experimental identification. Sampling faster cannot remove this physical lag. Initial mapping trials should combine stationary dwell measurements with travel intervals, record inlet position and pose uncertainty, and distinguish recovery transients from spatial gradients.

Zheng et al. (2019) demonstrated dynamic Gaussian-process calibration in a Delhi network that included PMS7003 devices. Their spatial distributions illustrate achievable analysis after reference collocation, not an accuracy specification for the rover. Information-driven gas mapping additionally depends on localization, environmental transport and an observation model (Gongora et al., 2023). Those inputs must be established before uncertainty-guided sampling is claimed. A mission visualization alone does not establish a valid dispersion field; transport simulation requires separate assumptions and boundary conditions, as exemplified by GADEN (Monroy et al., 2017).

[[FIGURE: research/licensed_figures/zheng2019_fig4.png]]

Caption provenance: external Delhi reference-monitor and calibrated low-cost-node data; Zheng et al. (2019), original Figure 4, reproduced under CC BY 4.0.

## Water probes, ultraviolet exposure and calibration uncertainty

The pH channel requires a verified electrode interface because glass electrodes have high source impedance. Buffer input bias, surface leakage and moisture can introduce offsets even when digital communication appears reliable. A short, shielded probe connection, clean high-impedance input region and mechanically supported connector are proposed. The ideal temperature-dependent electrode slope is expressed by

$$
E=E_7-S(T)(\mathrm{pH}-7),\qquad S(T)=\frac{\ln(10)RT}{F}.
$$

Here, E is the electrode potential and E_7 is its value at pH 7, both in volts, T is solution temperature in kelvin, R is the molar gas constant and F is the Faraday constant. The ideal magnitude is approximately 59.16 mV per pH unit at 25 °C; actual offset and slope require buffer calibration. The conditioning calculation assumes gain G = 3, a 5 V reference and 10-bit ADC with a 2.5 V midpoint; the proposed comparison uses a 3.3 V reference and 12-bit ADC with a 1.65 V midpoint. For an ideal N-bit ADC, one least-significant bit (LSB) represents V_ref/2ᴺ (Microchip Technology, n.d.), giving a pH increment of V_ref/[2ᴺ G S(T)]. At 25 °C, the respective increments are 0.0275122 and 0.00453951 pH/LSB. These quantization intervals describe ideal resolution; electrode, amplifier and reference errors determine measurement accuracy. A suitable reference circuit demonstrates the importance of a low-bias buffer and guarded input, but is not asserted to be installed on A3P5 (Analog Devices, 2013). Field procedures should document buffer temperature, stabilization, rinsing, electrode condition and an independent check solution (U.S. Geological Survey, 2021).

Turbidity measurements require local calibration against appropriate standards, control of bubbles and a documented optical path. Fouling and changes in particle properties can alter response between deployments; published low-cost instruments consequently assess calibration and maintenance together (Trevathan et al., 2020; Wang et al., 2024). The unidentified rover module cannot inherit their coefficients. Likewise, the GUVA identifier alone does not define the complete amplifier gain, spectral correction or angular response needed for a defensible ultraviolet index. Its board identity and calibration must be established before converting voltage into an exposure metric (DFRobot, n.d.-a).

For a calibrated measurand y=f(x), a first-order uncertainty budget can be written

$$
u_c^2(y)\approx J\Sigma_xJ^{\mathsf T}+u_{\mathrm{model}}^2.
$$

Here, J contains sensitivities of the measurement function, Σ_x is the covariance matrix of input uncertainties, and u_model represents additional calibration-model uncertainty when treated as independent. The budget should distinguish reference uncertainty, repeatability, environmental correction and drift; correlated terms must not be counted twice. This is an assessment framework rather than a numerical uncertainty claim (Joint Committee for Guides in Metrology, 2008). A3P5 presently requires the underlying collocation and stability measurements before calibrated environmental performance can be stated.

# External-data machine-learning calibration benchmark

## Dataset, task definition and eligibility

A reproducible external-data experiment was conducted to examine calibration choices before rover-specific training data become available. The UCI Air Quality archive contains fixed-station observations from a multisensor electronic nose and reference analysers (Vito, 2008). The associated publication concerns benzene calibration (De Vito et al., 2008); the present experiment defines a separate carbon-monoxide regression task. Its results support methodological development, not a claim that the rover's MQ devices have been calibrated or deployed successfully.

The target was CO(GT), in mg m⁻³. Exactly eight predictors were permitted: PT08.S1(CO), PT08.S2(NMHC), PT08.S3(NOx), PT08.S4(NO2), PT08.S5(O3), temperature T, relative humidity RH and absolute humidity AH. Channel labels identify supplied sensor responses, not perfectly selective analyte measurements. All other reference-gas columns were excluded. Timestamps served partitioning and visualization only; neither target lags nor time-derived predictors were introduced. Thus, prediction uses the contemporaneous sensor array and recorded environment without access to additional reference-analyser outputs.

The parsed file contained 9,471 rows. Removing 114 rows without valid timestamps left 9,357 unique timestamped observations. The sentinel −200 was converted to missing. Excluding 1,683 unavailable CO targets and another 330 observations with all predictors missing yielded 7,344 eligible observations. The retained predictors contained no missing cells, so the prespecified training-median imputer was inert. Targets were never imputed, and observations were neither interpolated nor concentration-filtered. Actual timestamps span 10 March 2004, 18:00, to 4 April 2005, 14:00; this auditable file range is retained despite differences from the repository summary. Dataset-local timestamps are used without inferring a timezone.

[[FIGURE: analysis/ml_outputs/figures/01_dataset_audit.png]]

Caption: Original analysis of the UCI Air Quality dataset: chronological coverage, target distributions, monthly eligibility and humidity distributions. Daily means require at least 12 observed hours; missing periods remain gaps. Source data: Vito (2008), CC BY 4.0. No A3P5 measurements are included.

## Chronological evaluation and model selection

Chronologically ordered eligible rows were partitioned at floor(0.70n) and floor(0.85n). Training comprised 5,140 observations from 10 March 2004, 18:00, through 19 December 2004, 17:00. Validation comprised 1,102 observations from 19 December 2004, 18:00, through 16 February 2005, 13:00. Testing comprised the subsequent 1,102 observations through 4 April 2005, 14:00. Separating later periods limits leakage from randomly mixing temporally dependent observations, although it cannot establish geographic transfer (Roberts et al., 2017; Kapoor and Narayanan, 2023).

Four model families were compared: a training-mean baseline, standardized ridge regression, random forest and histogram gradient boosting. Ridge solves

$$
(\widehat{\beta}_0,\widehat{\boldsymbol\beta})=\arg\min_{\beta_0,\boldsymbol\beta}\left[\sum_{i\in\mathcal T}(y_i-\beta_0-\mathbf z_i^{\mathsf T}\boldsymbol\beta)^2+\alpha\lVert\boldsymbol\beta\rVert_2^2\right].
$$

Here, 𝒯 denotes training observations, z_i denotes predictors standardized using training means and standard deviations, and α controls coefficient shrinkage. The intercept is unpenalized. This provides a compact linear comparator to nonlinear tree ensembles; random forests aggregate randomized trees to address more complex response surfaces (Breiman, 2001).

Twenty-one candidate configurations were evaluated. Ridge used α∈{0.01,0.1,1,10,100,1000}. Forests used 200 trees, all predictors available at each split, depths of 10 or unrestricted, and minimum leaf sizes of 1, 5 or 15. Boosting used 250 iterations, minimum leaf size 20, learning rates 0.05 or 0.1, 15 or 31 leaf nodes, and L2 penalties of 0 or 1; internal early stopping was disabled. All preprocessing and fitting used training data only. Minimum validation RMSE determined each family's configuration and the overall choice, with the first candidate resolving exact ties. Selections were saved before test evaluation; no training-plus-validation refit or test-based retuning occurred. The random seed was 20260915.

The baseline was the mean CO of the training partition, rather than a mean recomputed from the later test period. Similarly, standardization statistics were estimated before validation or test transformation. Retaining these operations inside each saved pipeline ensures that evaluation applies the stored training statistics. The candidate grid was intentionally finite and common to the recorded protocol. Its outcome compares these specified configurations; it does not establish the best possible algorithm or exhaust every nonlinear calibration strategy.

## Metrics and uncertainty procedure

For n held-out observations, errors were evaluated using

$$
\mathrm{MAE}=\frac1n\sum_i|\widehat y_i-y_i|,\qquad \mathrm{RMSE}=\sqrt{\frac1n\sum_i(\widehat y_i-y_i)^2},\qquad R^2=1-\frac{\sum_i(\widehat y_i-y_i)^2}{\sum_i(y_i-\overline y)^2}.
$$

Here, y_i denotes reference CO and its hatted counterpart denotes the prediction; the reference mean is calculated over the scored observations. MAE and RMSE retain mg m⁻³ units; R² is dimensionless. Mean prediction-minus-reference residual reports directional bias. Predictions were not clipped.

The test block spans 48 observed calendar days, with 10–24 eligible hours per day. Two thousand bootstrap replicates sampled these complete observed-day blocks with replacement, keeping the same sampled indices across model families. Variable-length days retained their available hours without interpolation. The 2.5th and 97.5th percentiles form conditional score intervals. Within-day dependence is preserved, but dependence across days, fitted-model uncertainty and missing-data uncertainty are not incorporated. These intervals therefore describe variability of frozen-model scores under this resampling scheme, not prediction intervals for future readings. Published calibration comparisons using withheld dates and locations provide complementary evidence that the validation design affects the question answered (Barkjohn et al., 2021).

[[FIGURE: research/licensed_figures/barkjohn2021_fig4.png]]

Caption provenance: external PurpleAir calibration errors under date- and state-withholding evaluation; Barkjohn et al. (2021), original Figure 4, reproduced under CC BY 4.0.

## Held-out results and diagnostic interpretation

Ridge with α=10 achieved the lowest validation RMSE, 0.6853 mg m⁻³, compared with 0.6900 for random forest, 0.8202 for boosting and 1.5136 for the mean baseline. Its test RMSE was 0.5020 mg m⁻³, with a 95% daily-block interval of 0.4353–0.5688; MAE was 0.3574 (0.3135–0.4062), and R² was 0.8480 (0.7971–0.8868). Mean bias was −0.1571 mg m⁻³, indicating underprediction on average. The paired RMSE reduction against the mean baseline was 0.8039 mg m⁻³ (0.7014–0.9030).

The selected forest used unrestricted depth and a minimum leaf size of 15. Its test RMSE was 0.4871 mg m⁻³, slightly below Ridge, but this later ranking does not alter the locked choice. Boosting selected learning rate 0.05, 31 leaves and zero L2 penalty; its test RMSE was 0.5651 mg m⁻³. The mean baseline returned RMSE 1.3059 mg m⁻³ and R²=−0.0283. All families remain reported. Overlapping bootstrap intervals are not interpreted as a formal equivalence test, and aggregate error alone does not establish adequate performance during uncommon high-concentration events.

[[FIGURE: analysis/ml_outputs/figures/02_test_metrics.png]]

Caption: Original frozen-test MAE, RMSE and R², with percentile intervals from 2,000 paired calendar-day resamples. The asterisk identifies validation-selected Ridge. Source data: Vito (2008), CC BY 4.0; external-data analysis.

The chronological trace and hourly agreement plot retain the full test period rather than selecting a favourable episode. Humidity-conditioned residual plots use fixed 10-percentage-point bins with at least 20 observations; displayed ranges are interquartile spreads, not confidence intervals. Validation and test mean CO were 2.2337 and 1.9329 mg m⁻³, respectively; corresponding mean RH values were 53.79% and 51.49%. These distribution differences may contribute to the lower test errors, although the present analysis does not isolate their effects. R² also depends on target variance and should accompany absolute error.

[[FIGURE: analysis/ml_outputs/figures/03_selected_model_predictions.png]]

Caption: Original Ridge predictions: complete held-out daily summaries, hourly agreement counts and residual distribution. Source data: Vito (2008), CC BY 4.0; no simulated points or rover observations.

[[FIGURE: analysis/ml_outputs/figures/04_residual_humidity.png]]

Caption: Original hourly residuals by RH for all frozen families; markers denote bin means and bars denote interquartile ranges. Source data: Vito (2008), CC BY 4.0.

Eligible observations covered 75.41% of hours within the training span, 78.05% within validation and 97.61% within testing. This change matters because the scored populations differ in both season and data availability. Hourly scores weight each available observation equally, whereas a displayed daily average summarizes a varying number of measurements. The day bootstrap resamples observed clusters without manufacturing unrecorded hours; it cannot reconstruct pollution episodes lost during sensor or reference outages. Consequently, the manuscript reports the cleaning audit and coverage alongside predictive performance. A later rover study should document acquisition failures prospectively and evaluate whether missingness is associated with humidity, concentration or actuator operation before adopting the same eligibility rule.

## Computational cost, reproducibility and transfer limits

Desktop measurements included preprocessing and used one-worker settings with one-thread BLAS/OpenMP execution. The recorded environment comprised Python 3.12.14 and scikit-learn 1.9.1 on Windows 11, with processor identifier Intel64 Family 6 Model 183 Stepping 1. Each model received three full-batch warm-up predictions before 21 repetitions, each timing a batch prediction and a single-observation prediction. Median single-observation prediction times across 21 warmed repetitions were 0.583 ms for Ridge, 5.819 ms for the forest and 1.707 ms for boosting. Their uncompressed serialized pipelines occupied 1,937, 4,899,034 and 920,233 bytes respectively. These measurements describe the current desktop implementation, not embedded RAM, flash, energy or real-time feasibility. Validation-only permutation sensitivity, evaluated over ten repeats after selection, was largest for PT08.S2(NMHC): shuffling it increased RMSE by 1.3255 ± 0.0201 mg m⁻³ (mean ± standard deviation over ten permutations). Correlated predictors and distribution disruption preclude interpreting this ranking as chemical specificity or causation.

[[FIGURE: analysis/ml_outputs/figures/05_desktop_cost_and_sensitivity.png]]

Caption: Original serialized sizes, desktop prediction-time medians and interquartile ranges, and validation permutation sensitivity with repeat standard deviations. Source data: Vito (2008), CC BY 4.0. Desktop costs do not establish onboard feasibility.

The archive hash, software versions, source-row assignments, candidate scores, frozen models, predictions and bootstrap distributions are retained. Reloaded artifacts reproduce predictions within an absolute tolerance of 10⁻¹². Nevertheless, the experiment uses historical fixed-station sensors with different materials and electronics from the proposed MQ array. Excluding unavailable targets and sensor outages can also introduce selection bias. Transfer to A3P5 therefore requires rover-specific reference collocation, heater-aware acquisition, independent later deployments and deployment-hardware measurements. The present contribution is an auditable calibration benchmark and a testable development route, not demonstrated autonomous environmental accuracy.
