## 8. Power, embedded control and communications
### 8.1. Electrical power architecture
The project description identifies a typical 3S LiPo configuration at 11.1 V nominal. Battery capacity, discharge capability, protection thresholds and usable energy at the intended duty cycle are not documented. The design therefore separates battery selection from an illustrative energy calculation. A fused input and service disconnect feed distinct motor, servo, logic and sensor branches. High-current switching paths should be routed so that their voltage drops and transients do not become the reference for sensitive analog measurements.

!FIG[diagrams/canva_02.png|Canva-created power architecture. Motor, servo, logic and sensor branches have distinct regulation and protection roles. Conductor and fuse ratings must follow measured current and component specifications. This is not a verified wiring schematic.|3.0]

The servo branch requires a regulator selected for simultaneous transient loads rather than average current alone. The gas-sensor heater supply should preserve the required waveform independently of ADC sampling. The logic branch needs a defined brownout response, and inter-board signals need voltage-compatible levels. A common reference may be necessary between boards, but high-current returns should not impose uncontrolled offsets on analog measurement ground.

In the declared scenario, a 10 Ah battery, 0.85 depth-of-discharge factor and 0.90 available-energy derating yield 84.915 Wh. These factors are assumptions, not measured battery characterization. Mechanical traction power is divided by a separate drivetrain conversion efficiency of 0.80 and added to an assumed 20 W auxiliary load. The two factors serve different roles and are not repeated corrections to the same quantity.

!EQ[E_{\mathrm{use}}=V_{\mathrm{nom}}C_{Ah}f_{DoD}f_E]
!EQ[P_{\mathrm{bat}}=\frac{F_{\mathrm{req}}v}{\eta_d}+P_{\mathrm{aux}},\qquad t=\frac{E_{\mathrm{use}}}{P_{\mathrm{bat}}}]

!FIG[analysis/figures/A04_energy_endurance.png|Calculated endurance under declared battery, load and constant-grade assumptions. The model omits voltage sag, temperature-dependent capacity, intermittent arm motion and detailed motor efficiency maps. It is an energy budget, not a measured runtime.|3.0]

At 0.25 m/s the calculated level-ground demand is 24.41 W, giving 3.48 h. A continuous 20° grade raises demand to 49.30 W and reduces the estimate to 1.72 h. A real route combines acceleration, stops, steering, slopes and sampling dwell, so neither value predicts a route. Current and voltage logging during representative missions should replace the constant-load approximation, and the battery should be characterized at the relevant temperature and discharge threshold.

### 8.2. Scheduling and data integrity
Low-level software should separate actuator timing from slower environmental acquisition and network traffic. A bounded control update should not wait for a web request or a slow sensor response. Each acquisition task should expose its latest valid value, acquisition timestamp and age rather than block the scheduler until a sensor is ready. Heater-cycle sensors require a state variable identifying when a reading is chemically and thermally interpretable. Delayed and invalid samples should remain visible in the log.

A useful record schema includes mission ID, monotonic sequence number, acquisition time, sensor ID, raw value, engineering value, unit, calibration version, validity flags, battery state and estimated pose with uncertainty. Monotonic time supports ordering within a run; wall-clock time supports comparison with reference instruments. Synchronization uncertainty should be recorded because assigning a delayed gas response to a precise coordinate can create a visually sharp but physically misleading map.

!TABLE[Interface|Primary responsibility|Required checks;Sensor to low-level controller|Acquire and timestamp raw data|Range, checksum, heater phase, warm-up, age;Low-level to communications|Publish actual state and faults|Sequence continuity, units, calibration version;Operator to arbiter|Request mode and bounded motion|Authority, freshness, limits, deliberate enable;Companion to low-level controller|Propose velocity or arm action|Expiration, feasibility, health conditions;Hardware protection to motor branch|Remove or inhibit drive energy|Independent wiring, latch state, reset;Logger to analysis pipeline|Retain reproducible evidence|Raw data, configuration and provenance]

### 8.3. Local networking and operator authority
A local access point allows a nearby operator to communicate without external Wi-Fi infrastructure. This is a connectivity arrangement, not a guarantee of range or resilience in a damaged building. Antenna placement, multipath, obstruction, competing traffic and power noise affect link quality. Video needs a separate bandwidth budget from command and health messages so that a large image stream cannot indefinitely delay a stop request or conceal stale state.

!FIG[diagrams/canva_11.png|Canva-created communications and dashboard architecture. Local Wi-Fi supports browser access, while radio control can provide an alternate command source. The arbiter permits one active authority and rejects stale requests.|3.0]

Manual, radio and autonomous requests should enter one arbiter with an explicit priority policy. A mode change should require neutral commands and a known actuator state. Commands must expire: an old packet received after an outage must not restart motion. The dashboard should distinguish requested mode from active mode and show the age of the last accepted command. Sensor validity and calibration status belong beside the value, preventing an uncalibrated indicator from appearing as an authoritative concentration.

