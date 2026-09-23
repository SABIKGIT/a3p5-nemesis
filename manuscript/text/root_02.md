## 5. Mobility, traction and steering coordination
### 5.1. Compatible wheel velocities
Four independently steered wheels can support several motion modes, but their commands must be mutually compatible. Under a locally planar, rigid-body, no-slip approximation, the velocity at each wheel follows from the body translation and yaw rate. Let wheel i lie at (xᵢ, yᵢ), with body velocity components vₓ and vᵧ and yaw rate ω. The wheel velocity components and corresponding steering angle are given below. The formulation is consistent with the wheel-compatibility treatment of Alexander and Maddocks (1989) and the coordinated architecture discussed by Lee and Li (2015).

!EQ[u_i=v_x-\omega y_i,\qquad w_i=v_y+\omega x_i]
!EQ[\delta_i=\operatorname{atan2}(w_i,u_i),\qquad \Omega_i=\frac{\sqrt{u_i^2+w_i^2}}{r_i}]

Here δᵢ is wheel heading, Ωᵢ is angular wheel speed and rᵢ is loaded rolling radius. The equivalent command (δᵢ + π, −Ωᵢ) may reduce steering travel, but only if the measured mechanism and cable routing permit it. At near-zero wheel velocity the heading is numerically indeterminate; the controller should retain a previous feasible angle or execute an explicit reorientation state. Small measurement noise must not cause an arbitrary steering reversal.

!FIG[diagrams/canva_03.png|Canva-created four-wheel motion-allocation diagram. A common body-motion command is converted to individual wheel targets, constrained by measured steering travel and actuator limits. Closed-loop angle and speed sensing are proposed implementation requirements.|3.0]

!FIG[analysis/figures/A01_steering_kinematics.png|Calculated wheel coordination for the estimated wheelbase and track. The plotted angle convention permits an equivalent reversed rolling direction. This is ideal geometry and does not establish unrestricted steering, zero-radius motion or measured path accuracy.|3.0]

Straight motion sets lateral velocity and yaw rate to zero. Crab motion uses a common heading with zero yaw rate. A coordinated turn requires every wheel velocity to be tangent to the same instantaneous rigid-body motion. Physical point-turn feasibility depends on verified steering travel, cable clearance, tire contact and actuator torque. Large heading changes should initially occur with traction inhibited or strongly limited, followed by a controlled speed ramp after convergence.

At 0.25 m/s and radius 0.140 m, ideal wheel speed is approximately 17.05 rpm. This is an output-wheel requirement, not a motor-shaft specification. Gear ratio, controller resolution and encoder counts must support observable low-speed motion. A motor with ample stall torque can still be unsuitable if it overheats during slow continuous operation or provides inadequate speed resolution near the operating point.

### 5.2. Feedback, slip and implementation limits
The recommended implementation includes independent steering-angle feedback and wheel encoders, neither established by photographs alone. A speed controller can use proportional-integral action with saturation and anti-windup, while the steering loop tracks an angle reference within hard and software limits. Driver current and motor temperature provide additional fault information. Each wheel channel should report its target, measured state and saturation status so that a high-level controller does not mistake commanded motion for achieved motion.

!FIG[diagrams/canva_04.png|Canva-created drive-feedback architecture. Encoder and body-motion feedback are proposed additions to the reported drivetrain. The wheel–ground interaction remains uncertain, so a tracking residual alone does not establish traction.|3.0]

A useful kinematic diagnostic is the velocity component perpendicular to a wheel heading. Under ideal rolling it should be zero. In practice it can reveal inconsistency between steering, wheel commands and an independently estimated body velocity. It is not a direct slip sensor when body velocity is computed only from the same wheel encoders. Longitudinal and lateral slip require separate interpretation; Burghi et al. (2024) examine adaptive slip compensation for a differential-drive robot through numerical simulation. Their results provide methodological context for controller development; this four-wheel-steering platform requires its own identified model and validation.

!EQ[e_{\perp,i}=-\sin\delta_i\,(v_x-\omega y_i)+\cos\delta_i\,(v_y+\omega x_i)]

