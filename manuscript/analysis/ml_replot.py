"""Regenerate figures from frozen outputs; no fitting, tuning or test rescoring."""
from pathlib import Path
src=Path(__file__).with_name('ml_benchmark.py').read_text(encoding='utf-8')
exec(compile(src.split('# DATA AUDIT.')[0],str(Path(__file__).with_name('ml_benchmark.py')),'exec'))
result=json.loads((OUT/'results.json').read_text(encoding='utf-8'))
winner=result['selection']
valid=pd.read_csv(OUT/'cleaned_observations_with_flags.csv',parse_dates=['timestamp'])
keep=valid.eligible
assign=pd.read_csv(OUT/'split_assignments.csv',parse_dates=['timestamp'])
records=valid.merge(assign[['source_row','split']],on='source_row',how='inner')
parts={k:records.loc[records.split==k].copy().sort_values('timestamp') for k in ['train','validation','test']}
testlog=pd.read_csv(OUT/'test_predictions.csv',parse_dates=['timestamp'])
yte=testlog[TARGET].to_numpy();preds={k:testlog[k+'_prediction'].to_numpy() for k in ORDER}
point={r['model']:{m:r['test_'+m] for m in ['MAE','RMSE','R2','Bias']} for r in result['models']}
ci={r['model']:{m:[r['test_'+m+'_lo'],r['test_'+m+'_hi']] for m in ['MAE','RMSE','R2','Bias']} for r in result['models']}
desk=pd.read_csv(OUT/'desktop_costs.csv');imp=pd.read_csv(OUT/'validation_permutation_sensitivity.csv')
section=src.split('# Figure 1:')[1].split('# Fully derived narrative')[0]
exec(compile('# Figure 1:'+section,str(Path(__file__).with_name('ml_benchmark.py')),'exec'))
result['environment']['scipy']=scipy.__version__
save_json('results.json',result)
req=OUT/'requirements-recorded.txt';text=req.read_text(encoding='utf-8')
if 'scipy==' not in text:req.write_text(text+'scipy=='+scipy.__version__+'\n',encoding='utf-8')
print('Regenerated five figure pairs from frozen CSV/JSON; no model refit or score changes.')