## 9. Navigation, mission concepts and protection
### 9.1. Proposed autonomy architecture
Autonomous navigation requires pose estimation, obstacle representation, a planner respecting vehicle limits and a controller able to realize the motion. None follows automatically from mounting a camera. The proposed architecture adds wheel/steering feedback, an IMU and a range-sensing modality, with a companion processor where required. LiDAR, depth sensing and visual-inertial approaches should be compared under the intended lighting, texture, dust and compute constraints.

!FIG[diagrams/canva_10.png|Canva-created proposed navigation pipeline. Calibration and synchronization feed localization and mapping. Planning accounts for clearance, braking and steering constraints. This describes development architecture rather than a completed autonomous implementation.|3.0]

ORB-SLAM3 and LIO-SAM illustrate different estimation architectures and sensor dependencies (Campos et al., 2021; Shan et al., 2020). Their performance does not transfer to NEMESIS without compatible sensors, calibration, timing, computing resources and evaluation. The dynamic-window approach connects local velocity choice with obstacle and braking constraints (Fox et al., 1997), but a conventional implementation must be adapted to steering-rate limits and the rover footprint. The arm and mast expand the swept volume beyond the chassis rectangle.

!FIG[blender/M05_mission.png|Blender autonomous-patrol concept with proposed deck LiDAR, humidity pod and a compact depth camera below the existing mast head. Route markings are illustrative. Added sensors are proposals; the image is not a logged navigation trial or obstacle-avoidance result.|3.5]

Obstacles should be inflated by clearance incorporating body geometry, localization uncertainty and stopping distance. On degraded localization, a controlled stop may be preferable to continuing along a plausible route. Recovery logic should explicitly request assistance, return to a verified location if feasible, or remain stopped. A successful route in a simple virtual environment cannot establish robustness to reflective surfaces, missing returns, wheel slip or moving people.

### 9.2. Mission-level behaviour
Environmental patrol combines travel and observation. The rover approaches a station, reduces speed, confirms readiness, dwells as required, records the observation and resumes travel. Industrial inspection prioritizes camera access and interpretable environmental indicators while preserving inlet clearance. Water assessment adds sample access and wet/dry boundaries. Disaster reconnaissance emphasizes visual information and cautious movement in uncertain terrain; it does not imply casualty transport or entry into explosive atmospheres.

!FIG[diagrams/canva_13.png|Canva-created mission/data workflow for environmental patrol, industrial inspection, water assessment, lightweight handling and reconnaissance. Quality checks and recovery conditions form part of the mission outcome.|3.0]

!FIG[blender/M01_mission.png|Blender concept of stationary environmental observation near industrial piping. Principal component positions are preserved. No contaminant release, gas concentration, hazardous-area certification or completed field inspection is represented.|3.5]

!FIG[blender/M04_mission.png|Blender visual-reconnaissance concept near debris. The rover remains on a clear support surface; masonry provides context. The scene does not demonstrate rubble traversal, structural assessment or rescue performance.|3.5]

Each task needs a measurable completion condition. An air observation is complete only when a valid sample with adequate timing/context is recorded; reaching a waypoint is insufficient. Manipulation needs confirmation that the object was grasped and placed, not merely that motor commands were issued. Inspection should record view coverage and unresolved occlusions. Abort and recovery events should remain in the dataset, because suppressing them makes the system appear more reliable than it is.

### 9.3. Stopping and fault handling
A software stop and emergency energy interruption serve different purposes. A controlled stop can regulate deceleration and preserve a safe arm state. A hardware emergency-stop circuit needs an independently defined effect on actuator energy and a deliberate reset. Removing all power indiscriminately may let a gravity-loaded joint move, so the mechanism needs a holding or parking strategy. These functions are specified at architecture level; no safety-standard compliance is claimed.

!FIG[diagrams/canva_12.png|Canva-created overview of operating and protective states. Actual transitions depend on explicit health, authority and reset conditions; the visual sequence is not an executable transition specification. Hardware interruption remains distinct from a controlled software stop.|3.0]

The simplified stopping-clearance model combines command latency, braking distance and a geometric allowance. Available deceleration is a ground-level quantity to measure on relevant surfaces and slopes, not an unloaded motor specification. Obstacle motion, slip and the run-down of a hardware power cut may require additional clearance.

!EQ[d_{\mathrm{clear}}=vT_{\mathrm{latency}}+\frac{v^2}{2a_{\mathrm{brake}}}+d_{\mathrm{margin}}]

!FIG[analysis/figures/A06_stopping_clearance.png|Calculated stopping clearance across assumed speed, delay and deceleration scenarios, including a 0.15 m allowance. The curves define quantities for braking trials and do not establish a certified protective distance.|3.0]

At 0.4 m/s, 0.3 s latency, 0.5 m/s² deceleration and 0.15 m margin, calculated clearance is 0.430 m. Raising speed to 1.0 m/s increases it to 1.450 m. The quadratic term explains why speed restriction can matter more than a small improvement in communication delay. Fault injection should test stale commands, receiver loss, low voltage, sensor dropout, encoder inconsistency and controller reset, recording both detection time and actual stopping motion.

@@ML@@
