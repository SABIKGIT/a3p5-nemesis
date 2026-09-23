# Mobility, manipulation and navigation research notes

Prepared 15 September 2026. Scope: 19 selected primary research/official sources. This is a targeted narrative engineering review, not a systematic review or a claim to have read thousands of papers. Titles, source links, access depth and cautions are in mobility_sources.json. Do not use search-hit or citation counts as a reading count.

## Evidence boundary for Nemesis

The supplied description is a design brief, not an experimental dataset. Photographs establish visible external layout; the prior Blender file is an estimated visual reconstruction. The brief explicitly describes autonomous navigation, LiDAR/depth sensing, environmental ML, geotagging and mission planning as development paths. Literature can motivate proposed changes but cannot fill missing measured mass, motor torque, link inertias, steering range, battery capacity, sensor calibration or trial results. No solar panel should be added (user correction).

Suitable manuscript positioning: "a reference-constrained design study and reproducible analytical evaluation of a modular environmental inspection rover." Use "proposed," "assumed," "calculated" and "illustrative simulation" exactly where applicable. Reserve "measured," "validated," "field-tested" and "outperformed" for supplied measurements.

## Proposed locomotion formulation (independent derivation)

Let the body origin be the chassis center, x forward, y left, yaw rate omega about z, and wheel i at (x_i,y_i). On a locally planar rigid support with no slip, the velocity at wheel i is

v_i = [v_x - omega y_i, v_y + omega x_i]^T.

A steer-and-drive command is

delta_i = atan2(v_y + omega x_i, v_x - omega y_i),
Omega_i = norm(v_i)/r_i.

Equivalent commands (delta_i + pi, -Omega_i) may reduce steering travel. Select among feasible equivalents using measured steering limits and cable travel. If norm(v_i) is close to zero, hold the preceding steering angle to prevent numerical angle jumps. For finite steering rates, first align at low/zero traction, then ramp drive speed. All-wheel commands must correspond to one common body twist; four unrelated setpoints induce scrub. See M01–M03.

A small lateral constraint residual useful for logged diagnostics is

e_perp,i = -sin(delta_i)(v_x - omega y_i) + cos(delta_i)(v_y + omega x_i).

This is a model residual, not a direct slip measurement unless body velocity has an independent estimate. Record encoder/steering feedback and fused body motion with synchronized timestamps.

### Drive modes to illustrate

- Straight: omega=0, v_y=0.
- Crab: omega=0 with all wheel headings equal to atan2(v_y,v_x).
- Coordinated turn: omega nonzero and the four wheel headings tangent to common circular motion.
- Point turn: v_x=v_y=0, but only if steering limits and wiring allow tangential wheel alignment.
- Stop/reorient: traction inhibited while large steering transients are executed.

The photographed system does not justify unlimited wheel yaw, so do not promise unrestricted holonomic/zero-radius motion merely because a 4WIS paper does. M05 is explicitly about unlimited steering and should be framed as a contrasting control frontier.

## Torque and terrain screening (independent Newtonian derivation)

On a slope alpha with mass m, forward acceleration a, rolling-resistance coefficient C_rr and external longitudinal force F_ext,

F_req = m a + m g sin(alpha) + C_rr m g cos(alpha) + F_ext.

An equal-load first sizing screen for n_d driven wheels is

tau_w,req = r F_req / n_d,
tau_motor,req = tau_w,req / (eta_g G).

Define G as motor-speed/wheel-speed gear reduction; eta_g is gear efficiency. State whether a manufacturer's torque is motor-shaft or gearbox-output torque. Do not divide by gear ratio a second time for a geared motor already specified at its output. Stall torque is not a continuous rating.

The necessary static traction limit on a uniform surface is

F_req <= mu m g cos(alpha).

Per-wheel limits are |F_i| <= mu_i N_i and tau_w,i <= r_i mu_i N_i. Unequal normal loads, wheel lift, soft soil, tread deformation and transient steering invalidate uniform allocation. A simple friction inequality screens infeasible scenarios; it does not establish traversability. M06–M08 motivate terrain/contact estimation and richer models.

Useful honest analytical graphs: torque versus slope for explicit mass and C_rr scenarios; feasible region over slope and friction coefficient; wheel speed/steering angles versus turn radius; energy per distance versus assumed rolling resistance. Every graph must state its assumed inputs and label calculated outputs. Do not call these real-world graphs.

## Manipulator stability (independent derivation)

Static total center of mass:

p_COM(q,m_p) = [sum_j m_j p_j(q) + m_p p_p(q)]/[sum_j m_j + m_p].

For coplanar contacts under gravity, project COM along the gravity direction onto the support plane and compute signed distance to each support-polygon edge. Require all distances positive and impose a design margin. An edge-based tipping moment is more informative when the arm is loaded:

M_margin,e = sum_j m_j g d_j,e - m_p g d_p,e - M_external,e

