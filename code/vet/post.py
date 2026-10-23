# Neighbour test per sector (method of tic240488148-localize/post.py): for every Gaia star within 150" (G<20.5) compute the e/s drop it would need
# at its own position to make the light-curve depth, then the forced-fit chi2 against the difference image vs the target-only fit.
import warnings; warnings.filterwarnings('ignore')
import sys, json, glob, numpy as np, pandas as pd
sys.path.insert(0,'glue'); from common import *
DEPTH=json.load(open('evidence/01b_box_checks.json'))['depth_ppm']*1e-6
def tmag(r):  # Stassun+2019 TIC v8 G->T relation; G-0.43 when no colour (inferred)
    c=r.BPmag-r.RPmag
    return r.Gmag-0.00522555*c**3+0.0891337*c**2-0.633923*c+0.0324473 if np.isfinite(c) else r.Gmag-0.43
def main():
    from PRF import TESS_PRF
    from astropy.io import fits
    rows=[]; summ=[]
    for s in map(int,sys.argv[1:]):
        tpf=tpf_for(s); z=np.load(f'pix/out/diff_s{s}.npz'); D,sig,oot=z['D'],z['sig'],z['oot']; ny,nx=D.shape
        prf=TESS_PRF(tpf.camera,tpf.ccd,s,tpf.column+nx/2,tpf.row+ny/2)
        g=gaia_field(tpf); g=g[(g.sep<150)&(g.Gmag<20.5)].reset_index(drop=True); g['T']=g.apply(tmag,axis=1)
        w=1/sig.ravel()**2
        def lin(models,img,W):
            A=np.vstack([m.ravel() for m in models]+[np.ones(img.size)]).T
            C=np.linalg.inv(A.T@(A*W[:,None])); b=C@(A.T@(img.ravel()*W)); r=img.ravel()-A@b
            return b,np.sqrt(np.diag(C)),float((r**2*W).sum())
        t0=g.iloc[0]; mT=prf.locate(t0.x,t0.y,(ny,nx))
        bT,_,_=lin([mT],oot,1/(np.abs(oot.ravel())+100)); FT=bT[0]
        bD,eD,c2T=lin([mT],D,w)
        fn=glob.glob(f'lcfits/*s{s:04d}-*_lc.fits'); crowd=1.0; ap=np.zeros((ny,nx),bool)
        if fn:
            with fits.open(fn[0]) as h:
                a=h['APERTURE'].data.astype(int); c0=h['APERTURE'].header['CRVAL1P']; r0=h['APERTURE'].header['CRVAL2P']; crowd=h[1].header.get('CROWDSAP',1.0)
            rr,cc=np.nonzero(a&2)
            for R_,C_ in zip(rr+r0-tpf.row,cc+c0-tpf.column):
                if 0<=R_<ny and 0<=C_<nx: ap[R_,C_]=True
            apsrc='SPOC'
        else:
            cx,cy=int(round(t0.x)),int(round(t0.y)); ap[cy-1:cy+2,cx-1:cx+2]=True; apsrc='3x3 (QLP aperture not in file; inferred)'
        fT=mT[ap].sum(); dF_ap=DEPTH*FT*fT; Areq_T=dF_ap/fT  # light-curve depth is already deblended (SPOC CROWDSAP / QLP dilution), so the target must drop DEPTH*FT; a neighbour must remove the same e/s from the aperture
        summ.append(dict(sector=s,ap=apsrc,npix=int(ap.sum()),crowdsap=crowd,FT=FT,A_req_target=Areq_T,A_target=bD[0],A_target_err=eD[0],z_target=(bD[0]-Areq_T)/eD[0]))
        print('S',s,apsrc,'npix',ap.sum(),'crowd',round(crowd,3),'A_req target',round(Areq_T,2),'fit',round(bD[0],2),'+-',round(eD[0],2),flush=True)
        for i,r in g.iterrows():
            if not (-0.5<r.x<nx-0.5 and -0.5<r.y<ny-0.5): continue
            m=prf.locate(r.x,r.y,(ny,nx)); fk=m[ap].sum(); Fk=FT*10**(-0.4*(r['T']-g['T'][0]))
            if fk<=1e-6: continue
            Areq=dF_ap/fk; b,e,c2=lin([m],D,w)
            res=D.ravel()-Areq*m.ravel(); c2req=float(((res-np.median(res))**2*w).sum())
            rows.append(dict(sector=s,source=int(r.Source),Gmag=r.Gmag,Tmag_est=r['T'],sep=r.sep,pa=r.pa,depth_req=Areq/Fk,A_req=Areq,A_fit=b[0],A_err=e[0],
                             dchi2_free=c2-c2T,dchi2_forced=c2req-c2T))
    df=pd.DataFrame(rows); df.to_csv('pix/out/neighbour_tests.csv',index=False); pd.DataFrame(summ).to_csv('pix/out/target_amp.csv',index=False)
    agg=df.groupby('source').agg(Gmag=('Gmag','first'),sep=('sep','first'),depth_req=('depth_req','median'),dchi2_forced=('dchi2_forced','sum'),dchi2_free=('dchi2_free','sum'),nsec=('sector','count')).reset_index()
    agg['verdict']=np.where(agg.depth_req>1,'cannot (needs >100% eclipse)',np.where(agg.dchi2_forced>25,'ruled out by pixels','NOT excluded'))
    agg.sort_values('sep').to_csv('pix/out/neighbour_summary.csv',index=False)
    pd.set_option('display.width',250); print(pd.DataFrame(summ).round(2).to_string()); print(agg.sort_values('sep').round(3).head(40).to_string()); print(agg.verdict.value_counts())
if __name__=='__main__': main()
