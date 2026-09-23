"""A3P5 Nemesis: reproducible analytical design study.
All input values are estimates or explicit scenarios, not physical measurements.
Run with Python 3.12 and the pinned requirements from the repository root.
"""
from pathlib import Path
import sys, json, csv, math, hashlib
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "python_packages"))
import numpy as np
OUT = HERE
FIG = OUT / "figures"
TAB = OUT / "tables"
FIG.mkdir(parents=True, exist_ok=True)
TAB.mkdir(parents=True, exist_ok=True)

P = {
 "evidence_status": "Analytical scenarios only; no rover measurements or trials supplied.",
 "estimated_geometry_m": {"wheelbase_L": 0.908, "track_W": 0.930, "wheel_radius_r": 0.140},
 "assumptions": {
  "base_mass_kg":24.0, "mass_sweep_kg":[15.0,24.0,35.0],
  "base_COM_m":[0.0,0.0,0.58], "payload_position_m":[0.8,0.0,1.0],
  "payload_sweep_kg":[0.0,2.0],
  "gravity_m_s2":9.80665, "rolling_resistance_coefficient":0.06,
  "battery_to_ground_efficiency":0.8,
  "speed_reference_m_s":0.25,
  "battery_nominal_V":11.1, "battery_capacity_Ah":10.0,
  "depth_of_discharge":0.85, "usable_energy_derating":0.90,
  "electronics_power_reference_W":20.0, "electronics_power_sweep_W":[10.0,20.0,40.0],
  "gas_first_order_tau_s":[5.0,15.0,30.0],
  "stop_latency_reference_s":0.30, "stop_deceleration_reference_m_s2":0.50,
  "stop_margin_m":0.15,
  "pH_conditioner_gain":3.0, "pH_midpoint_V":2.5, "ADC_reference_V":5.0,
  "ADC_bits":10, "ADC_max_code":1023, "ADC_code_count":1024, "proposed_ADC_reference_V":3.3,
  "proposed_ADC_bits":12, "proposed_ADC_code_count":4096, "proposed_midpoint_V":1.65, "pH_reference_temperature_C":25.0,
  "ADC_resolution_convention":"Ideal converter LSB = Vref / 2**N; maximum output code is 2**N - 1."
 },
 "coordinate_convention": "Body x forward, y left, z upward. Positive slope in stability analysis tilts the support plane downhill toward +x.",
 "torque_convention": "tau_w is total required longitudinal tire force times wheel radius / four driven wheels; it is gearbox-output wheel torque. Motor-shaft gearing is not specified.",
 "energy_convention": "Battery usable energy E=V*Ah*DoD*derating; separate battery-to-ground efficiency acts only on the traction power term, so it is not applied again to electronics."
}
L,W,r = (P["estimated_geometry_m"][x] for x in ("wheelbase_L","track_W","wheel_radius_r"))
A=P["assumptions"]; g=A["gravity_m_s2"]; m0=A["base_mass_kg"]; crr=A["rolling_resistance_coefficient"]
eta=A["battery_to_ground_efficiency"]; speed0=A["speed_reference_m_s"]
Euse=A["battery_nominal_V"]*A["battery_capacity_Ah"]*A["depth_of_discharge"]*A["usable_energy_derating"]
wheel_names=["FL","FR","RL","RR"]
wheel_xy=np.array([[L/2,W/2],[L/2,-W/2],[-L/2,W/2],[-L/2,-W/2]])

def wheel_commands(vx,vy,yaw):
    u=vx-yaw*wheel_xy[:,1]
    v=vy+yaw*wheel_xy[:,0]
    heading=np.arctan2(v,u)
    speed=np.hypot(u,v)
    # Choose equivalent heading inside [-90,90] degrees and signed rolling speed.
    reverse=np.abs(heading)>np.pi/2
    heading=np.where(heading>np.pi/2,heading-np.pi,heading)
    heading=np.where(heading<-np.pi/2,heading+np.pi,heading)
    speed=np.where(reverse,-speed,speed)
    return np.degrees(heading),speed,u,v

def tractive_force(mass,grade_deg,accel=0.0):
    a=np.radians(grade_deg)
    return mass*(accel+g*(np.sin(a)+crr*np.cos(a)))

def wheel_torque(mass,grade_deg,accel=0.0):
    return tractive_force(mass,grade_deg,accel)*r/4

def required_mu(grade_deg,accel=0.0):
    a=np.radians(grade_deg)
    return np.tan(a)+crr+accel/(g*np.cos(a))

def com(payload):
    return (m0*np.array(A["base_COM_m"])+np.asarray(payload)[...,None]*np.array(A["payload_position_m"]))/(m0+np.asarray(payload)[...,None])

def tip_angles(payload):
    cg=com(payload)
    return np.degrees(np.arctan((L/2-cg[...,0])/cg[...,2])), np.degrees(np.arctan((W/2-np.abs(cg[...,1]))/cg[...,2]))

