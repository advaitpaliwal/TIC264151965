# Ephemeris fit for TIC 264151965.01: the same batman + emcee model as code/vet/s1_fit.py
# (quadratic LD fixed at 0.25, 0.35; free Rp/R*, b, a/R*, flux level), with the period
# also free so the posterior carries the T0-P correlation used by ephemeris.py.
# Usage: python fit_ephemeris.py 264151965.npz 01b_box_checks.json chain.npz
import sys, json, numpy as np, batman, emcee
d = np.load(sys.argv[1]); t, f = d['t'], d['f']
b1 = json.load(open(sys.argv[2])); P0 = b1['P']; T00 = b1['T0']
n_ep = np.round((t - T00)/P0)
dt = t - T00 - n_ep*P0; m = np.abs(dt) < 0.3
tt, y, ne = t[m], f[m], n_ep[m]
sig = 1.4826*np.median(np.abs(y[np.abs(dt[m]) > 0.06] - np.median(y[np.abs(dt[m]) > 0.06])))
pr = batman.TransitParams(); pr.t0 = 0; pr.per = P0; pr.rp = 0.03; pr.a = 25; pr.inc = 89.
pr.ecc = 0; pr.w = 90; pr.u = [0.25, 0.35]; pr.limb_dark = 'quadratic'
def model(p):
    dT, dP, rp, b, a, c = p
    x = tt - (T00 + dT) - ne*(P0 + dP)
    pr.rp = rp; pr.a = a; pr.inc = np.degrees(np.arccos(b/a))
    return c*batman.TransitModel(pr, x, supersample_factor=11, exp_time=10/1440).light_curve(pr)
def lnp(p):
    dT, dP, rp, b, a, c = p
    if not (-0.02 < dT < 0.02 and -1e-3 < dP < 1e-3 and 0.005 < rp < 0.5 and 0 <= b < 1+rp and 2 < a < 200): return -np.inf
    return -0.5*np.sum(((y - model(p))/sig)**2)
rng = np.random.default_rng(1); nw = 32
p0 = np.array([0, 0, 0.035, 0.3, 30, 1]) + np.array([5e-4, 5e-6, 2e-3, 0.2, 3, 1e-5])*rng.standard_normal((nw, 6)); p0[:, 3] = np.abs(p0[:, 3])
S = emcee.EnsembleSampler(nw, 6, lnp); S.run_mcmc(p0, 6000, progress=False)
ch = S.get_chain(discard=2000, thin=10, flat=True)
T0 = T00 + ch[:, 0] + 2457000.0; P = P0 + ch[:, 1]
np.savez(sys.argv[3], T0_BJD=T0, P=P, rp_rs=ch[:, 2], b=ch[:, 3], a_rs=ch[:, 4], noise=sig, n_pts=m.sum())
q = lambda v: np.percentile(v, [16, 50, 84])
print('n_pts', m.sum(), 'acc', S.acceptance_fraction.mean())
print('T0 BJD_TDB', q(T0), 'std', T0.std()); print('P', q(P), 'std', P.std())
print('corr', np.corrcoef(T0, P)[0, 1]); print('rp_rs', q(ch[:, 2]), 'b', q(ch[:, 3]))
