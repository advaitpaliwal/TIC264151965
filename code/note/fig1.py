# Figure 1 for the TIC 264151965 note. Usage: python -I fig1.py <npz> <01b_box_checks.json> <01c_transit_fit.json> <out.png>
import sys, json, numpy as np, batman
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

d = np.load(sys.argv[1]); t, f, s = d['t'], d['f'], d['s']
box = json.load(open(sys.argv[2])); fit = json.load(open(sys.argv[3]))
P, T0 = box['P'], box['T0']                            # box-refined ephemeris, as in s1_fit.py
rp, b, a = fit['rp_rs'][1], fit['b'][1], fit['a_rs'][1]  # posterior medians of the free fit

def model(x):
    pr = batman.TransitParams(); pr.t0 = 0; pr.per = P; pr.rp = rp; pr.a = a
    pr.inc = np.degrees(np.arccos(b/a)); pr.ecc = 0; pr.w = 90; pr.limb_dark = 'quadratic'; pr.u = fit['LD_fixed']
    return batman.TransitModel(pr, x, supersample_factor=11, exp_time=10/1440).light_curve(pr)

dt = (((t-T0)/P+0.5) % 1 - 0.5) * P
ep = np.round((t-T0)/P).astype(int)
ppt = lambda y: (y-1)*1e3

def binned(x, y, w):
    e = np.arange(x.min(), x.max()+w, w); i = np.digitize(x, e)
    k = [k for k in range(1, len(e)) if (i == k).sum() > 2]
    return (np.array([(e[j-1]+e[j])/2 for j in k]), np.array([np.mean(y[i == j]) for j in k]),
            np.array([np.std(y[i == j])/np.sqrt((i == j).sum()) for j in k]))

fig = plt.figure(figsize=(7.5, 9.6))
gs = fig.add_gridspec(4, 4, height_ratios=[1.25, 0.9, 0.8, 0.9], hspace=0.55, wspace=0.35)
ink, grey, accent = 'k', '0.75', '#c4552b'
xm = np.linspace(-0.25, 0.25, 800)

ax = fig.add_subplot(gs[0, :]); w = np.abs(dt) < 0.25
ax.plot(dt[w]*24, ppt(f[w]), '.', color=grey, ms=2, zorder=1)
c, m, r = binned(dt[w], f[w], 10/1440)
ax.errorbar(c*24, ppt(m), r*1e3, fmt='o', color=ink, ms=3, lw=0.8, zorder=3)
ax.plot(xm*24, ppt(model(xm)), '-', color=accent, lw=1.4, zorder=4)
ax.set_xlim(-6, 6); ax.set_ylim(-3, 1.5); ax.set_xlabel('Hours from mid-transit'); ax.set_ylabel('Relative flux (ppt)')
ax.set_title(f'(a) 6 sectors folded on P = {P:.6f} d, 10-min bins', fontsize=9, loc='left')

ax = fig.add_subplot(gs[1, :]); sel = s == 101
c, m, r = binned(t[sel], f[sel], 30/1440)
ax.plot(c, ppt(m), '.', color=ink, ms=2.5)
for e in sorted(set(ep[sel])):
    tt = T0+e*P
    if t[sel].min() < tt < t[sel].max(): ax.axvline(tt, color=accent, lw=0.8, ymin=0.9, ymax=1.0)
ax.set_ylim(-4, 3); ax.set_xlabel('Time (BJD$_{\\rm TDB}$ $-$ 2457000)'); ax.set_ylabel('Rel. flux (ppt)')
ax.set_title('(b) Sector 101, unfolded, 30-min bins; ticks mark predicted transits', fontsize=9, loc='left')

for k, e in enumerate([367, 368, 370, 371]):
    ax = fig.add_subplot(gs[2, k]); x = t-(T0+e*P); w = np.abs(x) < 0.25
    c, m, r = binned(x[w], f[w], 30/1440)
    ax.plot(x[w]*24, ppt(f[w]), '.', color=grey, ms=2)
    ax.plot(c*24, ppt(m), 'o', color=ink, ms=2.5)
    ax.plot(xm*24, ppt(model(xm)), '-', color=accent, lw=1)
    ax.set_xlim(-6, 6); ax.set_ylim(-4.5, 3)
    ax.set_title(f'(c) epoch {e}, S{int(np.median(s[w]))}', fontsize=8, loc='left'); ax.set_xlabel('Hours', fontsize=8)
    ax.tick_params(labelsize=7)
    if k == 0: ax.set_ylabel('Rel. flux (ppt)', fontsize=8)

ax = fig.add_subplot(gs[3, :2]); w = np.abs(dt) < 0.25
for sel, col, lab, off in [(ep % 2 == 1, ink, 'odd', 0), (ep % 2 == 0, accent, 'even', 0.05)]:
    c, m, r = binned(dt[w & sel], f[w & sel], 20/1440)
    ax.errorbar(c*24+off, ppt(m), r*1e3, fmt='o', color=col, ms=3, lw=0.8, label=lab)
ax.set_xlim(-6, 6); ax.set_ylim(-3, 1.5); ax.legend(fontsize=7, frameon=False, loc='lower right')
ax.set_xlabel('Hours from mid-transit'); ax.set_ylabel('Rel. flux (ppt)')
ax.set_title('(d) odd and even transits', fontsize=9, loc='left')

ax = fig.add_subplot(gs[3, 2:]); d5 = (((t-T0-P/2)/P+0.5) % 1 - 0.5)*P; w = np.abs(d5) < 0.25
ax.plot(d5[w]*24, ppt(f[w]), '.', color=grey, ms=2)
c, m, r = binned(d5[w], f[w], 20/1440)
ax.errorbar(c*24, ppt(m), r*1e3, fmt='o', color=ink, ms=3, lw=0.8)
ax.set_xlim(-6, 6); ax.set_ylim(-3, 1.5); ax.set_xlabel('Hours from phase 0.5')
ax.set_title('(e) phase 0.5', fontsize=9, loc='left')

fig.savefig(sys.argv[4], dpi=200, bbox_inches='tight')
print('model depth ppm', (1-model(np.array([0.0]))[0])*1e6, 'epochs in S101', sorted(set(ep[s == 101])))
