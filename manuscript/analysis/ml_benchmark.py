"""Reproducible external-data CO calibration benchmark; no rover performance claim.
Run with Python 3.12 and the pinned requirements from the repository root.
No downloads. Raw ZIP is preserved, hash checked/reported. Models fit only train.
"""
from __future__ import annotations
import os
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
import sys, json, zipfile, hashlib, platform, time, warnings, itertools
from pathlib import Path
BASE = Path(__file__).resolve().parents[1]
PACKAGES = BASE / 'python_packages'
if PACKAGES.exists(): sys.path.insert(0, str(PACKAGES))
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sklearn
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.inspection import permutation_importance
import joblib
import scipy

SEED = 20260915
FEATURES = ['PT08.S1(CO)', 'PT08.S2(NMHC)', 'PT08.S3(NOx)', 'PT08.S4(NO2)', 'PT08.S5(O3)', 'T', 'RH', 'AH']
TARGET = 'CO(GT)'
N_BOOT = 2000
OUT = BASE / 'analysis' / 'ml_outputs'
FIG = OUT / 'figures'
MOD = OUT / 'models'
for p in [OUT, FIG, MOD]: p.mkdir(parents=True, exist_ok=True)
COLORS = {'DummyMean':'#69747D', 'Ridge':'#007E87', 'RandomForest':'#CC682D', 'HistGradientBoosting':'#465B9B'}
LABELS = {'DummyMean':'Mean baseline', 'Ridge':'Ridge', 'RandomForest':'Random forest', 'HistGradientBoosting':'Histogram boosting'}
ORDER = list(COLORS)
SPLIT_COL = {'train':'#007E87', 'validation':'#CC682D', 'test':'#465B9B'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':11,'axes.labelsize':10,'xtick.labelsize':9,'ytick.labelsize':9,'legend.fontsize':9,'figure.dpi':110,'savefig.dpi':300,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.17,'grid.linewidth':.5,'axes.axisbelow':True,'svg.fonttype':'none','pdf.fonttype':42})

def save_json(name, obj):
    (OUT/name).write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False, default=str),encoding='utf-8')
def metrics(y,p):
    return {'MAE':float(mean_absolute_error(y,p)), 'RMSE':float(np.sqrt(mean_squared_error(y,p))), 'R2':float(r2_score(y,p)), 'Bias':float(np.mean(p-y))}
def pubsave(fig, name):
    fig.savefig(FIG/(name+'.png'),bbox_inches='tight',facecolor='white')
    fig.savefig(FIG/(name+'.svg'),bbox_inches='tight',facecolor='white')
    plt.close(fig)
def dates(ax):
    loc=mdates.AutoDateLocator(minticks=4,maxticks=7)
    ax.xaxis.set_major_locator(loc);ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(loc))
def panel(ax,label,title):
    ax.set_title(f'{label}  {title}',loc='left',fontweight='semibold',pad=10)

# DATA AUDIT. Rows are eligible if timestamp/target valid and >=1 predictor exists.
archive=BASE/'research'/'air_quality.zip'
archive_sha=hashlib.sha256(archive.read_bytes()).hexdigest()
EXPECTED_ARCHIVE_SHA256='d4a64013fb385288a8a48d9d193ca7079b2e1bbddf6f8d458feb8c08ab2b8a2a'
if archive_sha != EXPECTED_ARCHIVE_SHA256:
    raise ValueError('Input archive SHA-256 differs from the archived study; do not mix dataset versions.')
with zipfile.ZipFile(archive) as z:
    rawbytes=z.read('AirQualityUCI.csv')
    import io
    raw=pd.read_csv(io.BytesIO(rawbytes),sep=';',decimal=',')
