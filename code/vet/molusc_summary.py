# Copied from tic240488148-companions/molusc_summary.py; only M changed (0.289 Msun; copied from hz-wide/vet_270573718).
import pandas as pd, numpy as np, glob
A=pd.concat([pd.read_csv(f) for f in sorted(glob.glob('molusc_out/m50k_s1?_all.csv'))],ignore_index=True)
n=len(A); M=0.289
A['m2']=A['mass ratio']*M
kept=A[A['Full Rejected']==0]
print('generated',n,'kept',len(kept),'frac %.4f'%(len(kept)/n))
print('reject: RUWE %.4f  Gaia %.4f'%(A['RUWE Rejected'].mean(),A['Gaia Rejected'].mean()))
st=A['m2']>=0.08
print('stellar (m2>=0.08) generated',st.sum(),'kept',(st&(A['Full Rejected']==0)).sum(),'frac %.4f'%((st&(A['Full Rejected']==0)).sum()/st.sum()))
w=(A['semi-major axis(AU)']*(1-A['eccentricity'])>10)
print('TRC-relevant a(1-e)>10AU: generated %.4f of all, kept %.4f of all'%(w.mean(),(w&(A['Full Rejected']==0)).mean()))
print('TRC-relevant & m2>=0.1: kept %.4f generated %.4f'%(((w)&(A['Full Rejected']==0)&(A['m2']>=0.1)).mean(),(w&(A['m2']>=0.1)).mean()))
for f in sorted(glob.glob('molusc_out/m50k_s1?_all.csv')):
    a=pd.read_csv(f); print(f, 'kept frac %.4f'%(1-a['Full Rejected'].mean()))
rng=np.random.default_rng(7); N=1000000; nk=int(round(len(kept)/n*N))
kept[['mass ratio','semi-major axis(AU)','eccentricity']].iloc[rng.integers(0,len(kept),nk)].reset_index(drop=True).to_csv('molusc_out/molusc_for_trc_N1e6.csv')
print('wrote',nk,'rows')
A.to_parquet('molusc_out/all_200k.parquet') if False else None
