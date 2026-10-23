# TRICERATOPS FPP/NFPP, no neighbours removed. Adapted from hunt-ffi/trc/run_fpp.py. usage: trc_run.py RUN_INDEX   (RUN_INDEX=-1 builds the target only)
import sys, json, pickle, os, time, glob, numpy as np, warnings; warnings.filterwarnings('ignore')
from astropy.io import fits
sys.path.insert(0,'/Users/advaitpaliwal/Scratch/planet-hunt/hunt-ffi/trc'); import gaia_patch
import triceratops.triceratops as tr
tic=264151965; k=int(sys.argv[1])
b=json.load(open('evidence/01b_box_checks.json')); P,T0=b['P'],b['T0']
z=np.load('264151965.npz'); t,f=z['t'],z['f']; secs=[38,65,99,100,101,102]
pk='trc/out/target.pkl'
if not os.path.exists(pk):
    tg=tr.target(ID=tic,sectors=np.array(secs)); aps=[]
    for i,s in enumerate(secs):
        fn=glob.glob(f'lcfits/*s{s:04d}-*_lc.fits'); ap=None
        if fn:
            with fits.open(fn[0]) as h:
                a=h['APERTURE'].data.astype(int); c0=h['APERTURE'].header['CRVAL1P']; r0=h['APERTURE'].header['CRVAL2P']
            rows,cols=np.nonzero(np.bitwise_and(a,2)); ap=np.column_stack([cols+c0,rows+r0])
        if ap is None:  # QLP: no aperture in file; 5x5 centred on target (TRICERATOPS default)
            tp=np.round(tg.pix_coords[i][0]); ap=np.array([np.repeat(np.arange(tp[0]-2,tp[0]+3),5),np.tile(np.arange(tp[1]-2,tp[1]+3),5)]).T
        aps.append(ap)
    tg._aps=aps; pickle.dump(tg,open(pk,'wb'))
    tg.stars.to_csv('trc/out/stars.csv',index=False); print('target built',len(tg.stars),'stars'); 
    if k<0: sys.exit()
tg=pickle.load(open(pk,'rb'))
ph=t-T0-np.round((t-T0)/P)*P; w=np.abs(ph)<0.25
edges=np.arange(-0.25,0.25+1e-9,10/1440); idx=np.digitize(ph[w],edges)
tb=np.array([ph[w][idx==i].mean() for i in np.unique(idx)]); fb=np.array([f[w][idx==i].mean() for i in np.unique(idx)])
dur=0.05; oot=np.abs(tb)>dur; err=float(np.std(fb[oot])); depth=float(np.median(fb[oot])-fb[np.abs(tb)<dur/2*0.8].mean())
tg.calc_depths(tdepth=depth,all_ap_pixels=tg._aps)
if k==0: tg.stars.to_csv('trc/out/stars_with_tdepth.csv',index=False)
np.random.seed(1000+k); t0=time.time()
tg.calc_probs(time=tb,flux_0=fb,flux_err_0=err,P_orb=P,contrast_curve_file=None,filt='TESS',N=1000000,parallel=True,exptime=10/1440,nsamples=20,verbose=0)
tg.probs.to_csv(f'trc/out/probs_{k}.csv',index=False)
json.dump(dict(tic=tic,run=k,P=P,T0=T0,depth_ppm=depth*1e6,err_ppm=err*1e6,nbins=len(tb),n_stars=len(tg.stars),FPP=float(tg.FPP),NFPP=float(tg.NFPP),sec=time.time()-t0),open(f'trc/out/res_{k}.json','w'))
print(k,tg.FPP,tg.NFPP,round(time.time()-t0),flush=True)
