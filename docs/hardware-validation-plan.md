# Hardware validation plan

**Status: proposed; NOT_EXECUTED.** No integrated rover trial logs, measured mass/COM, motor curves, environmental co-location data or autonomy trajectories were supplied for this study. The CSV files in [test-records/](test-records/) are unfilled templates. Their prefilled text defines proposed work; it is not an experimental result.

The plan operationalizes manuscript Sections 4–11 and preserves the photographed configuration: four outboard wheel modules, central enclosure, folded deck-mounted arm, inclined mast and side sampling equipment. It does not add a solar panel. Proposed LiDAR, depth sensing, humidity measurement and companion computation must be identified as additions until their installation is documented. Photograph-visible servos do not establish steering-angle feedback, encoders or a validated control stack.

## Evidence and progression

1. **Identify the actual configuration.** Record component identities, geometry, mass distribution, wiring, firmware and calibration records. Replace visual estimates only with traceable measurements.
2. **Characterize subsystems.** Establish loaded drivetrain, steering, power, measurement and stop behaviour under controlled conditions. Retain failed starts and interventions.
3. **Evaluate integration.** Test coordination, measurement timing, sample handling, authority transitions and complete missions within the identified envelope.
4. **Assess generalization.** Repeat across predefined surfaces, loads, days and environmental conditions. A successful demonstration is not a validated operating region.

The existing calculations set questions to test. They do not set test limits: 24 kg is not a weighed mass; 2 kg is not an approved payload; 20° is not an approved slope; 0.430 m is not a demonstrated stop clearance. See [engineering-calculations.md](engineering-calculations.md).

## Define acceptance before a run

Every protocol needs a configuration ID, scope, measured variables, units, reference instrument, uncertainty method, repetition plan, exclusion rules, numerical thresholds where needed, abort conditions, and a versioned decision rule. Define these **before** examining results. No numerical acceptance limits are established in this repository.

For example, a steering protocol may define a maximum absolute tracking error and a settling-time limit. A calibration protocol may define acceptable bias/error on separately held-out days within a stated environmental domain. The template leaves both limits blank. The reviewer cannot assign `PASS` while the criteria are unspecified or the measurements absent. Do not choose thresholds after seeing the observed error and describe them as preregistered.

Criteria definitions below are proposals for a test designer, not a declaration of compliance with a safety or certification standard. The manuscript's NIST response-robot reference supplies task-decomposition context; this project has not demonstrated compliance with that programme.

## Proposed test families

| ID | Scope and measurements | Acceptance-rule definition to complete before execution |
|---|---|---|
| HV01 | As-built geometry, component identity, loaded radius, total mass and firmware/configuration record | Required records complete; repeated measurements meet a declared uncertainty/repeatability budget. No assumed mass substituted for a measurement. |
| HV02 | Loaded drive speed, output torque or force, voltage, current and temperature over a declared duty interval | Tracking and continuous thermal/current limits satisfy identified component ratings and a predefined operating requirement. Stall ratings cannot serve as continuous limits. |
| HV03 | Steering zero, travel, backlash, rate, loaded current and independent angle feedback | Error/rate/settling limits met throughout the declared range without interference, limit violation or overload. |
| HV04 | Repeated straight, crab and coordinated-turn motion with independent pose observations | Predefined path/heading error and saturation/intervention limits met on every stated surface/load condition; wheel commands and achieved motion reported separately. |
| HV05 | Cable/hose clearance, retention and strain through the identified steering/arm sweep | No contact, trapped loop, loss of retention or unapproved bend during the documented sweep; component-specific bend/retention requirements identified before testing. |
| HV06 | COM in several arm/payload states, wheel loading and measured support geometry | Measured uncertainties and load cases support a predefined conservative envelope. Do not deliberately seek the model's zero-margin tipping angle. |
| HV07 | Known sample payload, grasp/place outcome, retention, contact forces, reach and arm/chassis interlock | Prespecified placement/retention criteria met; configuration remains within measured joint/load/support limits and recovery behaviour is recorded. |
| HV08 | Battery voltage/current, usable energy, rail stability, temperature, dwell/motion demand and runtime | Duty-cycle requirement met within identified pack/regulator limits and approved cutoff policy; no unexpected reset or measurement-reference disturbance. |
| HV09 | Stop trigger, actual detection/command delay, speed, distance, ground conditions and final actuator state | Measured distance/response state satisfy the declared clearance and time budget, including repeatability/uncertainty. Commanded braking and energy interruption assessed separately. |
| HV10 | Command arbitration, sequence/timestamp checks, link loss, stale commands, low-voltage indication and reset | Every defined injected condition produces the specified state within its declared time budget; no unintended restart or competing authority. |
| HV11 | Gas-channel identity, heater waveform/phase, raw output, reference exposure, humidity/temperature and recovery | Channel-specific, reference-based error and response criteria met on independent exposures/days within the declared domain. No assumed chemical selectivity. |
| HV12 | Particle reference co-location, humidity, inlet conditions, time alignment and motion/dust context | Held-out correction error, drift and validity flags meet declared criteria across documented aerosol/humidity conditions. |
| HV13 | pH buffers/temperature, conditioning transfer, electrode state, stabilization, turbidity standards, rinsing and sample identity | Independent check solutions/standards and repeats meet predefined error/uncertainty limits; sample handling preserves identity and contamination controls. |
| HV14 | Exact UV board, optical/reference response, pressure and temperature reference checks | Conversion and reference agreement meet defined domain/error criteria. BMP180 data are not used as a relative-humidity measurement. |
| HV15 | Installed navigation sensors, synchronization, extrinsics, independent pose, obstacle clearance and degraded localization | Defined route/clearance/recovery requirements met with documented takeover and failure rules. A rendered patrol scene is not a navigation test. |
| HV16 | Complete inspection, stationary sensing, staged-vessel water assessment, lightweight handling or visual-reconnaissance mission | Mission-specific completion condition, valid observation rate, time/energy requirement and abort/recovery conditions met within the already characterized configuration. |

