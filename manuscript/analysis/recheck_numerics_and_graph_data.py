"""Independent numerical/graph-data recheck; original results are read-only."""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:
    os.environ.setdefault(k,'1')
import sys,json,hashlib,importlib.util
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'python_packages'))
import numpy as np
import pandas as pd
import joblib
from sklearn.inspection import permutation_importance
OUT=BASE/'analysis/ml_outputs'; TAB=BASE/'analysis/tables';checks=[]
def check(name,actual,expected,atol=1e-10):
    a=np.asarray(actual);e=np.asarray(expected)
    ok=bool(np.allclose(a,e,rtol=1e-11,atol=atol,equal_nan=True))
    checks.append({'check':name,'passed':ok,'elements':int(a.size),
                   'maximum_absolute_difference':float(np.nanmax(np.abs(a-e))) if a.size else 0})
    if not ok: raise AssertionError(name)
g=9.80665;L=.908;W=.930;r=.140;mass=24.;crr=.06;eta=.8;E=11.1*10*.85*.9
# Recompute every exported engineering table column from elementary equations.
x=pd.read_csv(TAB/'kinematics_sweep.csv');xy={'FL':(L/2,W/2),'FR':(L/2,-W/2),'RL':(-L/2,W/2),'RR':(-L/2,-W/2)}
pos=np.array([xy[k] for k in x.wheel]);om=x.body_speed_m_s/x.turn_radius_m
u=x.body_speed_m_s-om*pos[:,1];v=om*pos[:,0];th=np.arctan2(v,u)
check('kinematic headings',np.degrees(th),x.steering_deg)
check('kinematic signed speed',np.hypot(u,v),x.rolling_speed_m_s)
check('kinematic wheel rpm',np.hypot(u,v)/r*60/(2*np.pi),x.wheel_rpm)
x=pd.read_csv(TAB/'grade_torque_traction.csv');a=np.radians(x.grade_deg)
force=x.mass_kg*g*(np.sin(a)+crr*np.cos(a))
check('grade force',force,x.steady_force_N);check('wheel torque',force*r/4,x.wheel_output_torque_Nm)
check('grade minimum mu',np.tan(a)+crr,x.minimum_uniform_mu)
check('accelerating torque',(force+.1*x.mass_kg)*r/4,x.wheel_output_torque_Nm_at_accel_0p1)
x=pd.read_csv(TAB/'static_stability.csv');cx=.8*x.payload_kg/(24+x.payload_kg);cz=(24*.58+x.payload_kg)/(24+x.payload_kg)
check('COM x',cx,x.COM_x_m);check('COM z',cz,x.COM_z_m)
check('front margin',L/2-cx-cz*np.tan(np.radians(x.downhill_front_slope_deg)),x.front_edge_margin_m)
check('front tip',np.degrees(np.arctan((L/2-cx)/cz)),x.front_static_tip_deg)
check('side tip',np.degrees(np.arctan((W/2)/cz)),x.lateral_static_tip_deg)
x=pd.read_csv(TAB/'energy_endurance.csv');a=np.radians(x.grade_deg)
power=mass*g*(np.sin(a)+crr*np.cos(a))*x.speed_m_s/eta+x.auxiliary_load_W
check('battery power',power,x.battery_power_W);check('usable energy',np.full(len(x),E),x.usable_energy_Wh)
check('endurance',E/power,x.endurance_h);check('ideal distance',x.speed_m_s*E/power*3.6,x.ideal_distance_km)
x=pd.read_csv(TAB/'sensor_step_response.csv')
check('step response',-np.expm1(-x.time_after_step_s/x.assumed_tau_s),x.normalized_response)
check('step travel distance',.25*x.time_after_step_s,x.spatial_distance_m_at_0p25mps)
x=pd.read_csv(TAB/'sensor_spatial_lag.csv')
check('90pct distance',x.speed_m_s*x.assumed_tau_s*np.log(10),x.distance_to_90pct_m)
check('90pct dwell',x.assumed_tau_s*np.log(10),x.minimum_dwell_90pct_s)
check('95pct dwell',x.assumed_tau_s*np.log(20),x.minimum_dwell_95pct_s)
x=pd.read_csv(TAB/'stopping_clearance.csv')
check('stopping clearance',x.speed_m_s*x.total_latency_s+x.speed_m_s**2/(2*x.available_deceleration_m_s2)+x.geometric_margin_m,x.required_clearance_m)
x=pd.read_csv(TAB/'pH_Nernst_ADC.csv');s=np.log(10)*8.31446261815324*(x.temperature_C+273.15)/96485.33212
mid=np.where(x.ADC_bits==10,2.5,1.65);voltage=mid+3*s*(7-x.pH)
check('Nernst slope',s,x.ideal_electrode_slope_V_per_pH);check('conditioned voltage',voltage,x.conditioned_voltage_V)
check('ideal ADC coordinate',voltage/x.ADC_reference_V*2.**x.ADC_bits,x.ideal_ADC_code_coordinate)
check('physical ADC LSB',x.ADC_reference_V/(2.**x.ADC_bits*3*s),x.ADC_step_pH)
x=pd.read_csv(TAB/'local_sensitivity.csv');calc=[];p0=mass*g*(np.sin(np.radians(10))+crr*np.cos(np.radians(10)))*.25/eta+20
for row in x.itertuples():
    p={'mass_kg':24,'speed_m_s':.25,'Crr':.06,'efficiency':.8,'aux_W':20};p[row.parameter]*=row.multiplier
    calc.append(p['mass_kg']*g*(np.sin(np.radians(10))+p['Crr']*np.cos(np.radians(10)))*p['speed_m_s']/p['efficiency']+p['aux_W'])