The study does not assume a particular suspension law. The photographs show mechanical links and wheel supports, but do not reveal spring stiffness, damping, articulation limits or load equalization. Applying an existing rocker-bogie or omni-wheel model without identifying the actual mechanism would introduce false precision. First measure wheel-contact locations and their motion relative to the chassis during controlled articulation, then derive constraints that match the assembled vehicle.

### 5.3. Grade force and torque demand
A first longitudinal sizing model balances acceleration, gravity and rolling resistance. For mass m, slope α, forward acceleration a and rolling-resistance coefficient Cᵣᵣ, required force is written below. An optional external force represents a tether or contact load. The model assumes continuing wheel contact and omits sinkage, bulldozing losses and steering scrub. These limitations matter on loose terrain, where the contact mechanics discussed by Iagnemma and Dubowsky (2004) require richer treatment.

!EQ[F_{\mathrm{req}}=ma+mg\sin\alpha+C_{rr}mg\cos\alpha+F_{\mathrm{ext}}]
!EQ[\tau_{w,\mathrm{req}}=\frac{rF_{\mathrm{req}}}{4},\qquad F_{\mathrm{req}}\leq\mu mg\cos\alpha]

The torque expression assumes equal force sharing by four driven wheels and gives gearbox-output torque at the wheel. If a datasheet already specifies geared output torque, do not apply the gear ratio again. For a motor-shaft comparison, divide output torque by gear ratio and gear efficiency once. The traction inequality is a necessary screen under uniform friction and loading; individual limits are |Fᵢ| ≤ μᵢNᵢ. A lightly loaded wheel can saturate before the total vehicle inequality is reached.

!FIG[analysis/figures/A02_grade_traction_torque.png|Analytical grade demand for declared mass and rolling-resistance scenarios. Torque is required gearbox-output torque per wheel under equal sharing. The friction boundary is a simplified necessary condition, not evidence of loose-soil mobility or safe climbing.|3.0]

For the declared 24 kg, Cᵣᵣ = 0.06, zero-acceleration case, a 20° grade requires 93.77 N total force and 3.282 N m per wheel at a 0.140 m radius. The corresponding uniform friction coefficient is at least 0.424. On level ground, the same model requires 0.494 N m per wheel. This difference shows why a successful indoor drive is insufficient evidence for a sloped outdoor mission. Continuous torque, motor heating, battery sag and actual friction must be measured before selecting an operating limit.

## 6. Manipulation, sampling and stability
### 6.1. Arm function and integration
The manipulator retains its original deck location and folded configuration. Its visible structure includes a yaw base, shoulder and elbow assemblies, laterally mounted motors, a wrist enclosure and a two-finger gripper. The model exposes named pivots for editing, but it is not a calibrated kinematic chain. Forward kinematics require measured joint axes, link transforms, zero positions and limits. Payload capacity additionally requires link masses, gearbox ratings, bearing loads and mounting stiffness.

For a measured mechanism, tool pose can be expressed as a product of joint transforms. The required tool wrench W_req is the three-component force and three-component moment that the manipulator must exert, expressed in the same frame as the 6 × n geometric Jacobian. It maps to actuator torque through the Jacobian transpose. An environment-applied wrench uses the opposite sign in the actuator compensation equation. Link gravity, acceleration and friction must be added. A gripper that holds an object while stationary does not establish safe reach or manipulation during driving. The proposed sampling mode inhibits chassis motion before the arm approaches a sample and releases that inhibition only after the arm and probes reach a verified travel configuration.

!EQ[{}^{B}T_E(\mathbf{q})=\prod_{j=1}^{n}T_j(q_j),\qquad \boldsymbol{\tau}=J(\mathbf{q})^T\mathbf{W}_{\mathrm{req}}+\boldsymbol{\tau}_g+\boldsymbol{\tau}_{\mathrm{dyn}}]

!FIG[diagrams/canva_09.png|Canva-created manipulation workflow. Reach, payload, collision and cable-travel checks precede motion. Joint/current feedback and grip confirmation are proposed controls, not evidence of a validated installed manipulator controller.|3.0]