raw['source_row']=np.arange(2,len(raw)+2) # CSV line number, header=1
stamp=pd.to_datetime(raw['Date'].fillna('')+' '+raw['Time'].fillna(''),format='%d/%m/%Y %H.%M.%S',errors='coerce')
raw['timestamp']=stamp
valid=raw.loc[stamp.notna(),['source_row','timestamp',TARGET]+FEATURES].copy()
if valid['timestamp'].duplicated().any(): raise ValueError('Duplicate timestamps require explicit adjudication.')
valid=valid.sort_values('timestamp',kind='stable').reset_index(drop=True)
missing_code={c:int((valid[c]==-200).sum()) for c in [TARGET]+FEATURES}
valid[[TARGET]+FEATURES]=valid[[TARGET]+FEATURES].replace(-200,np.nan)
# Do not impute a reference target. Entirely absent sensor records are abstentions.
no_target=valid[TARGET].isna()
all_missing=valid[FEATURES].isna().all(axis=1)
keep=~no_target & ~all_missing
eligible=valid.loc[keep].reset_index(drop=True)
assert eligible[TARGET].notna().all() and np.isfinite(eligible[TARGET]).all()
assert len(FEATURES)==8 and not any(c in FEATURES for c in ['NMHC(GT)','C6H6(GT)','NOx(GT)','NO2(GT)'])
n=len(eligible); b1=int(.70*n); b2=int(.85*n)
parts={'train':eligible.iloc[:b1].copy(),'validation':eligible.iloc[b1:b2].copy(),'test':eligible.iloc[b2:].copy()}
assert parts['train'].timestamp.max()<parts['validation'].timestamp.min()<parts['test'].timestamp.min()
assign=pd.concat([d.assign(split=k) for k,d in parts.items()],ignore_index=True)
assign[['source_row','timestamp','split']].to_csv(OUT/'split_assignments.csv',index=False)
valid.assign(eligible=keep,missing_target=no_target,all_predictors_missing=all_missing).to_csv(OUT/'cleaned_observations_with_flags.csv',index=False)
summary={}
for k,d in parts.items():
    elapsed=(d.timestamp.max()-d.timestamp.min()).total_seconds()/3600+1
    summary[k]={'n':len(d),'start':str(d.timestamp.min()),'end':str(d.timestamp.max()),'calendar_days_with_observations':int(d.timestamp.dt.normalize().nunique()),'available_hours_in_span':int(elapsed),'observed_fraction_of_span':float(len(d)/elapsed),'gaps_greater_than_one_hour':int((d.timestamp.diff().dt.total_seconds()>3600).sum()),'CO_mean':float(d[TARGET].mean()),'CO_sd':float(d[TARGET].std()),'CO_min':float(d[TARGET].min()),'CO_max':float(d[TARGET].max()),'RH_mean':float(d.RH.mean()),'partial_missing_predictor_rows':int(d[FEATURES].isna().any(axis=1).sum())}
audit={'archive_sha256':archive_sha,'csv_sha256':hashlib.sha256(rawbytes).hexdigest(),'raw_csv_rows':len(raw),'invalid_or_blank_timestamp_rows':int(stamp.isna().sum()),'valid_timestamp_rows':len(valid),'duplicate_timestamps':0,'timestamp_start':str(valid.timestamp.min()),'timestamp_end':str(valid.timestamp.max()),'missing_code':missing_code,'missing_target_excluded':int(no_target.sum()),'all_predictors_missing_total':int(all_missing.sum()),'additional_all_predictors_missing_excluded_with_valid_target':int((all_missing & ~no_target).sum()),'eligible_rows':n,'eligible_predictor_missing_cells':int(eligible[FEATURES].isna().sum().sum()),'selection_rule':'Valid timestamp, observed CO(GT), at least one observed predictor. -200 converted to NaN. No concentration outlier filtering or clipping.','timestamp_convention':'Naive dataset-local time; timezone is not inferred.','repository_discrepancy':'Repository prose states 9358 observations/March2004–February2005; archived CSV counts/range reported here follow the actual timestamp parse.','splits':summary}
save_json('data_audit.json',audit)