with signed perpendicular lever arms and a clearly declared convention. Use actual three-dimensional moment vectors when the terrain is sloped or external forces are present. For a crude centered rigid-body lateral tip screen on a cross-slope beta,

tan(beta_tip) = (track_width/2 - |y_COM|)/h_COM.

This is a static bound, not a safe operational slope. Tire compliance, suspension motion, acceleration, obstacles and payload movement can reduce margin. M04 supports force-angle approaches when external/inertial effects matter.

Arm joint torque should be computed from tau = J(q)^T F plus link gravity terms. A planar two-link teaching approximation can be written explicitly, but a claimed Nemesis workspace or torque envelope requires measured link lengths, joint axes, travel limits and masses.

Photo-based visual upgrades that preserve the user's structure: bolted joint covers, bearing housings, cable guides, strain relief, hard-stop indicators, limit switch brackets, guarded lift rails and stowed sample containers. Added hardware in a render is a proposed modification, not proof of installation.

## Navigation and computing architecture

M09 motivates acceleration/braking-aware local avoidance; M10 is a simple reactive baseline. A 4WIS planner must incorporate steering-rate feasibility, chassis footprint and manipulator swept volume. A visually clear 3D scene should show a route ribbon and blocked region as conceptual overlays, with caption "mission visualization; not a logged autonomous trial."

M11 and M12 are candidate SLAM stacks for a companion computer, with calibrated camera/IMU or lidar. Arduino Mega and ESP32 can remain low-level actuation, sampling and communication layers; this is not evidence that the full SLAM stack runs on them. M13 and M14 can motivate sampling-based manipulator planning but do not certify executable motion or collision safety.

A simple stopping-distance design screen is d_stop = v t_latency + v^2/(2 a_brake) + d_margin, assuming constant available braking deceleration. Test braking on actual surfaces, payloads and battery states. Communication delay should enter the bound. A lost link should trigger a defined controlled stop with arm interlocks; an emergency stop circuit should remain distinct from the wireless/software stop.

## Comparative discussion

Karo (M17): tracked flipper rover with an integrated arm and a structured performance program. Use it to explain why mobility, reach, sensing, serviceability and test protocols must be evaluated together. It is not a like-for-like wheel-performance benchmark. The article's arm torque paragraph has apparent numerical/notation inconsistencies; independently derive and check units rather than transfer calculations.

ResQbot 2.0 (M18): a dedicated casualty extraction architecture. It illustrates why "disaster assistance" for Nemesis should mean remote inspection and situational awareness within verified limits, not transporting patients. Its reported procedure validation is simulation. The downloaded PDF contains a physical assembled-platform photograph; a photo does not change the validation scope.

Telescopic omni-wheel robot (M19): a useful comparable low-cost integration photo and documented design-to-prototype path. Its active leg and roller-wheel mechanisms are architecturally different; do not apply its omni-wheel velocity matrix to conventional Nemesis tires.

## Required validation plan

Use M15–M16 to motivate repeatable trials, with no claim of NIST/ASTM compliance before protocols are actually applied.

1. Weigh complete rover and payload; measure wheelbase/track, wheel radius, steering limits, link geometry and COM variation.
2. Calibrate steer zero, encoder scales and sensor-to-body transforms.
3. Log repeated straight, crab and coordinated-turn trials on documented surfaces; evaluate trajectory RMSE, maximum error and steering mismatch.
4. Characterize speed, current, voltage, motor temperature, slope performance and stopping distance over payload and battery states.
5. Measure tip margin/arm reach conservatively using tethered bench procedures before dynamic loaded operations.
6. Evaluate obstacle avoidance with static and moving obstacles, localization degradation, sensor dropout and communications loss.
7. Report repetitions, operating conditions, raw traces, confidence intervals and unsuccessful trials; retain safety-stop events.
8. Compare to a clearly defined baseline on the same route, payload and sensor setup. Do not rank published robots using heterogeneous reported metrics.

## Figure reuse status

Two usable original photograph panels were extracted unmodified from publisher PDFs. See figure_reuse_ledger.json for exact title/DOI/license/caption/paths. Credit each reused panel locally in its caption and link CC BY 4.0; "courtesy" alone is insufficient. The third candidate (Karo Fig. 9) is licensed but the media CDN returned a challenge page, so its local HTML file must never be embedded as an image.

Recommended manuscript captions:
- "Comparator platform with telescopic legs and omni wheels. Reproduced from Mohamed et al. (2025), Fig. 1(c), CC BY 4.0. Original panel isolated from the composite figure; no image content altered. This is not A3P5 Nemesis."
- "ResQbot 2.0 in compact configuration. Reproduced from Saputra et al. (2021), Fig. 10(a), CC BY 4.0. Original panel isolated from the composite figure; no image content altered. Shown as a contrasting dedicated rescue architecture."