def total_power(speed,grade_deg,mass=m0,aux=20.0):
    return tractive_force(mass,grade_deg)*speed/eta+aux

def stop_distance(speed,latency=0.3,decel=0.5,margin=0.15):
    return speed*latency+speed**2/(2*decel)+margin

Rgas=8.31446261815324; Fconst=96485.33212
def nernst_slope(Tc):
    return np.log(10.0)*Rgas*(np.asarray(Tc)+273.15)/Fconst

def csv_write(name,rows):
    path=TAB/(name+".csv")
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    return str(path.relative_to(OUT))

tables={}
radii=np.linspace(.65,4.0,135)
kin=[]
for radius in radii:
    headings,vs,_,_=wheel_commands(speed0,0,speed0/radius)
    for i in range(4):
        kin.append({"turn_radius_m":float(radius),"body_speed_m_s":speed0,"wheel":wheel_names[i],
                    "steering_deg":float(headings[i]),"rolling_speed_m_s":float(vs[i]),"wheel_rpm":float(vs[i]/r*60/(2*np.pi))})
tables["kinematics"]=csv_write("kinematics_sweep",kin)
drive=[]
for mass in A["mass_sweep_kg"]:
 for grade in np.linspace(0,35,141):
    drive.append({"mass_kg":mass,"grade_deg":float(grade),"steady_force_N":float(tractive_force(mass,grade)),
       "wheel_output_torque_Nm":float(wheel_torque(mass,grade)),
       "minimum_uniform_mu":float(required_mu(grade)),
       "wheel_output_torque_Nm_at_accel_0p1":float(wheel_torque(mass,grade,.1))})
tables["drive"]=csv_write("grade_torque_traction",drive)
stability=[]
for payload in np.linspace(0,2,41):
 cg=com(payload); front,side=tip_angles(payload)
 for slope in np.linspace(0,40,81):
    margin=L/2-cg[0]-cg[2]*np.tan(np.radians(slope))
    stability.append({"payload_kg":float(payload),"downhill_front_slope_deg":float(slope),
      "COM_x_m":float(cg[0]),"COM_z_m":float(cg[2]),"front_edge_margin_m":float(margin),
      "front_static_tip_deg":float(front),"lateral_static_tip_deg":float(side)})
tables["stability"]=csv_write("static_stability",stability)
energy=[]
for aux in A["electronics_power_sweep_W"]:
 for grade in [0.,10.,20.]:
  for v in np.linspace(.05,.6,112):
    power=total_power(v,grade,aux=aux); end=Euse/power
    energy.append({"auxiliary_load_W":aux,"grade_deg":grade,"speed_m_s":float(v),"battery_power_W":float(power),
      "usable_energy_Wh":Euse,"endurance_h":float(end),"ideal_distance_km":float(v*end*3.6)})
tables["energy"]=csv_write("energy_endurance",energy)
gas=[]
for tau in A["gas_first_order_tau_s"]:
 for t in np.linspace(0,120,241):
    gas.append({"assumed_tau_s":tau,"time_after_step_s":float(t),"normalized_response":float(1-np.exp(-t/tau)),
       "spatial_distance_m_at_0p25mps":float(speed0*t),"steady_uniform_environment_assumed":1})
tables["gas"]=csv_write("sensor_step_response",gas)
gas_spatial=[]
for tau in A["gas_first_order_tau_s"]:
 for v in np.linspace(.025,.6,116):
    gas_spatial.append({"assumed_tau_s":tau,"speed_m_s":float(v),"distance_to_90pct_m":float(v*tau*np.log(10)),
      "minimum_dwell_90pct_s":float(tau*np.log(10)),"minimum_dwell_95pct_s":float(tau*np.log(20))})
tables["gas_spatial"]=csv_write("sensor_spatial_lag",gas_spatial)
stops=[]
for latency in [.1,.3,.6]:
 for decel in [.3,.5,.8]:
  for v in np.linspace(0,1,101):
    stops.append({"speed_m_s":float(v),"total_latency_s":latency,"available_deceleration_m_s2":decel,
       "geometric_margin_m":.15,"required_clearance_m":float(stop_distance(v,latency,decel))})
tables["stopping"]=csv_write("stopping_clearance",stops)
phrows=[]
for design,vref,bits,midpoint in [("Mega_5V_10bit_baseline",5.,10,2.5),("proposed_3p3V_12bit",3.3,12,1.65)]:
 for temp in [5.,25.,45.]:
  S=float(nernst_slope(temp))
  for ph in np.linspace(0,14,141):
    voltage=midpoint+3*S*(7-ph)
    # Continuous ideal code coordinate; integer quantization and clipping are not simulated.
    code=voltage/vref*(2**bits)
    phrows.append({"acquisition_design":design,"ADC_reference_V":vref,"ADC_bits":bits,
        "temperature_C":temp,"pH":float(ph),"ideal_electrode_slope_V_per_pH":S,
        "gain":3,"conditioned_voltage_V":float(voltage),"ideal_ADC_code_coordinate":float(code),
        "ADC_step_pH":float(vref/((2**bits)*3*S)),"within_ADC_rails":bool(0<=voltage<=vref)})