# Search spaces declared before scoring test. No internal random validation split.
spaces={
'DummyMean':[{}],
'Ridge':[{'alpha':a} for a in [.01,.1,1.,10.,100.,1000.]],
'RandomForest':[{'max_depth':d,'min_samples_leaf':l} for d,l in itertools.product([10,None],[1,5,15])],
'HistGradientBoosting':[{'learning_rate':lr,'max_leaf_nodes':leaves,'l2_regularization':l2} for lr,leaves,l2 in itertools.product([.05,.1],[15,31],[0.,1.])]}
protocol={'dataset_doi':'10.24432/C59K5F','source_url':'https://archive.ics.uci.edu/dataset/360/air+quality','target':TARGET,'target_unit':'mg m^-3','features':FEATURES,'excluded_reference_gases':['NMHC(GT)','C6H6(GT)','NOx(GT)','NO2(GT)'],'random_seed':SEED,'split_rule':'Chronological eligible-row boundaries at floor(0.70*n) and floor(0.85*n).','preprocessing':'Training-only median imputation; Ridge also training-only StandardScaler. No polynomial/time/target-lag features.','refit_policy':'Chosen per-family pipeline already fitted on first 70%; no train+validation refit.','selection_metric':'Validation RMSE; first candidate wins exact ties. Overall family selected only by validation RMSE.','search_spaces':spaces,'RF_fixed':{'n_estimators':200,'max_features':1.0,'n_jobs':1,'random_state':SEED},'HGB_fixed':{'max_iter':250,'min_samples_leaf':20,'early_stopping':False,'random_state':SEED},'test_evaluation':'Only after all configurations and overall validation winner are frozen.','bootstrap':'2000 paired resamples of entire observed calendar-day blocks with replacement. No filling missing hours, interpolation, model refitting, or test tuning.','ci_scope':'Percentile 95% intervals conditional on fitted models and observed test days; within-day dependence preserved, cross-day dependence not modeled.','prediction_policy':'Unclipped predictions; retain negative values for transparent evaluation.'}
save_json('benchmark_protocol.json',protocol)
Xtr=parts['train'][FEATURES]; ytr=parts['train'][TARGET].to_numpy()
Xva=parts['validation'][FEATURES]; yva=parts['validation'][TARGET].to_numpy()
def make_model(family,p):
    if family=='DummyMean': estimator=DummyRegressor(strategy='mean')
    elif family=='Ridge': estimator=Ridge(**p)
    elif family=='RandomForest': estimator=RandomForestRegressor(n_estimators=200,max_features=1.,n_jobs=1,random_state=SEED,**p)
    else: estimator=HistGradientBoostingRegressor(max_iter=250,min_samples_leaf=20,early_stopping=False,random_state=SEED,**p)
    steps=[('imputer',SimpleImputer(strategy='median'))]
    if family=='Ridge':steps.append(('scaler',StandardScaler()))
    return Pipeline(steps+[('regressor',estimator)])
selected={}; config={}; search=[]
for family,candidates in spaces.items():
    best=float('inf')
    for cid,p in enumerate(candidates):
        model=make_model(family,p); start=time.perf_counter();model.fit(Xtr,ytr);elapsed=time.perf_counter()-start
        v=metrics(yva,model.predict(Xva)); rec={'family':family,'candidate':cid,'parameters':json.dumps(p,sort_keys=True),'fit_seconds':elapsed,**{'validation_'+k:z for k,z in v.items()}}
        search.append(rec)
        if v['RMSE']<best:
            best=v['RMSE']; selected[family]=model; config[family]={'parameters':p,'validation':v,'fit_seconds':elapsed,'candidate':cid}
    print(f'{family}: selected using validation RMSE={best:.4f}',flush=True)
searchdf=pd.DataFrame(search); searchdf.to_csv(OUT/'validation_search.csv',index=False)
winner=min(ORDER,key=lambda k:config[k]['validation']['RMSE'])
save_json('frozen_selection.json',{'selection_basis':'Validation only, before any test metric calculation.','selected_family':winner,'models':config})

# Frozen test evaluation and retained fitted pipelines.
Xte=parts['test'][FEATURES];yte=parts['test'][TARGET].to_numpy();ts=parts['test'].timestamp.reset_index(drop=True)
preds={k:selected[k].predict(Xte) for k in ORDER}
point={k:metrics(yte,preds[k]) for k in ORDER}
# Calendar-day cluster resampling preserves exactly the observed, irregular hours.
day=ts.dt.normalize(); daynames=list(day.unique());blocks=[np.flatnonzero(day.to_numpy()==d) for d in daynames]
rng=np.random.default_rng(SEED)
boot={k:{m:[] for m in ['MAE','RMSE','R2','Bias']} for k in ORDER}; delta=[]
for _ in range(N_BOOT):
    idx=np.concatenate([blocks[j] for j in rng.integers(0,len(blocks),size=len(blocks))])
    for k in ORDER:
        for m,v in metrics(yte[idx],preds[k][idx]).items():boot[k][m].append(v)
    delta.append(boot['DummyMean']['RMSE'][-1]-boot[winner]['RMSE'][-1])
