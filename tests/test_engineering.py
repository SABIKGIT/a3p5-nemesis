"""Independent SI-unit recomputation of archived scenarios; no hardware trials."""
import math
from common import ANALYSIS, NumericCase, read_json, rows

G, L, W, RADIUS = 9.80665, 0.908, 0.930, 0.140
MASS, CRR, EFFICIENCY = 24.0, 0.06, 0.8
ENERGY_WH = 11.1 * 10.0 * 0.85 * 0.90


class EngineeringArchiveTests(NumericCase):
    def table(self, name, expected_rows):
        data = rows(ANALYSIS / "tables" / (name + ".csv"))
        self.assertEqual(len(data), expected_rows, name)
        return data

    def test_declared_inputs_and_unit_anchors(self):
        result = read_json(ANALYSIS / "analysis_results.json")
        self.assertEqual(result["parameters"]["estimated_geometry_m"],
                         {"wheelbase_L": L, "track_W": W, "wheel_radius_r": RADIUS})
        self.assertIn("no rover measurements", result["parameters"]["evidence_status"])
        summary = result["summary"]
        self.assertClose(summary["usable_energy_Wh"], 84.915)
        self.assertClose(summary["straight_wheel_rpm_at_0p25mps"], 60 * .25 / (2 * math.pi * RADIUS))
        self.assertClose(summary["grade_summary"][0]["each_wheel_torque_Nm"], MASS * G * CRR * RADIUS / 4)
        self.assertClose(summary["stopping_summary"][-1]["clearance_m_latency0p3_decel0p5_margin0p15"], 1.45)
        self.assertClose(summary["pH_summary"]["ADC_LSB_mV"], 5000 / 1024)

    def test_wheel_commands_reconstruct_one_body_twist(self):
        position = {"FL": (L/2, W/2), "FR": (L/2, -W/2),
                    "RL": (-L/2, W/2), "RR": (-L/2, -W/2)}
        for row in self.table("kinematics_sweep", 540):
            x, y = position[row["wheel"]]
            vx = float(row["body_speed_m_s"])
            yaw = vx / float(row["turn_radius_m"])
            heading = math.radians(float(row["steering_deg"]))
            speed = float(row["rolling_speed_m_s"])
            # Invert the exported steering commands and check both velocity components.
            self.assertClose(speed * math.cos(heading), vx - yaw * y)
            self.assertClose(speed * math.sin(heading), yaw * x)
            self.assertClose(float(row["wheel_rpm"]) * 2 * math.pi * RADIUS / 60, speed)
            self.assertLessEqual(abs(float(row["steering_deg"])), 90)

    def test_grade_force_torque_and_normal_load(self):
        for row in self.table("grade_torque_traction", 423):
            mass, angle = float(row["mass_kg"]), math.radians(float(row["grade_deg"]))
            normal = mass * G * math.cos(angle)
            force = mass * G * math.sin(angle) + CRR * normal
            self.assertClose(row["steady_force_N"], force)
            self.assertClose(float(row["wheel_output_torque_Nm"]) * 4 / RADIUS, force)
            self.assertClose(float(row["minimum_uniform_mu"]) * normal, force)
            self.assertClose(float(row["wheel_output_torque_Nm_at_accel_0p1"]) * 4 / RADIUS, force + .1 * mass)

    def test_mass_balance_and_tip_boundary(self):
        for row in self.table("static_stability", 3321):
            payload = float(row["payload_kg"])
            cx, cz = float(row["COM_x_m"]), float(row["COM_z_m"])
            self.assertClose(cx * (MASS + payload), .8 * payload)
            self.assertClose(cz * (MASS + payload), MASS * .58 + payload)
            angle = math.radians(float(row["downhill_front_slope_deg"]))
            self.assertClose(row["front_edge_margin_m"], L/2 - cx - cz * math.tan(angle))
            self.assertClose(cz * math.tan(math.radians(float(row["front_static_tip_deg"]))), L/2 - cx)
            self.assertClose(cz * math.tan(math.radians(float(row["lateral_static_tip_deg"]))), W/2)

    def test_energy_balance_and_distance_units(self):
        for row in self.table("energy_endurance", 1008):
            angle = math.radians(float(row["grade_deg"]))
            speed, aux = float(row["speed_m_s"]), float(row["auxiliary_load_W"])
            force = MASS * G * (math.sin(angle) + CRR * math.cos(angle))
            power = float(row["battery_power_W"])
            self.assertClose((power - aux) * EFFICIENCY, force * speed)
            self.assertClose(row["usable_energy_Wh"], ENERGY_WH)
            self.assertClose(float(row["endurance_h"]) * power, ENERGY_WH)
            self.assertClose(row["ideal_distance_km"], speed * float(row["endurance_h"]) * 3600 / 1000)

    def test_sensor_response_and_spatial_lag(self):
        for row in self.table("sensor_step_response", 723):
            time, tau = float(row["time_after_step_s"]), float(row["assumed_tau_s"])
            self.assertClose(row["normalized_response"], -math.expm1(-time/tau))
            self.assertClose(row["spatial_distance_m_at_0p25mps"], .25 * time)
            self.assertEqual(row["steady_uniform_environment_assumed"], "1")
        for row in self.table("sensor_spatial_lag", 348):
            tau, speed = float(row["assumed_tau_s"]), float(row["speed_m_s"])
            t90, t95 = float(row["minimum_dwell_90pct_s"]), float(row["minimum_dwell_95pct_s"])
            self.assertClose(math.exp(-t90/tau), .10)
            self.assertClose(math.exp(-t95/tau), .05)
            self.assertClose(row["distance_to_90pct_m"], speed * t90)

    def test_stopping_work_energy_balance(self):
        for row in self.table("stopping_clearance", 909):
            speed, acceleration = float(row["speed_m_s"]), float(row["available_deceleration_m_s2"])
            delay, margin = float(row["total_latency_s"]), float(row["geometric_margin_m"])
            braking_distance = float(row["required_clearance_m"]) - speed * delay - margin
            self.assertClose(2 * acceleration * braking_distance, speed ** 2)
            self.assertGreaterEqual(float(row["required_clearance_m"]) + 1e-12, margin)

    def test_nernst_voltage_and_adc_code_count(self):
        for row in self.table("pH_Nernst_ADC", 846):
            slope = math.log(10) * 8.31446261815324 * (float(row["temperature_C"]) + 273.15) / 96485.33212
            bits, reference, gain = int(row["ADC_bits"]), float(row["ADC_reference_V"]), float(row["gain"])
            midpoint = 2.5 if bits == 10 else 1.65
            voltage = midpoint + gain * slope * (7 - float(row["pH"]))
            self.assertClose(row["ideal_electrode_slope_V_per_pH"], slope)
            self.assertClose(row["conditioned_voltage_V"], voltage)
            self.assertClose(float(row["ideal_ADC_code_coordinate"]) * reference / (2 ** bits), voltage)
            self.assertClose(float(row["ADC_step_pH"]) * gain * slope, reference / (2 ** bits))
            self.assertEqual(row["within_ADC_rails"], str(0 <= voltage <= reference))

    def test_parameter_sensitivity_is_one_factor_at_a_time(self):
        def demand(p):
            a = math.radians(10)
            return p["mass_kg"] * G * (math.sin(a) + p["Crr"] * math.cos(a)) * p["speed_m_s"] / p["efficiency"] + p["aux_W"]
        base = {"mass_kg": 24, "speed_m_s": .25, "Crr": .06, "efficiency": .8, "aux_W": 20}
        for row in self.table("local_sensitivity", 15):
            changed = dict(base)
            changed[row["parameter"]] *= float(row["multiplier"])
            power = demand(changed)
            self.assertClose(row["value"], changed[row["parameter"]])
            self.assertClose(row["battery_power_W"], power)
            self.assertClose(row["endurance_h"], ENERGY_WH / power)
            self.assertClose(row["endurance_change_pct"], 100 * (demand(base)/power - 1))
