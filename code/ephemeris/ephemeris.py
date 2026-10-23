# Predicted mid-transit times of TIC 264151965.01, 2026-10-23 to 2027-12-31.
# Propagate every posterior sample (T0 + n*P) and take the
# median and standard deviation, so the T0-P correlation is kept.
# UTC times are geocentric: BJD_TDB minus the Roemer light-travel delay to the star, then TDB -> UTC.
# Usage: python code/ephemeris/ephemeris.py data/fit/chain.npz ephemeris.csv (chain from code/ephemeris/fit_ephemeris.py)
import sys, csv, numpy as np
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
chain, out = sys.argv[1], sys.argv[2]
c = np.load(chain, allow_pickle=True)
T0 = c['T0_BJD']; P = c['P']
STAR = SkyCoord(217.32580*u.deg, -58.76642*u.deg)  # TIC v8.2, J2000
GEO = EarthLocation.from_geocentric(0, 0, 0, unit=u.m)
T14_H = 1.16
t_start = Time('2026-10-23T00:00:00', scale='utc').tdb.jd
t_end = Time('2027-12-31T23:59:59', scale='utc').tdb.jd
t0m, pm = np.median(T0), np.median(P)
n = np.arange(int(np.ceil((t_start - t0m)/pm)) - 1, int(np.floor((t_end - t0m)/pm)) + 2)
pred = T0[None, :] + n[:, None]*P[None, :]
bjd = np.median(pred, 1); sig = pred.std(1)
def bjd_to_utc(b):
    t = Time(b, format='jd', scale='tdb', location=GEO)
    for _ in range(3):  # BJD = t + ltt(t); solve for t
        t = Time(b, format='jd', scale='tdb', location=GEO) - t.light_travel_time(STAR, 'barycentric')
        t = Time(t.jd, format='jd', scale='tdb', location=GEO)
    return t.utc
utc = bjd_to_utc(bjd)
keep = (utc.jd >= Time('2026-10-23', scale='utc').jd) & (utc.jd <= Time('2028-01-01', scale='utc').jd)
half = T14_H/48
with open(out, 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['epoch', 'mid_BJD_TDB', 'sigma_d', 'sigma_min', 'mid_UTC', 'ingress_UTC', 'egress_UTC'])
    for i in np.where(keep)[0]:
        m = utc[i]
        w.writerow([int(n[i]), '%.5f' % bjd[i], '%.5f' % sig[i], '%.1f' % (sig[i]*1440),
                    m.isot[:16], (m - half*u.day).isot[:16], (m + half*u.day).isot[:16]])
print('rows', keep.sum(), 'P', pm, 'T0', t0m, 'sigma_min range', sig[keep].min()*1440, sig[keep].max()*1440)
