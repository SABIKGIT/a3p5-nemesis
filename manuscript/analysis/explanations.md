# Reproducible analytical study

## Evidence status
All figures and numbers are calculated from explicit assumptions. This engineering analysis contains no measured rover trials. The separate external-data machine-learning benchmark is archived under ml_outputs/. Geometry is estimated from the visual model. These results screen design choices and define measurements needed; they are not a proof of mission capability.

## Coordinate, unit and parameter definitions
The body origin is the ground-plane projection of chassis center on the level reference support plane: x forward, y left, z up. COM height is measured above that support plane. Wheelbase L=0.908 m, track W=0.930 m and wheel radius r=0.140 m are estimated. Base mass is assumed 24.0 kg, with center of mass (0,0,0.58) m; added payload is at (0.8,0,1.0) m. The base COM is held fixed: changes in arm-link mass distribution, suspension compliance and wheel lift are omitted. Full assumptions and CSV data are in analysis_results.json and tables/.

## 1. Independent steer-and-drive kinematics
Wheel velocity is u_i=v_x−ωy_i, v_i=v_y+ωx_i; steering δ_i=atan2(v_i,u_i); rolling speed s_i=sqrt(u_i²+v_i²). Equivalent (δ+π,−s) is used to put displayed angles within ±90°. This mathematical equivalence is not confirmation of hardware steering limits. Zero-speed steering singularities, steering-rate feasibility, scrub and cable limits must be handled in implementation. Ideal straight wheel speed at 0.25 m/s is 17.052315 rpm.

## 2. Grade, rolling resistance and output torque
F=m[a+g(sin α+Crr cos α)], τ_w=Fr/4, and minimum uniform friction μ_min=tan α+Crr+a/(g cos α). Crr=0.06 and g=9.80665 m/s². Four equal longitudinal force shares are assumed. τ_w is required gearbox-output torque, so drivetrain efficiency must not be used to divide it a second time when comparing output-shaft motor data. Continuous torque and thermal ratings, steering losses, terrain deformation and unequal loads are missing. The simple Coulomb screen is necessary under these assumptions, not sufficient for soft-soil traversal.

| Grade | Force (N) | Wheel torque (N m) | Minimum μ | Battery power (W) | Endurance (h) |
|---:|---:|---:|---:|---:|---:|
| 0° | 14.121576 | 0.494255 | 0.060000 | 24.412992 | 3.478271 |
| 10° | 54.776803 | 1.917188 | 0.236327 | 37.117751 | 2.287719 |
| 20° | 93.767665 | 3.281868 | 0.423970 | 49.302395 | 1.722330 |
| 30° | 129.909444 | 4.546831 | 0.637350 | 60.596701 | 1.401314 |

Power/endurance columns assume speed 0.25 m/s and 20 W auxiliaries throughout a constant grade.

## 3. Static payload stability
p_COM=(m_base p_base+m_payload p_payload)/(m_base+m_payload). The front-edge margin is L/2−x_COM−h_COM tan β, where β slopes downhill toward the front. The ideal geometric front-tip angle is atan[(L/2−x_COM)/h_COM]; lateral tip angle uses (W/2−|y_COM|)/h_COM. These are zero-margin geometric tipping bounds, not safe operating slopes. Dynamic motion, obstacles, tire compliance, ground contact uncertainty, external arm force and actual arm-link motion must reduce the allowable operating envelope.

| Added payload (kg) | COM x (m) | COM z (m) | Front tip (deg) | Lateral tip (deg) | Front margin at 20° (m) |
|---:|---:|---:|---:|---:|---:|
| 0 | 0.000000 | 0.580000 | 38.052369 | 38.719993 | 0.242897 |
| 1 | 0.032000 | 0.596800 | 35.264305 | 37.924135 | 0.204783 |
| 2 | 0.061538 | 0.612308 | 32.658035 | 37.213840 | 0.169600 |

## 4. Power and endurance
Usable energy E=11.1 V×10 Ah×0.85×0.90=84.915000 Wh. The 0.90 factor derates available battery energy; it is separate from traction conversion efficiency. Battery power P=Fv/0.80+P_aux. Endurance t=E/P; hypothetical distance is v×t. Battery capacity, low-voltage cutoffs, temperature, current-induced voltage sag, motor maps and auxiliary load must be measured. No regenerative braking is modeled. Constant-grade operation is a stress scenario, not a route prediction. No solar contribution is included.

