# Step 4: transit depth in SAP vs PDCSAP (SPOC S38, S65) and QLP SAP_FLUX vs DET_FLUX (S99, S100), same flattening for both.
import numpy as np, json, glob, warnings; warnings.filterwarnings('ignore')
from astropy.io import fits
from wotan import flatten
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
b=json.load(open('evidence/01b_box_checks.json')); P,T0=b['P'],b['T0']; W=0.04
def depth(t,f):
    dt=(((t-T0)/P+0.5)%1-0.5)*P; i=np.abs(dt)<W/2; o=(np.abs(dt)>W)&(np.abs(dt)<W+0.25)
    s=1.4826*np.median(np.abs(f[o]-np.median(f[o]))); return float((np.median(f[o])-np.mean(f[i]))*1e6), float(s/np.sqrt(i.sum())*1e6), int(i.sum())
out={}; fig,ax=plt.subplots(2,4,figsize=(16,6),sharey='row')
files=sorted(glob.glob('lcfits/tess*s_lc.fits'))+sorted(glob.glob('lcfits/hlsp_qlp*s0099*.fits'))+sorted(glob.glob('lcfits/hlsp_qlp*s0100*.fits'))
for j,fn in enumerate(files):
    h=fits.open(fn); d=h[1].data; spoc='PDCSAP_FLUX' in d.columns.names
    sec=int(h[0].header['SECTOR'])
    t=d['TIME']; q=(d['QUALITY']==0)&np.isfinite(t)
    pairs=[('SAP_FLUX','PDCSAP_FLUX')] if spoc else [('SAP_FLUX','DET_FLUX')]
    res={}
    for k_,col in enumerate(pairs[0]):
        f=np.array(d[col],float); m=q&np.isfinite(f)&(f>0); tt,ff=t[m],f[m]/np.nanmedian(f[m])
        # mask transits while detrending
        dt=(((tt-T0)/P+0.5)%1-0.5)*P; intr=np.abs(dt)<0.06
        tr=flatten(tt,np.where(intr,np.nan,ff),method='biweight',window_length=0.5,return_trend=True)[1]
        tr=np.interp(tt,tt[np.isfinite(tr)],tr[np.isfinite(tr)]); fl=ff/tr
        dd,ee,n=depth(tt,fl); res[col]=dict(depth_ppm=dd,err_ppm=ee,n_in=n)
        if spoc and col=='SAP_FLUX':  # SAP is not crowding-corrected: correct with CROWDSAP/FLFRCSAP for a like-for-like depth
            c=h[1].header['CROWDSAP']; res[col]['crowdsap']=c; res[col]['depth_ppm_crowd_corrected']=dd/c; res[col]['err_crowd_corrected']=ee/c
        a=ax[k_,j]; a.plot(dt*24,(fl-1)*1e6,',',color='0.7'); be=np.arange(-6,6.01,0.33); ix=np.digitize(dt*24,be)
        a.plot([(be[i-1]+be[i])/2 for i in range(1,len(be))],[np.mean(fl[ix==i]-1)*1e6 if (ix==i).sum() else np.nan for i in range(1,len(be))],'ko-',ms=3)
        a.set_xlim(-6,6); a.set_ylim(-3000,1500); a.set_title(f'S{sec} {col}: {dd:.0f}±{ee:.0f} ppm',fontsize=9)
    out[f'S{sec}_{"SPOC" if spoc else "QLP"}']=res
json.dump(out,open('evidence/04_sap_vs_pdcsap.json','w'),indent=1); print(json.dumps(out,indent=1))
plt.tight_layout(); plt.savefig('plots/04_sap_vs_pdcsap.png',dpi=100)
