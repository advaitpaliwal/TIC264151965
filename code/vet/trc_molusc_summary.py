# Copy of hz-wide/vet_270573718/glue/trc_molusc_summary.py for TIC 264151965 (one case: none removed); adds scenario mean +- sd per run as glue/trc_summary.py.
import json,glob,pandas as pd,numpy as np
out={}; tic=264151965
m=pd.read_csv('molusc_out/molusc_for_trc_N1e6.csv'); N=10**6
P0=pd.read_csv('trc_molusc/out/probs_0.csv'); Ms=float(P0.loc[P0.ID==tic,'M_s'].iloc[0])
use=m[m['semi-major axis(AU)']*(1-m['eccentricity'])>10]
out['molusc_file']=dict(rows=len(m),rows_used_a1e_gt10=len(use),frac_of_N_used=len(use)/N,M_s_trc=Ms,q_floor=0.1/Ms,rows_raised_to_floor=int((use['mass ratio']<0.1/Ms).sum()))
for d in ['trc_molusc/out']:
    R=[json.load(open(f)) for f in sorted(glob.glob(d+'/res_*.json'))]
    F=np.array([r['FPP'] for r in R]); Nf=np.array([r['NFPP'] for r in R])
    P=pd.concat([pd.read_csv(f).assign(run=i) for i,f in enumerate(sorted(glob.glob(d+'/probs_*.csv')))])
    sc=P.groupby(['run','scenario']).prob.sum().groupby('scenario').agg(['mean','std']).sort_values('mean',ascending=False)
    top=P.groupby(['ID','scenario']).prob.sum().div(len(R)).sort_values(ascending=False).head(8)
    out[d]=dict(n_runs=len(R),seeds=[1000+r['run'] for r in R],FPP=F.round(4).tolist(),NFPP=Nf.tolist(),FPP_mean=float(F.mean()),FPP_sd=float(F.std(ddof=1)),FPP_min=float(F.min()),FPP_max=float(F.max()),n_below_0035=int((F<0.035).sum()),n_below_0015=int((F<0.015).sum()),NFPP_mean=float(Nf.mean()),NFPP_sd=float(Nf.std(ddof=1)),NFPP_max=float(Nf.max()),n_stars=R[0]['n_stars'],depth_ppm=R[0]['depth_ppm'],
      scenario_mean_sd={s:[float(a),float(b)] for s,(a,b) in sc.iterrows()},top_ID_scenario=[(int(i),s,float(v)) for (i,s),v in top.items()],sec=[round(r['sec']) for r in R])
json.dump(out,open('evidence/07_triceratops_molusc_summary.json','w'),indent=1)
for d,v in out.items(): print(d,json.dumps(v))