### Mission completion is evidence-specific

- **Environmental observation:** obtain a valid, timestamped, appropriately stabilized sample with calibration and location context; merely reaching a station is insufficient.
- **Water assessment:** demonstrate the actual access and immersion arrangement, reference checks, stabilization, rinsing and sample tracking. The current scene uses a staged vessel on dry support; it does not establish river deployment or water-ingress protection.
- **Lightweight handling:** document load, contact and retention, final placement and return to a verified travel state. A gripper photograph is not a payload rating.
- **Visual reconnaissance:** retain interpretable imagery and the observation location while respecting measured mobility and stop limits. The debris render is not a rubble-traversal result.
- **Proposed autonomous patrol:** identify installed sensors/software, pose reference, route outcomes, interventions and recovery. External UCI calibration results are not autonomy evidence.

## Records and data handling

The three CSV templates deliberately separate planning, raw observations and conclusions:

| File | One row represents | Initially blank fields |
|---|---|---|
| [test-plan.csv](test-records/test-plan.csv) | A proposed test family with its units, conditions, criterion definition and source | Approved limits, repetitions, protocol owner/date |
| [measurement-log.csv](test-records/measurement-log.csv) | A planned metric channel; copy rows for actual timestamped observations | Trial ID, timestamp, measured/reference value, uncertainty, instruments and raw-file provenance |
| [trial-log.csv](test-records/trial-log.csv) | A placeholder for a future executed trial; assign a unique ID for each repetition | Configuration, environment, dates, results, interventions, evidence files and reviewer |

All rows begin `execution_status=NOT_EXECUTED`. Trial conclusions begin `assessment_status=NOT_ASSESSED`. Numeric blanks mean **not measured/not supplied**, not zero and not a successful test. Metadata such as a metric name or unit is allowed to be prefilled; measured values and results are not.

Before execution, copy the templates into a new campaign directory, set unique protocol/trial/configuration IDs and commit the plan revision. Do not overwrite the distributed unfilled templates. Define timestamp timezone and synchronization error. When recording local timestamps, include the offset or retain the convention explicitly; do not silently label unsynchronized clocks UTC.

For each raw data file, retain its path, SHA-256, instrument/channel identity, units, acquisition method, calibration version and analysis-code commit. Keep raw observations immutable. Link processed results back to source rows, and record exclusions with reasons. Report all planned and attempted repetitions, aborted trials, protective stops and human interventions. Many samples from one run do not automatically constitute independent repeated trials.

The unit `1` denotes a dimensionless quantity; `pH` denotes the conventional pH scale, not volts. Use `V`, `A`, `W`, `Wh`, `N`, `N*m`, `m`, `m/s`, `m/s^2`, `s`, `deg`, `degC`, `Pa` and `%RH` as appropriate. A reference value must have the same unit and measurand as the recorded measurement or an explicitly documented conversion. Store compound conditions as named fields or a referenced configuration file, rather than silently changing their meaning between trials.

## Review and release gate

A completed trial record may use `execution_status=EXECUTED` or `ABORTED`; neither implies a pass. Use `assessment_status=PASS`, `FAIL` or `INCONCLUSIVE` only after review against the versioned criteria and attached evidence. Keep `NOT_ASSESSED` where criteria, data or review are incomplete. A change in mechanism, battery, firmware, sensor, calibration or mass distribution must identify which prior results remain applicable.

Publish outcomes with the tested configuration, full conditions, repetition counts, uncertainty, exclusions and limitations. Keep hardware records separate from `manuscript/analysis/tables/` and `manuscript/analysis/ml_outputs/`, which contain analytical scenarios and an external-data experiment respectively. Future empirical data must never be presented as part of the existing unexecuted record.

## Provenance

The plan derives from [manuscript Sections 4–11](../manuscript/text/manuscript_ieee.md), the [calculation assumptions/results](../manuscript/analysis/analysis_results.json) and the [external benchmark protocol](../manuscript/analysis/ml_outputs/benchmark_protocol.json). Each template row includes a source path, source section and source SHA-256. These hashes identify the document revision used to prepare the proposed test definition; they are not measurement-file hashes or evidence that a test occurred.