tables["pH"]=csv_write("pH_Nernst_ADC",phrows)

baseline={"mass_kg":24,"grade_deg":10,"speed_m_s":.25,"Crr":.06,"efficiency":.8,"aux_W":20}
basepower=float(total_power(.25,10))
sensitivity=[]
for key in ["mass_kg","speed_m_s","Crr","efficiency","aux_W"]:
 for mult in [.8,1,1.2]:
    params=dict(baseline); params[key]*=mult
    a=np.radians(params["grade_deg"])
    force=params["mass_kg"]*g*(np.sin(a)+params["Crr"]*np.cos(a))
    power=force*params["speed_m_s"]/params["efficiency"]+params["aux_W"]
    sensitivity.append({"parameter":key,"multiplier":mult,"value":params[key],"battery_power_W":power,
        "endurance_h":Euse/power,"endurance_change_pct":100*((basepower/power)-1)})
tables["sensitivity"]=csv_write("local_sensitivity",sensitivity)

summary={
 "usable_energy_Wh":Euse,
 "straight_wheel_rpm_at_0p25mps":float(speed0/r*60/(2*np.pi)),
 "coordinated_turn_R1m_at_0p25mps":{},
 "grade_summary":[{"grade_deg":d,"force_N":float(tractive_force(m0,d)),
   "each_wheel_torque_Nm":float(wheel_torque(m0,d)),"minimum_mu":float(required_mu(d)),
   "power_W_at_0p25mps_aux20W":float(total_power(speed0,d)),
   "endurance_h_at_0p25mps_aux20W":float(Euse/total_power(speed0,d))} for d in [0,10,20,30]],
 "stability_summary":[{"payload_kg":p,"COM_x_m":float(com(p)[0]),"COM_z_m":float(com(p)[2]),
   "front_tip_deg":float(tip_angles(p)[0]),"lateral_tip_deg":float(tip_angles(p)[1]),
   "front_margin_m_at_20deg":float(L/2-com(p)[0]-com(p)[2]*np.tan(np.radians(20)))} for p in [0,1,2]],
 "gas_summary":[{"tau_s":t,"t90_s":float(t*np.log(10)),"t95_s":float(t*np.log(20)),
   "distance90_m_at_0p25mps":float(.25*t*np.log(10))} for t in [5,15,30]],
 "stopping_summary":[{"speed_m_s":v,"clearance_m_latency0p3_decel0p5_margin0p15":float(stop_distance(v))}
    for v in [.25,.4,.6,1.0]],
 "pH_summary":{"slope_mV_per_pH_at25C":float(nernst_slope(25)*1000),
  "ADC_LSB_mV":5000/1024,"gain":3,
  "ADC_step_pH_at25C":float(5.0/(1024*3*nernst_slope(25))),
  "conditioned_voltage_at_pH0_V":float(2.5+3*nernst_slope(25)*7),
  "conditioned_voltage_at_pH14_V":float(2.5-3*nernst_slope(25)*7),
  "maximum_gain_for_full_pH0to14_ADC_span_at25C":float(5.0/(14*nernst_slope(25))),
  "proposed_3p3V_12bit_ADC_step_pH_at25C":float(3.3/(4096*3*nernst_slope(25)))},
 "endurance_sensitivity_reference_h":Euse/basepower
}
h,vs,_,_=wheel_commands(.25,0,.25)
for i in range(4):
 summary["coordinated_turn_R1m_at_0p25mps"][wheel_names[i]]={"steer_deg":float(h[i]),"speed_m_s":float(vs[i])}
# Sanity checks tied to physics, not claimed experimental validation.
assert np.allclose(wheel_commands(.25,0,0)[1],.25)
assert np.allclose(wheel_commands(.25,0,0)[0],0)
assert np.isclose(wheel_torque(24,0),24*g*.06*.14/4)
assert float(com(0)[2])==.58
assert all(row["within_ADC_rails"] for row in phrows)
assert np.isclose(stop_distance(0),.15)
assert np.isclose(Euse,84.915)
(OUT/"analysis_results.json").write_text(json.dumps({"parameters":P,"summary":summary,"tables":tables},indent=2),encoding="utf-8")

