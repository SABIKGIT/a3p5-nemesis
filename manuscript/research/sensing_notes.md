# Environmental sensing and ML evidence notes

## Scope and evidence boundary

This targeted set contains 25 sources verified on 15 September 2026. It is not a systematic review of thousands of papers. Read depth is recorded source by source. No A3P5 field logs, calibration data, ML labels, trained models or performance measurements were provided. Literature experiments remain external evidence. Blender mission images represent design intent; they cannot establish successful missions or CFD results.

## Corrections to the hardware narrative

- MQ135 is a nonspecific gas-response channel, not a selective calibrated CO2 instrument. Initial conditioning, stable heater supply, sensor-specific calibration and interference tests are required [SEN01]. For quantitative CO2, describe NDIR as a proposed addition.
- Exact MQ7 marking and board schematic need verification. The reference MQ-7B uses alternating heating phases. Its timings, voltages and detection range must not silently transfer to an unidentified MQ7 module [SEN02].
- MQ4 range is not accuracy. Methane readings require independent calibration. TGS2600 findings justify temperature, humidity and CO-interference tests but are not an MQ4 calibration [SEN03,SEN24].
- PMS7003 needs unobstructed sheltered intake/outlet away from wheel dust, motor heat and water spray. Store raw/corrected data and quality flags. The Delhi study actually used PMS7003, but its network model is not a ready-made rover calibration [SEN10].
- BMP180 measures pressure and temperature, not relative humidity. Add a clearly proposed RH channel near the air intake for PM calibration [SEN04,SEN08,SEN11,SEN12].
- The pH and turbidity probe models are not identified. DFRobot sources are candidate reference designs only. Use buffer/turbidity standards, repeats, blanks, temperature, stabilization, rinse/carryover control and maintenance logs [SEN06,SEN07,SEN16,SEN17,SEN25]. pH and turbidity alone do not establish potability.
- GUVA board gain and exposure geometry need verification. Raw voltage does not establish calibrated erythemal UV index [SEN05].

## Proposed mathematical analyses

For each resistive gas channel, Rs = RL(Vc/VRL - 1), with regulated supply Vc and measured load voltage VRL. Log voltage and heater phase before calibration. A candidate log-linear curve is log(Rs/R0) = a + b log(c). Its inversion applies only to a known target gas within experimentally established conditions. a, b and R0 must be measured, not guessed from a generic graph. Mixed-air channels should remain response indices until a multivariate estimator is independently validated [SEN01-SEN03].

For PM, compare a transparent calibration c_ref = beta0 + beta1 c_raw + beta2 RH + beta3 T + epsilon with uncorrected data. Keep unclipped predictions for residual diagnostics. A literature-derived humidity sensitivity study may use c_dry = c_raw*m/[1 + kappa/(100/RH - 1)], where RH is percent. m and kappa are assumed parameters until local calibration, and the expression is not a validated PMS7003 correction [SEN11,SEN12].

Mobile sensing has spatial lag d_lag = v*tau. Illustrative assumptions v=0.15 m/s and tau=10 s yield 1.5 m lag; this is a calculation, not a measured rover property. The first-order model tau*dc_s/dt + c_s = c_environment can support speed/response-time sweeps. Choose stationary sample dwell from measured step-response settling. Timestamp every location; sequential samples must not be presented as a simultaneous concentration field [SEN13,SEN14].

For a proposed spatial Gaussian process, mu*=k*^T(K+sigma_n^2 I)^-1 y and sigma*^2=k**-k*^T(K+sigma_n^2 I)^-1 k*. Plot the predicted mean and uncertainty together, mark extrapolation and unvisited cells, and avoid interpolating through walls without a justified obstacle model. Model uncertainty does not include every source of physical measurement error [SEN10,SEN14,SEN23].

## Proposed ML study (no model trained)

1. Log timestamp, mission, pose/location uncertainty, raw channel values, heater phase, T/RH/pressure, sensor serial, battery voltage, calibration version, maintenance and validity flags.
2. Collect collocated reference observations and distinguish true environmental events from sensor faults or contamination.
3. Split by independent mission/day/site/sensor according to deployment. Keep the final external test set untouched; imputation, scaling, feature selection and hyperparameter tuning belong inside training folds [SEN19,SEN20].
4. Compare linear calibration, random forests and Gaussian processes. Isolation Forest can flag unusual patterns but cannot identify a pollutant or diagnose a hazard by itself [SEN21-SEN23].
5. Report MAE, RMSE, bias, interval coverage and errors stratified by humidity, temperature, concentration and site. For detection, report event-level precision/recall, missed events, false alarms per hour and delay with uncertainty intervals grouped by independent mission/site.
6. Do not discard actual pollution peaks just because they are outliers. Audit exclusion decisions and data completeness.
7. Measure compute time, memory, power and communications on actual electronics before claiming real-time Mega/ESP32 inference.

## Mission visualizations and licensed evidence

A rendered plume must be labeled schematic. GADEN is a possible subsequent gas-transport simulation tool [SEN13], not a name for Blender staging. If wind-aware mapping is proposed, identify the anemometer and additional computation as additions. Show accessible sampling poses and cable management. No airboat result implies that A3P5 is amphibious.

Four unmodified publisher PNGs are in research/licensed_figures. Exact image/source links, CC BY 4.0 license URLs, and captions are recorded in sensing_sources.json and licensed_figures/provenance_download.json. Their publisher pages explicitly declare the license. All images decoded successfully and were visually inspected in a montage.

- Jayaratne 2018 Fig.2: 645x492, empirical humidity-response plot; use at modest width.
- Patel 2024 Fig.4: 2067x723, three calibration scatterplots; suitable for full column. Vector original: https://amt.copernicus.org/articles/17/1051/2024/amt-17-1051-2024-f04-high-res.pdf
- Zheng 2019 Fig.4: 2067x1996, network boxplots; use near full width if selected.
- Barkjohn 2021 Fig.4: 1378x1372, validation-error boxplots; useful beside blocked-validation design.

Every caption must explicitly identify these as the cited studies' data, not A3P5 results. Keep attribution and license links. If cropped or relabeled, describe the modification. Do not transfer any published coefficient or accuracy number to the rover.
