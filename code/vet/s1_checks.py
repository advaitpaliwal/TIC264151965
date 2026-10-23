# Step 1b: box checks at the GPU period: per-sector/per-year depth, odd/even, secondary at every phase, 2P and P/2, 0.594 d relation.
import numpy as np, sys, json
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
d=np.load(sys.argv[1]); t,f,s=d['t'],d['f'],d['s']
P0=4.815795935724232; T00=2336.179233927793
def box(P,T0,w,ph0=0.0,sel=None):
    dt=(((t-T0)/P-ph0+0.5)%1-0.5)*P; sel=np.ones_like(t,bool) if sel is None else sel
    i=(np.abs(dt)<w/2)&sel; o=(np.abs(dt)>w)&(np.abs(dt)<w+0.25)&sel
    if i.sum()<3: return np.nan,np.nan,0
    return float(np.median(f[o])-np.mean(f[i])), float(1.4826*np.median(np.abs(f[o]-np.median(f[o])))/np.sqrt(i.sum())), int(i.sum())
best=None
for P in P0+np.linspace(-4e-5,4e-5,81):
    for dT in np.linspace(-0.02,0.02,41):
        for w in [0.04,0.05,0.06,0.07]:
            dd,e,n=box(P,T00+dT,w)
            if best is None or dd/e>best[0]: best=(dd/e,P,T00+dT,w,dd,e)
snr,P,T0,w,dep,err=best; out=dict(P=P,T0=T0,box_width_d=w,depth_ppm=dep*1e6,err_ppm=err*1e6,snr=snr)
# per sector
out['per_sector']={int(x):dict(zip(['depth_ppm','err_ppm','n_in'],[v*1e6 if k<2 else v for k,v in enumerate(box(P,T0,w,sel=(s==x)))])) for x in np.unique(s)}
out['per_year']={}
for name,sel in [('Y4_S38',s==38),('Y5_S65',s==65),('Y8_S99-102',s>=99)]:
    a=box(P,T0,w,sel=sel); out['per_year'][name]=dict(depth_ppm=a[0]*1e6,err_ppm=a[1]*1e6,n_in=a[2])
# odd/even
ep=np.round((t-T0)/P).astype(int)
o=box(P,T0,w,sel=(ep%2==1)); e=box(P,T0,w,sel=(ep%2==0))
out['odd_even']=dict(odd_ppm=o[0]*1e6,odd_err=o[1]*1e6,even_ppm=e[0]*1e6,even_err=e[1]*1e6,sigma=abs(o[0]-e[0])/np.hypot(o[1],e[1]))
# secondary scan across all phases (box of same width), excluding primary
phs=np.arange(0,1,0.0025); sc=[]
for ph in phs:
    dd,ee,n=box(P,T0,w,ph0=ph); sc.append((ph,dd*1e6,ee*1e6))
sc=np.array(sc); m=(sc[:,0]>0.03)&(sc[:,0]<0.97)
k=np.nanargmax(sc[m,1]/sc[m,2]); out['secondary_scan']=dict(best_phase=sc[m][k,0],depth_ppm=sc[m][k,1],err_ppm=sc[m][k,2],snr=sc[m][k,1]/sc[m][k,2],
   at_0p5=dict(zip(['depth_ppm','err_ppm'],sc[np.argmin(abs(sc[:,0]-0.5)),1:3])), n_phases_snr_gt3=int(np.sum(sc[m,1]/sc[m,2]>3)), n_phases=int(m.sum()))
# 2P halves and P/2
a=box(2*P,T0,w); b=box(2*P,T0+P,w); out['twoP']=dict(half0_ppm=a[0]*1e6,half0_err=a[1]*1e6,half1_ppm=b[0]*1e6,half1_err=b[1]*1e6)
h=box(P,T0,w,ph0=0.5); out['halfP_phase0p5']=dict(depth_ppm=h[0]*1e6,err_ppm=h[1]*1e6)
# per-epoch depths
eps=sorted(set(ep[np.abs(((t-T0)/P+0.5)%1-0.5)*P<w/2]))
pe=[]
for k_ in eps:
    sel=(ep==k_); a=box(P,T0,w,sel=sel); pe.append(dict(epoch=int(k_),t=float(T0+k_*P),sector=int(s[sel][0]),depth_ppm=a[0]*1e6,err_ppm=a[1]*1e6,n_in=a[2]))
out['per_epoch']=pe
dd=np.array([x['depth_ppm'] for x in pe]); ee=np.array([x['err_ppm'] for x in pe]); g=np.isfinite(dd)&(ee>0)
wm=np.sum(dd[g]/ee[g]**2)/np.sum(1/ee[g]**2); out['per_epoch_chi2']=dict(chi2=float(np.sum(((dd[g]-wm)/ee[g])**2)),dof=int(g.sum()-1),max_single_frac_of_total_snr2=float(np.max((dd[g]/ee[g])**2)/np.sum((dd[g]/ee[g])**2)),n_neg=int(np.sum(dd[g]<0)))
out['ratio_P_over_0.5942']=P/0.5941529573089234
json.dump(out,open('evidence/01b_box_checks.json','w'),indent=1)
print(json.dumps({k:v for k,v in out.items() if k!='per_epoch'},indent=1))
# plots
fig,ax=plt.subplots(2,2,figsize=(13,8)); ax=ax.ravel()
def binplot(a,x,y,bw,c='k'):
    be=np.arange(x.min(),x.max()+bw,bw); idx=np.digitize(x,be); bc=[];bm=[];bs=[]
    for j in range(1,len(be)):
        q=y[idx==j]
        if len(q)>2: bc.append((be[j-1]+be[j])/2); bm.append(np.mean(q)); bs.append(np.std(q)/np.sqrt(len(q)))
    a.errorbar(bc,bm,bs,fmt='o',color=c,ms=3)
dt=(((t-T0)/P+0.5)%1-0.5)*P*24; mm=np.abs(dt)<8
ax[0].plot(dt[mm],(f[mm]-1)*1e6,',',color='0.75'); binplot(ax[0],dt[mm],(f[mm]-1)*1e6,0.25); ax[0].set_ylim(-3000,1500); ax[0].set_title(f'folded P={P:.5f} d, depth {dep*1e6:.0f}±{err*1e6:.0f} ppm'); ax[0].set_xlabel('hours')
ph=((t-T0)/P+0.25)%1-0.25; binplot(ax[1],ph,(f-1)*1e6,0.005); ax[1].set_title('full phase (0.024 d bins)'); ax[1].set_ylim(-1500,600); ax[1].axvline(0.5,ls=':')
ax[2].plot(sc[:,0],sc[:,1]/sc[:,2],'k-'); ax[2].axhline(3,ls=':'); ax[2].set_title('box SNR at every phase'); ax[2].set_xlabel('phase')
for k_,(nm,c) in enumerate([('odd','C0'),('even','C3')]):
    sel=mm&(ep%2==k_^1); binplot(ax[3],dt[sel],(f[sel]-1)*1e6,0.33,c)
ax[3].set_title('odd (blue) vs even (red)'); ax[3].set_ylim(-3000,1500)
plt.tight_layout(); plt.savefig('plots/01_fold_secondary_oddeven.png',dpi=110)
fig,a=plt.subplots(figsize=(8,4)); a.errorbar([x['t'] for x in pe],dd,ee,fmt='o'); a.axhline(wm); a.set_xlabel('BTJD'); a.set_ylabel('depth ppm'); a.set_title('per-transit depth'); plt.savefig('plots/01_per_epoch.png',dpi=110)