!FIG[blender/M03_mission.png|Blender illustration of lightweight sample handling. A small vial is positioned between the gripper tips in the preserved arm pose, with a nearby preparation bench. The image illustrates a task arrangement; no pickup trial, payload capacity or automated success rate is claimed.|3.5]

### 6.2. Payload-dependent support margin
A mobile manipulator must be evaluated as one mass distribution. Centre of mass depends on arm pose, payload location and every substantial component. The simplified calculation holds the unladen base centre of mass fixed and adds a payload at a declared forward location. This isolates one sensitivity but omits the movement of the arm links themselves. Force-angle and edge-moment approaches, such as Papadopoulos and Rey (1996), become necessary when external forces, inertial loads or noncoplanar contacts matter.

!EQ[\mathbf{p}_{CG}=\frac{m_b\mathbf{p}_b+m_p\mathbf{p}_p}{m_b+m_p}]
!EQ[M_{\mathrm{front}}=\frac{L}{2}-x_{CG}-h_{CG}\tan\beta,\qquad \beta_{\mathrm{tip}}=\tan^{-1}\!\left(\frac{L/2-x_{CG}}{h_{CG}}\right)]

M_front is the projected distance to the front support edge on a slope descending toward the front. Zero defines an ideal geometric tipping boundary, not an allowable operating slope. Compliance, wheel lift, acceleration, arm contact, uneven ground and centre-of-mass uncertainty reduce the useful margin. Even a positive static value can be inadequate when a wheel unloads or arm motion produces a transient reaction moment.

!FIG[analysis/figures/A03_static_stability.png|Calculated support-margin sensitivity for an assumed 24 kg base with centre-of-mass height 0.58 m and a payload at (0.8, 0, 1.0) m. The curves are ideal static geometric bounds and must not be used as approved operating slopes.|3.0]

The assumed unloaded front-tipping bound is 38.05°. Adding 1 kg at the stated position reduces it to 35.26°, while 2 kg reduces it to 32.66°. At a 20° downhill slope, corresponding front margins are approximately 0.243, 0.205 and 0.170 m. These values show the direction and magnitude of model sensitivity. They do not justify a 2 kg payload because arm torque, gripper retention and actual mass distribution remain unmeasured.

A conservative implementation should enforce a pose-dependent envelope after physical identification. It can reject a requested arm pose when the estimated support margin is insufficient, accounting for uncertainty rather than a single nominal value. Low-confidence terrain contact or an unknown payload should trigger a more restricted mode. Cable routing must be checked within the same envelope: a reachable pose is unusable if it pulls a connector or traps a harness against a wheel support.

### 6.3. Water access and sample logistics
The side rack provides organized sample handling, but access to water is a separate mechanical problem. In the mission illustration, a staged vessel sits beneath the existing pH probe so that the electrode enters the liquid while the upper housing remains clear. This shows spatial compatibility in one configuration. It does not demonstrate automatic deployment into a river, a sealed wet enclosure or a mechanism for raising and lowering the probe.

!FIG[blender/M02_mission.png|Blender water-assessment concept with a staged vessel beneath the original side-mounted pH probe. The chassis remains on dry support. Vessel placement and probe immersion are illustrative; autonomous deployment and water-ingress protection are unverified.|3.5]

!FIG[blender/M02_probe_detail.png|Blender detail of the pH electrode entering a vessel. The liquid covers the electrode tip while the upper housing stays above it. This is a sampling arrangement, not a measured pH result or validated waterproof assembly.|3.1]

Sampling records should connect a physical container to time, position estimate, operator or mission ID, probe calibration and acquisition state. Rinsing, stabilization and contamination control affect interpretation and belong in the workflow. Turbidity can be sensitive to bubbles, container geometry and residue. Samples requiring laboratory confirmation should retain their identity through collection, transport and analysis; the rover reading can then be compared with the laboratory result rather than used as an unsupported replacement.

@@SENSING@@