ci={k:{m:[float(x) for x in np.quantile(v,[.025,.975])] for m,v in dic.items()} for k,dic in boot.items()}
rows=[];desktop=[]
for k in ORDER:
    path=MOD/(k+'.joblib');joblib.dump(selected[k],path,compress=0)
    size=path.stat().st_size
    for _ in range(3):selected[k].predict(Xte)
    batch=[];single=[]
    for _ in range(21):
        t=time.perf_counter();selected[k].predict(Xte);batch.append((time.perf_counter()-t)*1000)
        t=time.perf_counter();selected[k].predict(Xte.iloc[:1]);single.append((time.perf_counter()-t)*1000)
    row={'model':k,'selected_by_validation':k==winner,'validation_MAE':config[k]['validation']['MAE'],'validation_RMSE':config[k]['validation']['RMSE'],'validation_R2':config[k]['validation']['R2'],'test_n':len(yte),**{'test_'+m:v for m,v in point[k].items()}}
    for m in ci[k]:row.update({f'test_{m}_lo':ci[k][m][0],f'test_{m}_hi':ci[k][m][1]})
    rows.append(row)
    desktop.append({'model':k,'artifact_bytes_uncompressed_joblib':size,'selected_candidate_fit_seconds':config[k]['fit_seconds'],'batch_n':len(Xte),'batch_prediction_median_ms':float(np.median(batch)),'batch_prediction_q25_ms':float(np.quantile(batch,.25)),'batch_prediction_q75_ms':float(np.quantile(batch,.75)),'single_prediction_median_ms':float(np.median(single)),'single_prediction_q25_ms':float(np.quantile(single,.25)),'single_prediction_q75_ms':float(np.quantile(single,.75)),'repetitions':21,'n_jobs_or_OMP':1})
    # Replay artifact verifies serialization without refitting.
    restored=joblib.load(path);np.testing.assert_allclose(restored.predict(Xte),preds[k],rtol=0,atol=1e-12)