# Plotting is intentionally separate from the equations and exported numeric tables.
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
from matplotlib import ticker
plt.rcParams.update({
 "font.family":"DejaVu Sans","font.size":8.5,"axes.titlesize":9.5,"axes.labelsize":8.5,
 "xtick.labelsize":7.5,"ytick.labelsize":7.5,"legend.fontsize":7.3,
 "figure.dpi":150,"savefig.dpi":360,"svg.fonttype":"none",
 "axes.spines.top":False,"axes.spines.right":False,"axes.edgecolor":"#86959b",
 "axes.labelcolor":"#23333b","text.color":"#15262f","xtick.color":"#43545c","ytick.color":"#43545c",
 "axes.grid":True,"grid.color":"#dce3e6","grid.linewidth":.55,"grid.alpha":.75,
 "lines.linewidth":1.8,"figure.facecolor":"white","axes.facecolor":"white",
 "mathtext.fontset":"dejavusans","legend.frameon":False
})
colors=["#087d94","#d37d24","#655ea8","#2f8465"]
manifest=[]
def make_fig():
    fig,axes=plt.subplots(1,2,figsize=(7.15,3.42),layout="constrained")
    return fig,axes
def save(fig,name,title,subtitle):
    fig.suptitle(title,fontsize=11.5,fontweight="bold",x=.02,ha="left")
    fig.supxlabel(subtitle,fontsize=7,color="#586b75")
    for ext in ["png","svg"]:
        fig.savefig(FIG/(name+"."+ext),bbox_inches="tight",pad_inches=.06)
    manifest.append({"id":name,"title":title,"png":str((FIG/(name+".png")).relative_to(OUT)),
                     "svg":str((FIG/(name+".svg")).relative_to(OUT)),"evidence":"Analytical scenario; not measured data."})
    plt.close(fig)
def panel(ax,letter,title):
    ax.set_title(f"({letter}) {title}",loc="left",pad=8,fontweight="bold")

fig,ax=make_fig()
panel(ax[0],"a","Common-body-twist wheel alignment")
ax[0].set_aspect("equal")
# Four compact plan views. These arrows are velocity vectors, not animation data.
for label,cx,cy,vx,vy,om in [("Straight",-.85,.73,.25,0,0),("Crab",.85,.73,.177,.177,0),
                              ("Coordinated",-.85,-.73,.25,0,.25),("Point turn",.85,-.73,0,0,.35)]:
    scale=.69
    ax[0].add_patch(Rectangle((cx-L*scale/2,cy-W*scale/2),L*scale,W*scale,
                           facecolor="#edf2f4",edgecolor="#9babb3",linewidth=.8))
    ang,sp,uu,vv=wheel_commands(vx,vy,om)
    for i,(xx,yy) in enumerate(wheel_xy):
        x=cx+xx*scale; y=cy+yy*scale
        th=np.radians(ang[i]); dl=.11
        ax[0].plot([x-dl*np.cos(th),x+dl*np.cos(th)],[y-dl*np.sin(th),y+dl*np.sin(th)],color=colors[0],lw=3.5)
        ax[0].arrow(x,y,uu[i]*.7,vv[i]*.7,head_width=.045,head_length=.055,color=colors[1],length_includes_head=True,lw=.7)
    ax[0].text(cx,cy-.54,label,ha="center",fontsize=7.6)
ax[0].set_xlim(-1.52,1.62); ax[0].set_ylim(-1.5,1.38)
ax[0].set_xticks([]);ax[0].set_yticks([]);ax[0].grid(False)
ax[0].text(-1.44,1.25,"Body +x right; +y up",fontsize=7,color="#657883")
panel(ax[1],"b","Steering during a steady left turn")
heads=np.array([wheel_commands(.25,0,.25/R)[0] for R in radii])
for i in range(4):
 ax[1].plot(radii,heads[:,i],label=wheel_names[i],color=colors[i],ls="-" if i<2 else "--")
ax[1].axhline(0,color="#758890",lw=.6)
ax[1].set_xlabel("Body-center turn radius R (m)");ax[1].set_ylabel("Wheel steering angle (deg)")
ax[1].legend(ncol=2,loc="upper right")
save(fig,"A01_steering_kinematics","Four-wheel steering: coordinated geometry",
     "Estimated L = 0.908 m, W = 0.930 m; steady body speed 0.25 m/s. Commands assume ideal rolling.")

fig,ax=make_fig()
grades=np.linspace(0,35,141)
panel(ax[0],"a","Steady-speed wheel torque demand")
for mass,col in zip([15,24,35],colors):
 ax[0].plot(grades,wheel_torque(mass,grades),label=f"m = {mass} kg",color=col)
ax[0].set_xlabel("Grade angle (deg)");ax[0].set_ylabel("Required torque per wheel (N m)");ax[0].legend()
panel(ax[1],"b","Minimum friction coefficient")
ax[1].plot(grades,required_mu(grades),color=colors[0],label="Steady speed")
ax[1].plot(grades,required_mu(grades,.1),color=colors[1],ls="--",label="Acceleration 0.1 m/s²")
for mu in [.3,.5,.7]:
 ax[1].axhline(mu,color="#a8b5ba",lw=.65,ls=":")
 ax[1].text(34.8,mu+.012,f"{mu:.1f}",ha="right",fontsize=7,color="#73858e")
