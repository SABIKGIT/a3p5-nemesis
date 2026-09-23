# Source-checked context and future benchmark options

These 11 leads supplement the metadata census. They were checked at the scope stated below, not all read in full. None demonstrates this rover’s performance. Datasets were identified, not downloaded or tested.

## R01 · Gas source localization and mapping with mobile robots: A review (2022)

Type: review. DOI: [10.1002/rob.22109](https://doi.org/10.1002/rob.22109). [Checked source](https://onlinelibrary.wiley.com/doi/full/10.1002/rob.22109).

Primary starting review for gas-sensing hardware, ground and aerial platforms, source localization, distribution mapping, and informative path planning.

Application limit: Gas mapping needs spatial localization and a measurement model; onboard gas sensing alone does not demonstrate autonomous source localization.

Read scope: Publisher abstract and selected platform/mapping/discussion sections.

## R02 · Low-Cost Outdoor Air Quality Monitoring and Sensor Calibration: A Survey and Critical Analysis (2021)

Type: review. DOI: [10.1145/3446005](https://doi.org/10.1145/3446005). [Checked source](https://arxiv.org/abs/1912.06384).

Starting survey for low-cost air sensor calibration, cross-sensitivity, environmental effects, and drift.

Application limit: Literature calibration methods do not provide calibration coefficients for the rover sensors.

Read scope: Author preprint abstract and bibliographic record.

## R03 · A Review of Low-Cost Particulate Matter Sensors from the Developers’ Perspectives (2020)

Type: review. DOI: [10.3390/s20236819](https://doi.org/10.3390/s20236819). [Checked source](https://pmc.ncbi.nlm.nih.gov/articles/PMC7730878/).

Sensor-developer view of low-cost particulate monitoring and Plantower-family evaluations.

Application limit: Treat calibration and comparison results as sensor-, aerosol-, and deployment-specific.

Read scope: Indexed article excerpt; full page later returned an access challenge.

## R04 · Low-cost monitoring of atmospheric PM—development and testing (2022)

Type: empirical_sensor_evaluation. DOI: [10.1016/j.jenvman.2021.114158](https://doi.org/10.1016/j.jenvman.2021.114158). [Checked source](https://www.sciencedirect.com/science/article/pii/S0301479721022209).

Directly relevant PMS7003 evaluation involving controlled calibration and a 15-month field deployment.

Application limit: Results belong to that study and must not be quoted as A3P5 accuracy, reliability, or maintenance validation.

Read scope: Publisher abstract and highlights.

## R05 · Connected Sensors, Innovative Sensor Deployment and Intelligent Data Analysis for Online Water Quality Monitoring (2021)

Type: review. DOI: [10.1109/JIOT.2021.3081772](https://doi.org/10.1109/JIOT.2021.3081772). [Checked source](https://researchportal.hw.ac.uk/en/publications/connected-sensors-innovative-sensor-deployment-and-intelligent-da/).

Overview linking water sensor parameters, deployment using autonomous platforms, and online data analysis.

Application limit: A wheeled rover requires a specified sampling interface; aquatic-vehicle results are context rather than direct evidence for this chassis.

Read scope: Author institution bibliographic record and abstract.

## R06 · GADEN: A 3D Gas Dispersion Simulator for Mobile Robot Olfaction in Realistic Environments (2017)

Type: simulator_paper. DOI: [10.3390/s17071479](https://doi.org/10.3390/s17071479). [Checked source](https://github.com/MAPIRlab/gaden).

Reproducible gas-dispersion and gas-sensor simulation framework for future navigation and olfaction experiments.

Application limit: A simulator supports controlled algorithm comparisons; it does not validate physical sensor response or field performance.

Read scope: Official project README and supplied citation.

## R07 · VGR Dataset: A CFD-based Gas Dispersion Dataset for Mobile Robotic Olfaction (2023)

Type: simulation_dataset. DOI: [10.1007/s10846-023-02012-z](https://doi.org/10.1007/s10846-023-02012-z). [Checked source](https://mapir.isa.uma.es/mapirwebsite/?p=1708).

Author-provided dataset page describes 120 airflow/gas simulations across 30 detailed house models, with GADEN/OpenFOAM files.

Application limit: These are simulated indoor data; they are neither outdoor emissions observations nor measurements collected by A3P5.

Read scope: Official dataset page and citation.

## R08 · Gas Sensor Array Drift Dataset (2012)

Type: experimental_sensor_dataset. DOI: [10.24432/C5RP6W](https://doi.org/10.24432/C5RP6W). [Checked source](https://archive.ics.uci.edu/dataset/224/gas).

Controlled metal-oxide sensor-array benchmark for drift and calibration-transfer methods.

Application limit: Different sensors and controlled exposure conditions prevent direct transfer of reported model accuracy to MQ135/MQ7/MQ4 devices.

Read scope: Official UCI dataset metadata and variable description.

## R09 · Air Quality (2008)

Type: field_sensor_dataset. DOI: [10.24432/C59K5F](https://doi.org/10.24432/C59K5F). [Checked source](https://archive.ics.uci.edu/dataset/360/air+quality).

UCI reports 9,358 hourly records from five metal-oxide sensors with reference gas measurements; useful for future calibration-method examples.

Application limit: Different equipment and location from the rover. Preserve time order in validation and handle the documented -200 missing-value marker.

Read scope: Official UCI dataset metadata and variable description.

## R10 · Gas sensor array under dynamic gas mixtures (2015)

Type: experimental_sensor_dataset. DOI: [10.24432/C5WP4C](https://doi.org/10.24432/C5WP4C). [Checked source](https://archive.ics.uci.edu/dataset/322/gas+sensor+array+under+dynamic+gas+mixtures).

UCI reports continuous recordings from 16 Figaro sensors under varying methane/ethylene and CO/ethylene mixtures; useful for response-delay and cross-sensitivity methods.

Application limit: Not MQ-series hardware or a rover field benchmark. The page contains a legacy research-only note alongside a CC BY 4.0 label; resolve terms before reuse beyond this bibliographic recommendation.

Read scope: Official UCI dataset metadata and variable description.

## R11 · Gaden-RT: A Real Time and Interactive Gas Dispersion Simulator for Mobile Robotics (2025)

Type: simulator_paper. DOI: [10.1016/j.softx.2025.102388](https://doi.org/10.1016/j.softx.2025.102388). [Checked source](https://github.com/MAPIRlab/gaden).

Current official GADEN project citation for the real-time interactive simulator implementation.

Application limit: Cite the version actually used if future experiments adopt it; no such experiments were performed here.

Read scope: Official project README and supplied citation.
