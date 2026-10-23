# Step 1a: TLS refit near the GPU period, with the TIC star.
import numpy as np, sys, json
from transitleastsquares import transitleastsquares
d=np.load(sys.argv[1]); t,f,s=d['t'],d['f'],d['s']
m=transitleastsquares(t,f)
r=m.power(period_min=4.80,period_max=4.83,oversampling_factor=5,R_star=0.310,R_star_min=0.25,R_star_max=0.37,M_star=0.289,M_star_min=0.24,M_star_max=0.34,use_threads=1,show_progress_bar=False)
out={k:(float(getattr(r,k)) if np.ndim(getattr(r,k))==0 else None) for k in ['period','period_uncertainty','T0','depth','duration','SDE','snr','odd_even_mismatch','transit_count','distinct_transit_count','empty_transit_count','depth_mean_odd','depth_mean_even','rp_rs']}
out['depth_mean_odd']=list(map(float,r.depth_mean_odd)); out['depth_mean_even']=list(map(float,r.depth_mean_even)); out['depth_mean']=list(map(float,r.depth_mean))
out['per_transit_snr']=[float(x) for x in r.snr_per_transit]; out['transit_times']=[float(x) for x in r.transit_times]
out['note']='TLS 2.0 on the search light curve (10-min, flattened); depth is 1-depth flux ratio'
json.dump(out,open('evidence/01a_tls_refit.json','w'),indent=1); print(json.dumps({k:v for k,v in out.items() if k not in('per_transit_snr','transit_times')},indent=1))