ax[1].set_xlabel("Grade angle (deg)");ax[1].set_ylabel("Required friction coefficient");ax[1].legend(loc="upper left")
save(fig,"A02_grade_traction_torque","Grade demand and traction feasibility",
     "Assumed Crr = 0.06; r = 0.140 m; four equal drive-force shares. No tire/soil or motor testing.")

fig,ax=make_fig()
payloads=np.linspace(0,2,81); fs,ss=tip_angles(payloads)
panel(ax[0],"a","Static geometric tipping bounds")
ax[0].plot(payloads,fs,label="Downhill toward front",color=colors[0])
ax[0].plot(payloads,ss,label="Lateral cross-slope",color=colors[1])
ax[0].set_xlabel("Additional payload mass (kg)");ax[0].set_ylabel("Geometric tipping angle (deg)")
ax[0].legend(loc="lower left");ax[0].set_ylim(31,42)
panel(ax[1],"b","Front support-edge margin")
slopes=np.linspace(0,40,161)
cg=com(payloads)
margins=1000*(L/2-cg[:,0][None,:]-cg[:,2][None,:]*np.tan(np.radians(slopes[:,None])))
im=ax[1].pcolormesh(payloads,slopes,margins,cmap="RdYlBu",shading="auto",vmin=-110,vmax=460,rasterized=True)
ax[1].contour(payloads,slopes,margins,levels=[0],colors="#23333b",linewidths=1.0)
ax[1].set_xlabel("Additional payload mass (kg)");ax[1].set_ylabel("Slope downhill toward front (deg)")
cb=fig.colorbar(im,ax=ax[1],pad=.02);cb.set_label("Margin (mm)");cb.ax.tick_params(labelsize=7)
save(fig,"A03_static_stability","Payload position shifts the support margin",
     "Assumed base m = 24 kg, COM z = 0.58 m; payload at (0.8, 0, 1.0) m. Static bounds, not safe slope limits.")

fig,ax=make_fig()
vel=np.linspace(.05,.6,180)
panel(ax[0],"a","Electrical power required")
for grade,col in zip([0,10,20],colors):
 ax[0].plot(vel,total_power(vel,grade),color=col,label=f"Grade {grade}°")
ax[0].set_xlabel("Steady speed (m/s)");ax[0].set_ylabel("Battery power (W)");ax[0].legend()
panel(ax[1],"b","Endurance versus auxiliary load")
auxes=np.linspace(10,40,151)
for grade,col in zip([0,10,20],colors):
 ax[1].plot(auxes,Euse/total_power(.25,grade,aux=auxes),color=col,label=f"Grade {grade}°")
ax[1].set_xlabel("Auxiliary electronics load (W)");ax[1].set_ylabel("Calculated endurance (h)");ax[1].legend()
save(fig,"A04_energy_endurance","Energy budgeting under declared load scenarios",
     "11.1 V × 10 Ah × 0.85 × 0.90 = 84.915 Wh usable; drive efficiency 0.80; 24 kg. Panel (a): auxiliaries 20 W.")

fig,ax=make_fig()
time=np.linspace(0,120,241)
panel(ax[0],"a","Normalized first-order step response")
for tau,col in zip([5,15,30],colors):
 ax[0].plot(time,1-np.exp(-time/tau),color=col,label=f"τ = {tau} s")
ax[0].axhline(.9,color="#788b94",ls=":",lw=.8);ax[0].text(115,.918,"90%",ha="right",fontsize=7)
ax[0].set_xlabel("Time after concentration step (s)");ax[0].set_ylabel("Normalized sensor response");ax[0].legend(loc="lower right")
panel(ax[1],"b","Spatial distance to 90% response")
vel2=np.linspace(0,.6,121)
for tau,col in zip([5,15,30],colors):
 ax[1].plot(vel2,vel2*tau*np.log(10),color=col,label=f"τ = {tau} s")
ax[1].set_xlabel("Travel speed (m/s)");ax[1].set_ylabel("Distance traveled before t90 (m)");ax[1].legend()
save(fig,"A05_sensor_response_lag","Moving measurements: response lag and dwell time",
     "Illustrative time constants, not measured MQ-sensor response. No gas concentration calibration is implied.")

fig,ax=make_fig()
speeds=np.linspace(0,1,161)
panel(ax[0],"a","Effect of total decision latency")
for t,col in zip([.1,.3,.6],colors):
 ax[0].plot(speeds,stop_distance(speeds,t,.5),label=f"Latency {t:.1f} s",color=col)
