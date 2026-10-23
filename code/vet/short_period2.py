# Step 1e: test whether the 0.594 d peaks are aliases of catalogued neighbour variables: ASASSN-V J142912.22-584458.1 (EW, P 0.396213 d, 76.7") and Gaia DR3 RRAB (P 0.52389 d, 24.5").
import numpy as np, json
from astropy.timeseries import LombScargle
b=json.load(open('evidence/01b_box_checks.json')); P,T0=b['P'],b['T0']
z=np.load('264151965.npz'); t,f=z['t'],z['f']; dt=(((t-T0)/P+0.5)%1-0.5)*P; m=np.abs(dt)>0.06; t,f=t[m],f[m]
fq=np.linspace(1/2.0,1/0.15,400000); ls=LombScargle(t,f); pw=ls.power(fq)
order=np.argsort(pw)[::-1]; peaks=[]
for i in order:
    if all(abs(fq[i]-fq[j])>0.01 for j in peaks): peaks.append(i)
    if len(peaks)==8: break
out=dict(top_peaks=[dict(P_d=float(1/fq[i]),power=float(pw[i])) for i in peaks],FAP_top=float(ls.false_alarm_probability(pw[peaks[0]])))
for lab,Pv in [('EW_P',0.396213),('EW_P/2',0.396213/2),('EW_3P/2',0.396213*1.5),('RRAB_P',0.52389),('RRAB_P/2',0.52389/2)]:
    k=np.argmin(abs(1/fq-Pv)); w=(abs(1/fq-Pv)<0.002); out[lab]=dict(P=Pv,max_power_pm2mday=float(pw[w].max()),at_P=float(1/fq[w][np.argmax(pw[w])]))
for lab,Pv in [('EW',0.396213),('RRAB',0.52389)]:
    ph=(t/Pv)%1; A=np.vstack([np.sin(2*np.pi*n*ph) for n in (1,2,3)]+[np.cos(2*np.pi*n*ph) for n in (1,2,3)]+[np.ones_like(ph)]).T
    c,*_=np.linalg.lstsq(A,f,rcond=None); out[lab+'_harmonic_amps_ppm']=[float(np.hypot(c[n],c[n+3])*1e6) for n in range(3)]
json.dump(out,open('evidence/01e_short_period_neighbours.json','w'),indent=1); print(json.dumps(out,indent=1))