check('sensitivity power',calc,x.battery_power_W);check('sensitivity endurance',E/np.array(calc),x.endurance_h)
check('sensitivity percent',100*(p0/np.array(calc)-1),x.endurance_change_pct)
# Existing 65-check ledger remains unmodified; recorded values also internally agree.
old=json.loads((BASE/'analysis/final_numerical_audit.json').read_text())
for item in old['checks']:check('prior65: '+item['check'],item['recomputed'],item['recorded'],atol=2e-9)
# Reparse original archive using the executable listing's explicitly audited loader.
spec=importlib.util.spec_from_file_location('listing',BASE/'text/code_listing_revision.py');listing=importlib.util.module_from_spec(spec);spec.loader.exec_module(listing)
data=listing.load_eligible();n=len(data);a=int(.70*n);b=int(.85*n);tr=data.iloc[:a];va=data.iloc[a:b];te=data.iloc[b:]
check('chronological partition sizes',[len(tr),len(va),len(te)],[5140,1102,1102])
assert tr.timestamp.max()<va.timestamp.min()<te.timestamp.min()
assert data[listing.FEATURES].isna().sum().sum()==0
saved=pd.read_csv(OUT/'test_predictions.csv',parse_dates=['timestamp']);assert list(te.timestamp)==list(saved.timestamp)
check('held-out targets',te[listing.TARGET],saved[listing.TARGET])
metrics=pd.read_csv(OUT/'metrics.csv').set_index('model');y=te[listing.TARGET].to_numpy();pred={}
for family in metrics.index:
    m=joblib.load(OUT/'models'/f'{family}.joblib');pred[family]=m.predict(te[listing.FEATURES])
    check(f'{family} serialized predictions',pred[family],saved[family+'_prediction'],atol=1e-12)
    check(f'{family} imputer fitted on training',m['imputer'].statistics_,tr[listing.FEATURES].median())
    if family=='Ridge':
        check('Ridge train-only scaler mean',m['scaler'].mean_,tr[listing.FEATURES].mean())
        check('Ridge train-only scaler variance',m['scaler'].var_,tr[listing.FEATURES].var(ddof=0))
    residual=pred[family]-y
    point=[np.mean(abs(residual)),np.sqrt(np.mean(residual**2)),1-np.sum(residual**2)/np.sum((y-y.mean())**2),np.mean(residual)]
    for key,value in zip(['MAE','RMSE','R2','Bias'],point):check(f'{family} test {key}',value,metrics.loc[family,'test_'+key])
    check(f'{family} validation score',np.sqrt(np.mean((m.predict(va[listing.FEATURES])-va[listing.TARGET])**2)),metrics.loc[family,'validation_RMSE'])
    costs=pd.read_csv(OUT/'desktop_costs.csv').set_index('model')
    check(f'{family} actual serialized bytes',(OUT/'models'/f'{family}.joblib').stat().st_size,costs.loc[family,'artifact_bytes_uncompressed_joblib'])