ax[0].set_xlabel("Speed before stop (m/s)");ax[0].set_ylabel("Required clear distance (m)");ax[0].legend()
panel(ax[1],"b","Braking uncertainty and speed")
decels=np.linspace(.2,1,100)
dist=stop_distance(speeds[None,:],.3,decels[:,None])
im=ax[1].pcolormesh(speeds,decels,dist,cmap="viridis",shading="auto",rasterized=True)
cs=ax[1].contour(speeds,decels,dist,levels=[.3,.5,1,2],colors="white",linewidths=.65)
ax[1].clabel(cs,inline=True,fontsize=6.5,fmt="%.1f m")
ax[1].set_xlabel("Speed before stop (m/s)");ax[1].set_ylabel("Available deceleration (m/s²)")
cb=fig.colorbar(im,ax=ax[1],pad=.02);cb.set_label("Clearance (m)")
save(fig,"A06_stopping_clearance","Stopping clearance depends on braking and delay",
     "d = v·latency + v²/(2a) + 0.15 m. Panel (a): a = 0.5 m/s²; panel (b): latency 0.3 s. Assumed scenarios.")

fig,ax=make_fig()
ph=np.linspace(0,14,141)
panel(ax[0],"a","Electrode conditioning and temperature")
for T,col in zip([5,25,45],colors):
 ax[0].plot(ph,2.5+3*nernst_slope(T)*(7-ph),label=f"T = {T}°C",color=col)
ax[0].axhline(0,color="#91a0a7",ls=":",lw=.6);ax[0].axhline(5.0,color="#91a0a7",ls=":",lw=.6)
ax[0].set_xlabel("Solution pH");ax[0].set_ylabel("Conditioned output voltage (V)")
ax[0].set_ylim(-.08,5.1);ax[0].legend()
panel(ax[1],"b","ADC resolution is not measurement accuracy")
Ts=np.linspace(0,50,101)
for bits,vref,label,col in [(10,5.0,"Mega: 5 V, 10 bit",colors[0]),(12,3.3,"Proposed: 3.3 V, 12 bit",colors[1])]:
 ax[1].plot(Ts,vref/((2**bits)*3*nernst_slope(Ts)),label=label,color=col)
ax[1].set_yscale("log");ax[1].set_xlabel("Electrode temperature (°C)");ax[1].set_ylabel("Ideal pH increment per ADC LSB")
ax[1].legend();ax[1].yaxis.set_major_formatter(ticker.LogFormatterMathtext())
save(fig,"A07_pH_conditioning","pH conditioning and ideal ADC resolution",
     "Panel (a): 5 V, gain +3, midpoint 2.5 V. Panel (b): LSB = Vref / 2^N; gain +3 for both designs.")

fig,ax=make_fig()
panel(ax[0],"a","Local endurance sensitivity (±20%)")
labels={"mass_kg":"Mass","speed_m_s":"Speed","Crr":"Rolling resistance","efficiency":"Drive efficiency","aux_W":"Auxiliary load"}
keys=list(labels)
for i,key in enumerate(keys):
 lo=next(v["endurance_change_pct"] for v in sensitivity if v["parameter"]==key and v["multiplier"]==.8)
 hi=next(v["endurance_change_pct"] for v in sensitivity if v["parameter"]==key and v["multiplier"]==1.2)
 ax[0].barh(i-.14,lo,height=.25,color=colors[0],label="Input −20%" if i==0 else None)
 ax[0].barh(i+.14,hi,height=.25,color=colors[1],label="Input +20%" if i==0 else None)
ax[0].set_yticks(range(len(keys)),[labels[k] for k in keys]);ax[0].invert_yaxis()
ax[0].axvline(0,color="#7a8c94",lw=.8);ax[0].set_xlabel("Change from baseline endurance (%)")
ax[0].set_ylim(5.35,-.6)
ax[0].legend(loc="lower right",fontsize=7,ncol=2)
panel(ax[1],"b","COM height controls geometric tip bound")
heights=np.linspace(.35,.85,151)
for massp,col in zip([0,1,2],colors):
 x=(massp*.8)/(24+massp); z=(24*heights+massp)/(24+massp)
 ax[1].plot(heights,np.degrees(np.arctan((L/2-x)/z)),label=f"Payload {massp} kg",color=col)
ax[1].set_xlabel("Assumed unloaded COM height (m)");ax[1].set_ylabel("Front tipping angle (deg)")
ax[1].legend()
save(fig,"A08_parameter_sensitivity","Which missing measurements change the conclusions?",
     "Endurance baseline: 24 kg, 10° grade, 0.25 m/s, Crr 0.06, η 0.80, auxiliaries 20 W. One-at-a-time scenarios.")