## 5. Response lag while moving
For a first-order step model y(t)=1−exp(−t/τ), t90=τ ln(10), t95=τ ln(20), and spatial distance traveled before response fraction p is v t_p. Time constants 5,15,30 s are illustrative assumptions, not MQ-sensor datasheet or calibration values. Real sensors can have humidity effects, cross-sensitivity, heater transients, nonlinearity and asymmetric recovery. Even stopping to dwell cannot provide chemical selectivity.

| Assumed τ (s) | t90 (s) | t95 (s) | Distance to 90% at 0.25 m/s (m) |
|---:|---:|---:|---:|
| 5 | 11.512925 | 14.978661 | 2.878231 |
| 15 | 34.538776 | 44.935984 | 8.634694 |
| 30 | 69.077553 | 89.871968 | 17.269388 |

## 6. Stopping-clearance scenario
Required clear distance d=v t_latency+v²/(2a)+d_margin. The figures sweep assumed latency and available deceleration, with margin 0.15 m. Available deceleration is a measured ground-level quantity that must include slope and slip effects; the formula assumes constant braking during the modeled interval. Human approach, obstacle motion and mechanical emergency-stop run-down are omitted.

| Speed (m/s) | Clearance at latency 0.3 s, a=0.5 m/s², margin 0.15 m (m) |
|---:|---:|
| 0.25 | 0.287500 |
| 0.4 | 0.430000 |
| 0.6 | 0.690000 |
| 1.0 | 1.450000 |

## 7. Nernst slope and analog conditioning
The ideal monovalent electrode slope is S(T)=ln(10) R(T+273.15)/F. R=8.31446261815324 J mol⁻¹ K⁻¹; F=96485.33212 C mol⁻¹. An explicitly assumed positive-gain conditioning circuit maps V_ADC=2.5+3 S(T)(7−pH). Electrode polarity can be reversed in actual hardware. At 25°C the magnitude is 59.159350 mV/pH. A Mega-compatible 5 V, 10-bit ADC scenario has 1024 codes indexed 0…1023. Its ideal least-significant-bit (LSB) input interval is Vref/2^N = 5/1024 V, equal to 4.882812 mV. The maximum output code is 1023; it does not define the denominator for the physical quantizer interval. The table records a continuous ideal code coordinate, not simulated integer conversions. The 5 V reference must be measured; the nominal supply is not an accuracy standard.

With gain 3, the ideal pH increment per ADC LSB is 0.02751221. The pH 0 and 14 outputs are 3.742346 V and 1.257654 V. The maximum ideal gain for a symmetric full pH 0–14 span at 25°C is 6.036964; practical rail/headroom constraints reduce it. Quantization is not accuracy: buffer calibration, electrode condition, temperature compensation, very high input impedance, input bias current and analog noise dominate real pH uncertainty. For comparison, a proposed 3.3 V, 12-bit front end with gain 3 and midpoint 1.65 V gives an ideal increment of 0.00453951 pH/LSB. This is a proposed acquisition design, not proof the present hardware achieves it. An electrode cannot be connected directly to a MCU ADC: a very-high-input-impedance buffer/conditioner and compatible offset/gain are required for either case. ADC resolution and usable effective resolution must not be conflated.

## 8. Sensitivity and reproducibility
Figure A08 changes one assumed input by ±20% at a time and holds all other inputs constant; it is a deterministic sensitivity sweep, not a probability distribution or confidence interval. This isolates which measurements are most valuable without inventing experimental uncertainty. The endurance reference is 2.287719 h. The second panel varies unknown base COM height to demonstrate why photo-based tipping claims are unreliable.

Run engineering_analysis.py with the bundled Python runtime after installing matplotlib into manuscript/python_packages. Numeric tables use deterministic grids with no random numbers. Each PNG is saved at 360 dpi and each SVG retains editable text. No external plot or dataset is republished.

## Supporting theory references
The independently derived kinematic and contact assumptions are consistent with Alexander and Maddocks (1989), Lee and Li (2015), and Iagnemma and Dubowsky (2004); the stability limitations are motivated by Papadopoulos and Rey (1996). Refer to research/mobility_sources.json for exact primary-source citations. Equations here are explicitly stated elementary model derivations, not copied reported results.

## Priority measurements
Measure complete mass and COM in several arm poses; loaded wheel radius; motor continuous output torque/current/temperature; tire friction and rolling losses on each surface; actual controller/watchdog latency and braking distance; battery usable energy at duty cycle; sensor step/recovery response; calibrated analog pH transfer and uncertainty. Report successful and failed trials separately from these analytical design screens.