res=pd.DataFrame(rows);res.to_csv(OUT/'metrics.csv',index=False)
desk=pd.DataFrame(desktop);desk.to_csv(OUT/'desktop_costs.csv',index=False)
testlog=parts['test'][['source_row','timestamp',TARGET,'RH','T']].reset_index(drop=True).copy()
for k in ORDER:testlog[k+'_prediction']=preds[k];testlog[k+'_residual']=preds[k]-yte
testlog.to_csv(OUT/'test_predictions.csv',index=False)
for k in ORDER:pd.DataFrame(boot[k]).to_csv(OUT/('bootstrap_'+k+'.csv'),index=False)
result={'data_audit':audit,'selection':winner,'models':rows,'paired_test_RMSE_gain_vs_mean_baseline':{'point':point['DummyMean']['RMSE']-point[winner]['RMSE'],'percentile_95':list(np.quantile(delta,[.025,.975]))},'test_calendar_day_blocks':len(blocks),'min_observed_hours_per_test_day':min(map(len,blocks)),'max_observed_hours_per_test_day':max(map(len,blocks)),'bootstrap_repetitions':N_BOOT,'desktop_costs':desktop,'environment':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'scikit_learn':sklearn.__version__,'matplotlib':matplotlib.__version__,'joblib':joblib.__version__,'scipy':scipy.__version__,'platform':platform.platform(),'processor':platform.processor(),'thread_setting':{x:os.environ.get(x) for x in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']}},'limitations':['External single-site historical sensor-array benchmark, not Nemesis data or validation.','Different MOS sensor materials and electronics; no MQ-series transfer demonstrated.','No spatial/site holdout available; chronological holdout probes only this site/time shift.','Daily cluster intervals preserve within-day dependence but not dependencies spanning days.','No uncertainty from model fitting/selection, missing-target selection, or reference instrument error is included.','Desktop timing and serialized model size are not microcontroller latency, RAM, flash, energy or control-loop performance.']}
save_json('results.json',result)

# Validation-only permutation sensitivity, never used to change model or features.
pimp=permutation_importance(selected[winner],Xva,yva,n_repeats=10,random_state=SEED,scoring='neg_root_mean_squared_error',n_jobs=1)
imp=pd.DataFrame({'feature':FEATURES,'validation_RMSE_increase_mean':pimp.importances_mean,'validation_RMSE_increase_sd':pimp.importances_std}).sort_values('validation_RMSE_increase_mean')
imp.to_csv(OUT/'validation_permutation_sensitivity.csv',index=False)

# Figure 1: data coverage and shift; no fabricated measurements/interpolation.
f,axs=plt.subplots(2,2,figsize=(10.4,7.3),layout='constrained')
for k,d in parts.items():
    g=d.set_index('timestamp')[TARGET].resample('D').agg(['mean','count']);g.loc[g['count']<12,'mean']=np.nan
    axs[0,0].plot(g.index,g['mean'],color=SPLIT_COL[k],lw=1.0,label=f'{k.capitalize()} (n={len(d):,})')
    axs[0,1].hist(d[TARGET],bins=np.arange(0,12.5,.5),density=True,histtype='step',color=SPLIT_COL[k],lw=1.7,label=k.capitalize())
panel(axs[0,0],'a','Observed CO by chronological partition');axs[0,0].set_ylabel('Daily mean CO (mg m$^{-3}$)');dates(axs[0,0]);axs[0,0].legend(frameon=False,loc='upper right',fontsize=8)
panel(axs[0,1],'b','Target distribution');axs[0,1].set_xlabel('Reference CO (mg m$^{-3}$)');axs[0,1].set_ylabel('Density');axs[0,1].legend(frameon=False)
coverage=valid.set_index('timestamp').assign(eligible=keep.to_numpy()).resample('MS').agg(total=(TARGET,'size'),available=('eligible','sum'))
coverage.to_csv(OUT/'monthly_data_coverage.csv')
x=np.arange(len(coverage));axs[1,0].bar(x,coverage.total,color='#DFE4E8',label='Timestamped rows');axs[1,0].bar(x,coverage.available,color='#007E87',label='Eligible rows');axs[1,0].set_xticks(x);axs[1,0].set_xticklabels(coverage.index.strftime('%b\n%Y'),fontsize=7);axs[1,0].set_ylabel('Hourly observations');axs[1,0].legend(frameon=False,fontsize=8);panel(axs[1,0],'c','Recorded-data availability')
for k,d in parts.items():axs[1,1].hist(d.RH,bins=np.arange(0,105,5),density=True,histtype='step',color=SPLIT_COL[k],lw=1.7,label=k.capitalize())
axs[1,1].set_xlabel('Relative humidity (%)');axs[1,1].set_ylabel('Density');panel(axs[1,1],'d','Environmental distribution shift');axs[1,1].legend(frameon=False)
f.suptitle('External UCI dataset: chronology, availability and distribution shift',fontsize=13,fontweight='semibold');pubsave(f,'01_dataset_audit')

# Figure 2: test metrics and uncertainty; all families retained regardless of rank.
f,axs=plt.subplots(1,3,figsize=(10.4,3.5),layout='constrained')
ypos=np.arange(4)
for ax,m,tag in zip(axs,['MAE','RMSE','R2'],['a','b','c']):
    for i,k in enumerate(ORDER):
        v=point[k][m];lo,hi=ci[k][m];ax.errorbar(v,i,xerr=[[v-lo],[hi-v]],fmt='o',color=COLORS[k],capsize=3,ms=6)
    ax.set_yticks(ypos);ax.set_yticklabels([LABELS[k]+(' *' if k==winner else '') for k in ORDER]);ax.invert_yaxis();ax.set_xlabel(('$R^2$' if m=='R2' else m)+(' (mg m$^{-3}$)' if m!='R2' else ' (unitless)'));panel(ax,tag,{'MAE':'Absolute error','RMSE':'Root mean square error','R2':'Coefficient of determination'}[m])
    if m=='R2':ax.axvline(0,color='#333333',lw=.7,ls='--')
f.suptitle(f'Frozen chronological test: {len(yte):,} observations; 95% daily-block intervals',fontsize=12,fontweight='semibold');pubsave(f,'02_test_metrics')

# Figure 3: validation-selected model only, entire test chronology and scatter.
f=plt.figure(figsize=(10.4,7.2),layout='constrained');gs=f.add_gridspec(2,2,height_ratios=[1,1.15]);ax=f.add_subplot(gs[0,:]);ax2=f.add_subplot(gs[1,0]);ax3=f.add_subplot(gs[1,1])
trace=testlog.set_index('timestamp')[[TARGET,winner+'_prediction']].resample('D').mean();counts=testlog.set_index('timestamp')[TARGET].resample('D').count();trace.loc[counts<12,:]=np.nan
trace.assign(observed_hours=counts).to_csv(OUT/'test_daily_trace.csv')
ax.plot(trace.index,trace[TARGET],color='#202B35',lw=1.5,label='Reference');ax.plot(trace.index,trace[winner+'_prediction'],color=COLORS[winner],lw=1.5,label=LABELS[winner]);ax.set_ylabel('Daily mean CO (mg m$^{-3}$)');panel(ax,'a','Complete held-out period, daily summaries');dates(ax);ax.legend(frameon=False,ncol=2)
mx=max(yte.max(),preds[winner].max())+.3;mn=min(0,preds[winner].min())-.1
hb=ax2.hexbin(yte,preds[winner],gridsize=32,mincnt=1,cmap='Blues',linewidths=0,extent=(mn,mx,mn,mx));ax2.plot([mn,mx],[mn,mx],color='#333333',lw=.9,ls='--');ax2.set(xlabel='Reference CO (mg m$^{-3}$)',ylabel='Predicted CO (mg m$^{-3}$)',xlim=(mn,mx),ylim=(mn,mx));ax2.set_aspect('equal',adjustable='box');f.colorbar(hb,ax=ax2,label='Hourly observations',fraction=.05);panel(ax2,'b','Hourly agreement')
r=preds[winner]-yte;ax3.hist(r,bins=35,color=COLORS[winner],alpha=.8);ax3.axvline(0,color='#222222',ls='--',lw=1);ax3.axvline(r.mean(),color='#CC682D',lw=1.5,label=f'Mean bias {r.mean():.3f}');ax3.set_xlabel('Prediction minus reference (mg m$^{-3}$)');ax3.set_ylabel('Hourly observations');ax3.legend(frameon=False);panel(ax3,'c','Residual distribution')
f.suptitle('External-data predictions: '+LABELS[winner]+' selected using validation only',fontsize=13,fontweight='semibold');pubsave(f,'03_selected_model_predictions')

# Figure 4: conditional error for every frozen family.
f,axs=plt.subplots(2,2,figsize=(10.4,6.8),sharey=True,layout='constrained');resid_rows=[]
for ax,k,tag in zip(axs.ravel(),ORDER,list('abcd')):
    rh=parts['test'].RH.to_numpy();r=preds[k]-yte
    ax.scatter(rh,r,s=8,alpha=.16,color=COLORS[k],edgecolors='none',rasterized=True)
    bins=np.arange(0,101,10);bb=np.digitize(rh,bins)-1
    for j in range(len(bins)-1):
        rr=r[bb==j]
        if len(rr)<20:continue
        center=float(np.median(rh[bb==j]));me=float(rr.mean());ql,qu=np.quantile(rr,[.25,.75])
        ax.plot([center,center],[ql,qu],color='#162B35',lw=2);ax.plot(center,me,'o',color='#162B35',ms=4)
        resid_rows.append({'model':k,'RH_bin_low':bins[j],'RH_bin_high':bins[j+1],'n':len(rr),'residual_mean':me,'residual_q25':ql,'residual_q75':qu})
    ax.axhline(0,color='#333333',ls='--',lw=.8);ax.set_xlim(0,100);ax.set_xlabel('Relative humidity (%)');ax.set_ylabel('CO residual (mg m$^{-3}$)');panel(ax,tag,LABELS[k])
f.suptitle('Held-out conditional errors: hourly points and RH-bin means / interquartile ranges',fontsize=12,fontweight='semibold');pd.DataFrame(resid_rows).to_csv(OUT/'test_residual_RH_bins.csv',index=False);pubsave(f,'04_residual_humidity')

# Figure 5: desktop-specific measured costs and validation-only sensitivity.
f,axs=plt.subplots(1,3,figsize=(10.4,4.3),layout='constrained')
for i,k in enumerate(ORDER):
    dd=desk.loc[desk.model==k].iloc[0]
    axs[0].barh(i,dd.artifact_bytes_uncompressed_joblib/2**20,color=COLORS[k])
    med=dd.single_prediction_median_ms;lo=dd.single_prediction_q25_ms;hi=dd.single_prediction_q75_ms
    axs[1].errorbar(med,i,xerr=[[med-lo],[hi-med]],fmt='o',color=COLORS[k],capsize=3,ms=6)
for ax in axs[:2]:ax.set_yticks(np.arange(4));ax.set_yticklabels([LABELS[k] for k in ORDER]);ax.invert_yaxis()
axs[0].set_xscale('log');axs[0].set_xlabel('Serialized pipeline (MiB, log scale)');panel(axs[0],'a','Artifact size')
axs[1].set_xlabel('Single-row prediction (ms)');panel(axs[1],'b','Desktop prediction latency')
axs[2].barh(np.arange(len(imp)),imp.validation_RMSE_increase_mean,xerr=imp.validation_RMSE_increase_sd,color=COLORS[winner],error_kw={'linewidth':.8,'capsize':2});axs[2].set_yticks(np.arange(len(imp)));axs[2].set_yticklabels(imp.feature,fontsize=8);axs[2].set_xlabel('Validation RMSE increase (mg m$^{-3}$)');panel(axs[2],'c','Validation sensitivity');axs[2].axvline(0,color='#333333',lw=.7)
f.suptitle('Desktop computational costs and validation-only predictor sensitivity',fontsize=13,fontweight='semibold');pubsave(f,'05_desktop_cost_and_sensitivity')

# Fully derived narrative and compact reproducibility instructions.
wrow=res.loc[res.model==winner].iloc[0]
table=['| Model | Validation RMSE | Test MAE (95% interval) | Test RMSE (95% interval) | Test R² (95% interval) |','|---|---:|---:|---:|---:|']
for rr in rows:
    k=rr['model'];table.append(f"| {LABELS[k]}{' [validation choice]' if k==winner else ''} | {rr['validation_RMSE']:.4f} | {rr['test_MAE']:.4f} ({rr['test_MAE_lo']:.4f}–{rr['test_MAE_hi']:.4f}) | {rr['test_RMSE']:.4f} ({rr['test_RMSE_lo']:.4f}–{rr['test_RMSE_hi']:.4f}) | {rr['test_R2']:.4f} ({rr['test_R2_lo']:.4f}–{rr['test_R2_hi']:.4f}) |")
text=f'''# Reproducible external-data CO calibration benchmark

## Methods

The archived UCI Air Quality dataset (DOI:10.24432/C59K5F) was reanalysed, with CO(GT) in mg/m³ as the target. Predictors were only the five PT08 sensor-response channels and T, RH and AH. Other analyzer-derived gases were excluded. Date/time served only chronological partitioning and plotting. The -200 sentinel was converted to missing; target values were never imputed and concentration outliers were not removed or clipped. Rows with all eight predictors missing were excluded as unavailable observations. The archive contains {len(raw):,} parsed rows, of which {int(stamp.isna().sum()):,} lack timestamps. Among {len(valid):,} timestamped rows, {int(no_target.sum()):,} lacked reference CO and another {int((all_missing & ~no_target).sum()):,} had no predictors, leaving {n:,} observations. There were {audit['eligible_predictor_missing_cells']} missing predictor cells in the final eligible data, so the prespecified median imputation was inert. Actual timestamps span {audit['timestamp_start']} to {audit['timestamp_end']}; this differs from the repository summary and is reported from the CSV rather than silently corrected.

Chronological partitions contained {b1:,} training, {b2-b1:,} validation and {n-b2:,} test observations. Their exact dates and all source row IDs are retained. Every preprocessing step and fitted model used the first 70% only; no train-plus-validation refit was performed. Hyperparameters and family choice used validation RMSE only. The final 15% was scored after configuration freeze. All four families remain reported regardless of test ranking. The search spaces and seed {SEED} are saved in benchmark_protocol.json. Random forest used 200 trees and one worker; histogram boosting used 250 iterations with internal early stopping disabled. No time, gas-reference, or target-lag predictors were used.

Frozen predictions were assessed with MAE, RMSE, R² and mean bias. Uncertainty intervals are percentile 95% intervals from {N_BOOT:,} paired resamples of {len(blocks)} observed calendar-day clusters. All available hours in each sampled day were kept together; no missing hours were filled. Test days contain {min(map(len,blocks))}–{max(map(len,blocks))} eligible observations. These are conditional score intervals, not prediction intervals or full model-training uncertainty. Dependence across multiple days is not represented. No statistical significance claim is inferred from visual interval overlap.

## Results

The validation-selected family was **{LABELS[winner]}**. Test RMSE was **{point[winner]['RMSE']:.4f} mg/m³** (95% daily-cluster interval {ci[winner]['RMSE'][0]:.4f}–{ci[winner]['RMSE'][1]:.4f}); MAE was **{point[winner]['MAE']:.4f} mg/m³** and R² **{point[winner]['R2']:.4f}**. Mean residual (prediction minus reference) was {point[winner]['Bias']:.4f} mg/m³. These results were actually computed from the public dataset and are not A3P5 field measurements.

'''+'\n'.join(table)+f'''

All errors are in mg/m³; R² is unitless. The paired RMSE improvement versus the mean baseline was {result['paired_test_RMSE_gain_vs_mean_baseline']['point']:.4f} mg/m³ (95% interval {result['paired_test_RMSE_gain_vs_mean_baseline']['percentile_95'][0]:.4f}–{result['paired_test_RMSE_gain_vs_mean_baseline']['percentile_95'][1]:.4f}). Configuration files show the validation decision, even if another model later has a better test score.

## Figures

1. `01_dataset_audit`: observed chronology, target/environment distribution shifts and monthly availability. Daily trace values require at least 12 observed hours; missing days remain gaps. Histogram density is normalized separately per partition.
2. `02_test_metrics`: all frozen families with 95% paired calendar-day bootstrap intervals; asterisk marks the validation-selected family.
3. `03_selected_model_predictions`: full held-out daily trace, hourly agreement and residual histogram for the validation-selected family; the scatter uses observed counts rather than fabricated points.
4. `04_residual_humidity`: hourly residuals, means and interquartile ranges within fixed 10%-RH bins containing at least 20 observations. These bars are descriptive spread, not confidence intervals.
5. `05_desktop_cost_and_sensitivity`: uncompressed serialized-pipeline sizes, 21 warmed single-row desktop timings, and validation-only permutation sensitivity (10 repeats, mean ± standard deviation). Permutation effects are not causal and can be shared across correlated predictors.

All figures are original analysis graphics from UCI data, with both 300-dpi PNG and editable vector SVG files.

## Desktop cost interpretation

Timing used one worker/thread setting and is measured on the current desktop with full preprocessing included. The selected-candidate fit time, batch-prediction median and quartiles, single-row median and quartiles, serialized artifact size and software environment are in desktop_costs.csv/results.json. Serialized bytes do not measure inference RAM, embedded flash requirements or energy. Neither desktop timings nor this dataset establish onboard Mega/ESP32 feasibility.

## Limits and transfer to Nemesis

This is a historical, single-site, fixed-station benchmark with different sensor materials and electronics. It does not validate MQ7/MQ4/MQ135 calibration, selective analyte detection, mobile plume localization, model transfer to Bangladesh, sensor aging robustness, mission success, or onboard execution. The temporal holdout tests this archive's particular seasonal/drift shift; it is not independent site validation. Excluding missing targets and all-sensor outages may induce selection bias. Bootstrap intervals omit cross-day dependence, model-selection uncertainty, calibration-reference error and missing-data uncertainty. R² can vary with the target's held-out variance. No performance number may be assigned to A3P5 without new rover-specific collocation and external validation.

## Reproduce

Run `ml_benchmark.py` from the analysis folder using Python with the versions recorded in results.json; it reads ../research/air_quality.zip and discovers ../python_packages. Exact raw archive SHA256: `{archive_sha}`. The script stores all selected fitted pipelines, raw test predictions, split assignments, candidate validation scores, complete bootstrap score distributions and the cleaning audit. Saved-artifact predictions were reloaded and verified against the frozen predictions to absolute tolerance 1e-12. Numerical scores are reproducible with the recorded versions/seed; desktop timing measurements naturally vary.

## Sources

- Vito, S. (2008), Air Quality dataset. UCI. https://doi.org/10.24432/C59K5F (accessed 15 September 2026). UCI currently displays CC BY 4.0 alongside legacy research-only wording; this analysis is research use.
- De Vito, S.; Massera, E.; Piga, M.; Martinotto, L.; Di Francia, G. (2008). On field calibration of an electronic nose for benzene estimation in an urban pollution monitoring scenario. Sensors and Actuators B: Chemical 129(2), 750–757. https://doi.org/10.1016/j.snb.2007.09.060. The current CO task is a new reanalysis, not reproduction of the original benzene result.
- scikit-learn SimpleImputer documentation: https://scikit-learn.org/stable/modules/generated/sklearn.impute.SimpleImputer.html
- scikit-learn RandomForestRegressor documentation: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html
'''
(OUT/'methods_results_limits.md').write_text(text,encoding='utf-8')
(OUT/'requirements-recorded.txt').write_text('\n'.join(f'{k}=={v}' for k,v in {'numpy':np.__version__,'pandas':pd.__version__,'scikit-learn':sklearn.__version__,'matplotlib':matplotlib.__version__,'joblib':joblib.__version__,'scipy':scipy.__version__}.items())+'\n',encoding='utf-8')
print(res[['model','validation_RMSE','test_MAE','test_RMSE','test_R2']].to_string(index=False),flush=True)
print('Complete:',OUT,flush=True)