(OUT/"figure_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
# A concise human-readable methods and exact-results companion.
md = f"""# Reproducible analytical study

## Evidence status
All figures and numbers are calculated from explicit assumptions. No trials, environmental records, learned-model outputs or measured Nemesis performance were supplied or fabricated. Geometry is estimated from the visual model. These results screen design choices and define measurements needed; they are not a proof of mission capability.

## Coordinate, unit and parameter definitions
The body origin is the ground-plane projection of chassis center on the level reference support plane: x forward, y left, z up. COM height is measured above that support plane. Wheelbase L={L:.3f} m, track W={W:.3f} m and wheel radius r={r:.3f} m are estimated. Base mass is assumed {m0:.1f} kg, with center of mass (0,0,0.58) m; added payload is at (0.8,0,1.0) m. The base COM is held fixed: changes in arm-link mass distribution, suspension compliance and wheel lift are omitted. Full assumptions and CSV data are in analysis_results.json and tables/.

## 1. Independent steer-and-drive kinematics
Wheel velocity is u_i=v_x−ωy_i, v_i=v_y+ωx_i; steering δ_i=atan2(v_i,u_i); rolling speed s_i=sqrt(u_i²+v_i²). Equivalent (δ+π,−s) is used to put displayed angles within ±90°. This mathematical equivalence is not confirmation of hardware steering limits. Zero-speed steering singularities, steering-rate feasibility, scrub and cable limits must be handled in implementation. Ideal straight wheel speed at 0.25 m/s is {summary['straight_wheel_rpm_at_0p25mps']:.6f} rpm.

## 2. Grade, rolling resistance and output torque
F=m[a+g(sin α+Crr cos α)], τ_w=Fr/4, and minimum uniform friction μ_min=tan α+Crr+a/(g cos α). Crr=0.06 and g=9.80665 m/s². Four equal longitudinal force shares are assumed. τ_w is required gearbox-output torque, so drivetrain efficiency must not be used to divide it a second time when comparing output-shaft motor data. Continuous torque and thermal ratings, steering losses, terrain deformation and unequal loads are missing. The simple Coulomb screen is necessary under these assumptions, not sufficient for soft-soil traversal.

| Grade | Force (N) | Wheel torque (N m) | Minimum μ | Battery power (W) | Endurance (h) |
|---:|---:|---:|---:|---:|---:|
"""
for d in summary["grade_summary"]:
 md+=f"| {d['grade_deg']}° | {d['force_N']:.6f} | {d['each_wheel_torque_Nm']:.6f} | {d['minimum_mu']:.6f} | {d['power_W_at_0p25mps_aux20W']:.6f} | {d['endurance_h_at_0p25mps_aux20W']:.6f} |\n"
md+=f"""
Power/endurance columns assume speed 0.25 m/s and 20 W auxiliaries throughout a constant grade.

## 3. Static payload stability
p_COM=(m_base p_base+m_payload p_payload)/(m_base+m_payload). The front-edge margin is L/2−x_COM−h_COM tan β, where β slopes downhill toward the front. The ideal geometric front-tip angle is atan[(L/2−x_COM)/h_COM]; lateral tip angle uses (W/2−|y_COM|)/h_COM. These are zero-margin geometric tipping bounds, not safe operating slopes. Dynamic motion, obstacles, tire compliance, ground contact uncertainty, external arm force and actual arm-link motion must reduce the allowable operating envelope.

| Added payload (kg) | COM x (m) | COM z (m) | Front tip (deg) | Lateral tip (deg) | Front margin at 20° (m) |
|---:|---:|---:|---:|---:|---:|
"""
for d in summary["stability_summary"]:
 md+=f"| {d['payload_kg']} | {d['COM_x_m']:.6f} | {d['COM_z_m']:.6f} | {d['front_tip_deg']:.6f} | {d['lateral_tip_deg']:.6f} | {d['front_margin_m_at_20deg']:.6f} |\n"
md+=f"""
## 4. Power and endurance
Usable energy E=11.1 V×10 Ah×0.85×0.90={Euse:.6f} Wh. The 0.90 factor derates available battery energy; it is separate from traction conversion efficiency. Battery power P=Fv/0.80+P_aux. Endurance t=E/P; hypothetical distance is v×t. Battery capacity, low-voltage cutoffs, temperature, current-induced voltage sag, motor maps and auxiliary load must be measured. No regenerative braking is modeled. Constant-grade operation is a stress scenario, not a route prediction. No solar contribution is included.

## 5. Response lag while moving
For a first-order step model y(t)=1−exp(−t/τ), t90=τ ln(10), t95=τ ln(20), and spatial distance traveled before response fraction p is v t_p. Time constants 5,15,30 s are illustrative assumptions, not MQ-sensor datasheet or calibration values. Real sensors can have humidity effects, cross-sensitivity, heater transients, nonlinearity and asymmetric recovery. Even stopping to dwell cannot provide chemical selectivity.

| Assumed τ (s) | t90 (s) | t95 (s) | Distance to 90% at 0.25 m/s (m) |
|---:|---:|---:|---:|
"""
for d in summary["gas_summary"]:
 md+=f"| {d['tau_s']} | {d['t90_s']:.6f} | {d['t95_s']:.6f} | {d['distance90_m_at_0p25mps']:.6f} |\n"
md+=f"""
## 6. Fail-safe stopping
Required clear distance d=v t_latency+v²/(2a)+d_margin. The figures sweep assumed latency and available deceleration, with margin 0.15 m. Available deceleration is a measured ground-level quantity that must include slope and slip effects; the formula assumes constant braking during the modeled interval. Human approach, obstacle motion and mechanical emergency-stop run-down are omitted.

| Speed (m/s) | Clearance at latency 0.3 s, a=0.5 m/s², margin 0.15 m (m) |
|---:|---:|
"""
for d in summary["stopping_summary"]:
 md+=f"| {d['speed_m_s']} | {d['clearance_m_latency0p3_decel0p5_margin0p15']:.6f} |\n"
phs=summary["pH_summary"]
md+=f"""
## 7. Nernst slope and analog conditioning
The ideal monovalent electrode slope is S(T)=ln(10) R(T+273.15)/F. R=8.31446261815324 J mol⁻¹ K⁻¹; F=96485.33212 C mol⁻¹. An explicitly assumed positive-gain conditioning circuit maps V_ADC=2.5+3 S(T)(7−pH). Electrode polarity can be reversed in actual hardware. At 25°C the magnitude is {phs['slope_mV_per_pH_at25C']:.6f} mV/pH. A Mega-compatible 5 V, 10-bit ADC scenario has 1024 codes indexed 0…1023. Its ideal least-significant-bit (LSB) input interval is Vref/2^N = 5/1024 V, equal to {phs['ADC_LSB_mV']:.6f} mV. The maximum output code is 1023; it does not define the denominator for the physical quantizer interval. The table records a continuous ideal code coordinate, not simulated integer conversions. The 5 V reference must be measured; the nominal supply is not an accuracy standard.

With gain 3, the ideal pH increment per ADC LSB is {phs['ADC_step_pH_at25C']:.8f}. The pH 0 and 14 outputs are {phs['conditioned_voltage_at_pH0_V']:.6f} V and {phs['conditioned_voltage_at_pH14_V']:.6f} V. The maximum ideal gain for a symmetric full pH 0–14 span at 25°C is {phs['maximum_gain_for_full_pH0to14_ADC_span_at25C']:.6f}; practical rail/headroom constraints reduce it. Quantization is not accuracy: buffer calibration, electrode condition, temperature compensation, very high input impedance, input bias current and analog noise dominate real pH uncertainty. For comparison, a proposed 3.3 V, 12-bit front end with gain 3 and midpoint 1.65 V gives an ideal increment of {phs["proposed_3p3V_12bit_ADC_step_pH_at25C"]:.8f} pH/LSB. This is a proposed acquisition design, not proof the present hardware achieves it. An electrode cannot be connected directly to a MCU ADC: a very-high-input-impedance buffer/conditioner and compatible offset/gain are required for either case. ADC resolution and usable effective resolution must not be conflated.

## 8. Sensitivity and reproducibility
Figure A08 changes one assumed input by ±20% at a time and holds all other inputs constant; it is a deterministic sensitivity sweep, not a probability distribution or confidence interval. This isolates which measurements are most valuable without inventing experimental uncertainty. The endurance reference is {summary['endurance_sensitivity_reference_h']:.6f} h. The second panel varies unknown base COM height to demonstrate why photo-based tipping claims are unreliable.

Run engineering_analysis.py with the bundled Python runtime after installing matplotlib into manuscript/python_packages. Numeric tables use deterministic grids with no random numbers. Each PNG is saved at 360 dpi and each SVG retains editable text. No external plot or dataset is republished.

## Supporting theory references
The independently derived kinematic and contact assumptions are consistent with Alexander and Maddocks (1989), Lee and Li (2015), and Iagnemma and Dubowsky (2004); the stability limitations are motivated by Papadopoulos and Rey (1996). Refer to research/mobility_sources.json for exact primary-source citations. Equations here are explicitly stated elementary model derivations, not copied reported results.

## Priority measurements
Measure complete mass and COM in several arm poses; loaded wheel radius; motor continuous output torque/current/temperature; tire friction and rolling losses on each surface; actual controller/watchdog latency and braking distance; battery usable energy at duty cycle; sensor step/recovery response; calibrated analog pH transfer and uncertainty. Report successful and failed trials separately from these analytical design screens.
"""
(OUT/"explanations.md").write_text(md,encoding="utf-8")
print(json.dumps({"figures":len(manifest),"tables":len(tables),"summary":summary},indent=2))