# Independently reproduce all 2,000 paired calendar-day score replicates.
days=te.timestamp.dt.normalize().to_numpy();names=pd.unique(days);blocks=[np.flatnonzero(days==day) for day in names]
check('observed-day block counts',[len(blocks),min(map(len,blocks)),max(map(len,blocks))],[48,10,24])
rng=np.random.default_rng(20260915);draws={k:[] for k in pred}
for _ in range(2000):
    idx=np.concatenate([blocks[j] for j in rng.integers(len(blocks),size=len(blocks))]);yy=y[idx]
    for family,pp in pred.items():
        e=pp[idx]-yy;draws[family].append([np.mean(abs(e)),np.sqrt(np.mean(e**2)),1-np.sum(e**2)/np.sum((yy-yy.mean())**2),np.mean(e)])
for family in pred:
    arr=np.asarray(draws[family]);stored=pd.read_csv(OUT/f'bootstrap_{family}.csv')
    check(f'{family} all paired bootstrap scores',arr,stored[['MAE','RMSE','R2','Bias']])
    for j,key in enumerate(['MAE','RMSE','R2','Bias']):
        check(f'{family} {key} interval',np.quantile(arr[:,j],[.025,.975]),[metrics.loc[family,'test_'+key+'_lo'],metrics.loc[family,'test_'+key+'_hi']])
rr=json.loads((OUT/'results.json').read_text());delta=np.asarray(draws['DummyMean'])[:,1]-np.asarray(draws['Ridge'])[:,1]
check('paired RMSE reduction interval',np.quantile(delta,[.025,.975]),rr['paired_test_RMSE_gain_vs_mean_baseline']['percentile_95'])
# Data actually summarized in ML figures: daily traces, coverage, RH-bin summaries.
trace=saved.set_index('timestamp')[[listing.TARGET,'Ridge_prediction']].resample('D').mean();count=saved.set_index('timestamp')[listing.TARGET].resample('D').count();trace.loc[count<12]=np.nan
oldtrace=pd.read_csv(OUT/'test_daily_trace.csv');check('daily trace values',trace.to_numpy(),oldtrace[[listing.TARGET,'Ridge_prediction']]);check('daily trace counts',count,oldtrace.observed_hours)
rh=te.RH.to_numpy();bin_index=np.digitize(rh,np.arange(0,101,10))-1
for row in pd.read_csv(OUT/'test_residual_RH_bins.csv').itertuples():
    e=(pred[row.model]-y)[bin_index==row.RH_bin_low//10]
    check(f'{row.model} RH-bin {row.RH_bin_low}',[len(e),e.mean(),*np.quantile(e,[.25,.75])],[row.n,row.residual_mean,row.residual_q25,row.residual_q75])
model=joblib.load(OUT/'models/Ridge.joblib');importance=permutation_importance(model,va[listing.FEATURES],va[listing.TARGET],n_repeats=10,random_state=20260915,scoring='neg_root_mean_squared_error',n_jobs=1)
imp=pd.read_csv(OUT/'validation_permutation_sensitivity.csv').set_index('feature').loc[listing.FEATURES]
check('validation permutation means',importance.importances_mean,imp.validation_RMSE_increase_mean)
check('validation permutation SDs',importance.importances_std,imp.validation_RMSE_increase_sd)
report={'status':'PASS','checks':checks,'check_groups':len(checks),'all_pass':all(x['passed'] for x in checks),'scope':'Read-only independent recomputation of all 9 engineering tables; serialized ML pipelines, all test metrics, all 2000 paired bootstrap replicates, plotted daily/RH summaries and validation permutation sensitivity. Candidate refits are tested separately by code_listing_revision.py. Existing 65-check ledger preserved.','figure_scope':['8 engineering figures','5 ML figures'],'not_retested':'Historical desktop timing measurements are retained as recorded; timing varies between runs. No new rover measurements or performance claims.'}
(BASE/'analysis/code_graph_recheck.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'status':report['status'],'check_groups':len(checks),'scalar_values_checked':sum(c['elements'] for c in checks)},indent=2))
