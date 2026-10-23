# Step 1c: batman + emcee transit fit, free rp/R*, b, a/R*, T0 (P fixed at box-grid best). Quadratic LD fixed (TESS band, M3V ~ u1 0.25 u2 0.35, inferred typical).
import numpy as np, sys, json, batman, emcee
d=np.load(sys.argv[1]); t,f=d['t'],d['f']
b1=json.load(open('evidence/01b_box_checks.json')); P=b1['P']; T0=b1['T0']
dt=(((t-T0)/P+0.5)%1-0.5)*P; m=np.abs(dt)<0.3; x,y=dt[m],f[m]
sig=1.4826*np.median(np.abs(y[np.abs(x)>0.06]-np.median(y[np.abs(x)>0.06])))
pr=batman.TransitParams(); pr.t0=0; pr.per=P; pr.rp=0.03; pr.a=25; pr.inc=89.; pr.ecc=0; pr.w=90; pr.u=[0.25,0.35]; pr.limb_dark='quadratic'
TM=batman.TransitModel(pr,x,supersample_factor=11,exp_time=10/1440)
def model(p):
    tc,rp,b,a,c=p; pr.t0=tc; pr.rp=rp; pr.a=a; pr.inc=np.degrees(np.arccos(b/a)); return c*TM.light_curve(pr)
def lnp(p):
    tc,rp,b,a,c=p
    if not(-0.02<tc<0.02 and 0.005<rp<0.5 and 0<=b<1+rp and 2<a<200): return -np.inf
    return -0.5*np.sum(((y-model(p))/sig)**2)
nw=32; p0=np.array([0,0.035,0.3,30,1])+np.array([1e-3,2e-3,0.2,3,1e-5])*np.random.default_rng(1).standard_normal((nw,5)); p0[:,2]=np.abs(p0[:,2])
S=emcee.EnsembleSampler(nw,5,lnp); S.run_mcmc(p0,6000,progress=False); ch=S.get_chain(discard=2000,thin=10,flat=True)
G=6.674e-8; rho=3*np.pi*(ch[:,3])**3/(G*(P*86400)**2)
rhoTIC=0.289*1.989e33/(4/3*np.pi*(0.310*6.957e10)**3)
aTIC=(rhoTIC*G*(P*86400)**2/(3*np.pi))**(1/3)
inc=np.arccos(ch[:,2]/ch[:,3]); T14=P/np.pi*np.arcsin(np.sqrt((1+ch[:,1])**2-ch[:,2]**2)/ch[:,3]/np.sin(inc))*24
T14_b0_TIC=P/np.pi*np.arcsin((1)/aTIC)*24
q=lambda v:[float(np.percentile(v,16)),float(np.percentile(v,50)),float(np.percentile(v,84))]
best=ch[np.argmax([lnp(p) for p in ch[::20]])*20]
out=dict(P=P,T0=T0,noise_ppm_per10min=sig*1e6,n_pts=int(m.sum()),rp_rs=q(ch[:,1]),b=q(ch[:,2]),a_rs=q(ch[:,3]),rho_gcc=q(rho),rho_TIC_gcc=rhoTIC,a_rs_TIC=aTIC,
  T14_h=q(T14),T14_expected_b0_TIC_h=T14_b0_TIC,Rp_Re=q(ch[:,1]*0.310*109.1),depth_model_ppm=float((1-model(np.r_[best[0],best[1],best[2],best[3],1]).min())*1e6),
  frac_b_gt_0p9=float(np.mean(ch[:,2]>0.9)),frac_grazing=float(np.mean(ch[:,2]>1-ch[:,1])),acceptance=float(np.mean(S.acceptance_fraction)),LD_fixed=[0.25,0.35])
# density-fixed comparison: chi2 best with a fixed to TIC (b free) vs free
from scipy.optimize import minimize
def nll_fixed(p): return -lnp([p[0],p[1],p[2],aTIC,p[3]])
r=min((minimize(nll_fixed,[0,0.035,b0,1],method='Nelder-Mead',options=dict(maxiter=4000,xatol=1e-7,fatol=1e-3)) for b0 in [0.1,0.5,0.8,0.9]),key=lambda z:z.fun)
out['TIC_density_fit']=dict(rp_rs=r.x[1],b=r.x[2],chi2=2*r.fun,chi2_free_best=-2*lnp(best),dchi2_fixed_minus_free=2*r.fun+2*lnp(best))
json.dump(out,open('evidence/01c_transit_fit.json','w'),indent=1); print(json.dumps(out,indent=1))
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
xs=np.linspace(-0.3,0.3,2000); TM2=batman.TransitModel(pr,xs,supersample_factor=11,exp_time=10/1440)
fig,a=plt.subplots(figsize=(8,4.5)); be=np.arange(-0.3,0.3,0.005); idx=np.digitize(x,be)
a.plot(x*24,(y-1)*1e6,',',color='0.8'); a.errorbar([(be[j-1]+be[j])/2*24 for j in range(1,len(be))],[np.mean(y[idx==j]-1)*1e6 for j in range(1,len(be))],[np.std(y[idx==j])/np.sqrt(max(1,(idx==j).sum()))*1e6 for j in range(1,len(be))],fmt='ko',ms=3)
pr.t0=best[0];pr.rp=best[1];pr.a=best[3];pr.inc=np.degrees(np.arccos(best[2]/best[3])); a.plot(xs*24,(TM2.light_curve(pr)*best[4]-1)*1e6,'C3',label='free fit')
pr.t0=r.x[0];pr.rp=r.x[1];pr.a=aTIC;pr.inc=np.degrees(np.arccos(min(r.x[2]/aTIC,1))); a.plot(xs*24,(TM2.light_curve(pr)*r.x[3]-1)*1e6,'C0--',label='density fixed to TIC')
a.set_ylim(-2500,1200); a.set_xlim(-4,4); a.legend(); a.set_xlabel('hours'); a.set_title('transit fit (7-min bins)'); plt.savefig('plots/01_transit_fit.png',dpi=110)
