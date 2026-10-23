# Summarise 10 TRICERATOPS runs: FPP/NFPP mean +- std, scenario probabilities averaged over runs.
import json, glob, numpy as np, pandas as pd
R=[json.load(open(f)) for f in sorted(glob.glob('trc/out/res_*.json'))]
fpp=np.array([r['FPP'] for r in R]); nfpp=np.array([r['NFPP'] for r in R])
P=pd.concat([pd.read_csv(f).assign(run=i) for i,f in enumerate(sorted(glob.glob('trc/out/probs_*.csv')))])
by=P.groupby(['ID','scenario'])['prob'].agg(['mean','std']).reset_index().sort_values('mean',ascending=False)
sc=P.groupby(['run','scenario'])['prob'].sum().groupby('scenario').agg(['mean','std']).sort_values('mean',ascending=False)
out=dict(n_runs=len(R),runs=R,FPP_mean=fpp.mean(),FPP_std=fpp.std(ddof=1),FPP_min=fpp.min(),FPP_max=fpp.max(),NFPP_mean=nfpp.mean(),NFPP_std=nfpp.std(ddof=1),NFPP_max=nfpp.max(),
  scenario_totals=sc.reset_index().to_dict('records'),top_star_scenarios=by.head(12).to_dict('records'))
json.dump(out,open('evidence/05_triceratops_summary.json','w'),indent=1,default=float)
print(json.dumps({k:v for k,v in out.items() if k!='runs'},indent=1,default=float))
for r in R: print(r['run'],r['FPP'],r['NFPP'],round(r['sec']),r['depth_ppm'],r['n_stars'])
