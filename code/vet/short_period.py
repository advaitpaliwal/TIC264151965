# Step 1d: is the ~0.594 d signal stellar variability or a second transit? LS on raw PDCSAP/QLP, and fold of the search LC (with the 4.8158 d transits masked).
import numpy as np, json, glob, warnings; warnings.filterwarnings('ignore')
from astropy.io import fits
from astropy.timeseries import LombScargle
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
b=json.load(open('evidence/01b_box_checks.json')); P,T0=b['P'],b['T0']
out={}; fig,ax=plt.subplots(2,3,figsize=(16,7)); ax=ax.ravel()
fq=np.linspace(1/15,1/0.2,60000)
for j,fn in enumerate(sorted(glob.glob('lcfits/tess*s_lc.fits'))+sorted(glob.glob('lcfits/hlsp_qlp*.fits'))):
    h=fits.open(fn); d=h[1].data; col='PDCSAP_FLUX' if 'PDCSAP_FLUX' in d.columns.names else 'SAP_FLUX'; sec=int(h[0].header['SECTOR'])
    t=d['TIME']; f=np.array(d[col],float); m=(d['QUALITY']==0)&np.isfinite(t)&np.isfinite(f); t,f=t[m],f[m]/np.nanmedian(f[m])
    pw=LombScargle(t,f).power(fq); k=np.argmax(pw); i594=np.argmin(abs(1/fq-0.5942)); 
    w=(1/fq>0.55)&(1/fq<0.65); k2=np.where(w)[0][np.argmax(pw[w])]
    amp=np.std(f)*1e6
    out[f'S{sec}_{col}']=dict(top_period_d=float(1/fq[k]),top_power=float(pw[k]),best_in_0p55_0p65_d=float(1/fq[k2]),power_there=float(pw[k2]),rms_ppm=float(amp))
    if j<4:
        ax[j].plot(1/fq,pw,'k-',lw=.5); ax[j].set_xscale('log'); ax[j].axvline(0.5942,c='r',ls=':'); ax[j].set_title(f'S{sec} {col} LS; top {1/fq[k]:.3f} d',fontsize=9)
z=np.load('264151965.npz'); t,f=z['t'],z['f']
dt=(((t-T0)/P+0.5)%1-0.5)*P; m=np.abs(dt)>0.06; t,f=t[m],f[m]
for Ps,T0s,lab in [(0.5941529573089234,2334.429586864932,'iter1'),(0.594479339970699,2334.8086694387453,'iter3')]:
    ph=((t-T0s)/Ps+0.25)%1-0.25; be=np.linspace(-0.25,0.75,61); ix=np.digitize(ph,be)
    bm=np.array([np.mean(f[ix==i]-1)*1e6 for i in range(1,len(be))]); bc=(be[1:]+be[:-1])/2
    ax[4 if lab=='iter1' else 5].plot(bc,bm,'o-'); ax[4 if lab=='iter1' else 5].set_title(f'search LC folded at {Ps:.5f} d ({lab}), 4.82 d transits masked',fontsize=9)
    # sinusoid fit amplitude vs box
    A=np.vstack([np.sin(2*np.pi*ph),np.cos(2*np.pi*ph),np.ones_like(ph)]).T; c,*_=np.linalg.lstsq(A,f,rcond=None)
    out[f'fold_{lab}']=dict(P=Ps,sin_amp_ppm=float(np.hypot(c[0],c[1])*1e6),binned_profile_ppm=[round(x) for x in bm],min_bin_ppm=float(bm.min()),
       n_bins_below_minus150ppm=int((bm<-150).sum()))
# LS on the flattened search LC too
pw=LombScargle(t,f).power(fq); k=np.argmax(pw); out['search_LC_LS']=dict(top_period_d=float(1/fq[k]),top_power=float(pw[k]))
out['P_ratio_4p8158_over_0p5942']=P/0.5941529573089234
json.dump(out,open('evidence/01d_short_period.json','w'),indent=1); print(json.dumps({k:{kk:vv for kk,vv in v.items() if kk!='binned_profile_ppm'} if isinstance(v,dict) else v for k,v in out.items()},indent=1))
plt.tight_layout(); plt.savefig('plots/01_short_period.png',dpi=95)
