# LEO-vetter as the v4 candidate gate (2026-10-20)

**Result: LEO-vetter passed all 4 known planets and failed all 23 known artifacts, so it is now the gate.** `gate.py` runs it on every v4 peak with ok==True and SDE>=9 and writes `candidates.csv`. Gate counts so far (338 of 664 peaks vetted, 0 pass) are in section 4; the rest is still running.

Nothing in `res_v4/`, `summary.csv`, `drive.py` or the running search was touched. At most 2 Python processes, 1 thread each, under `taskpolicy -a`.

## 1. What LEO-vetter is (verified)
- Code: https://github.com/mkunimoto/LEO-Vetter, commit 26c6656 (2026-07-29), version 1.2.0, GPL-3.0. Installed unchanged into `hunt4/.venv` with `uv pip install` (the venv has no pip).
- Paper: Kunimoto et al. 2025, AJ 170, 280, **arXiv 2509.10619**. The id in the brief, 2502.07953, is an unrelated plasma-physics paper (checked on arxiv.org). Saved: `_sources/arxiv_2509.10619.html` (+ `.txt`, `.url`), `_sources/leo_README.md`, `_sources/leo_thresholds_v1.2.0.py` (+ `.url`).
- It was built for exactly our case: the paper ran it on ~200,000 TESS M-dwarf light curves and cut ~20,000 detections to 172 candidates, with 91% of injected planets kept and 99.91% of simulated false alarms rejected (paper abstract and section VI.1).
- It runs 13 "false alarm" tests (noise, systematics, star variability) and 4 "false positive" tests (eclipsing binaries). Pass = pass all 17. A fifth false-positive test (off-target, from pixel difference images) needs TESS pixel cutouts; **not run**, so a pass here is flux-level only.
- Thresholds: the repo's defaults in `leo_vetter/thresholds.py`, used as shipped. Nothing was changed. Two repo defaults differ from the paper text: asymmetry fails at ASYM > 8 in the repo vs > 10 in the paper (section III.5), and single-event fails at max SES/MES > 0.8 in the repo vs > 0.88 in the paper (section III.11). The repo values are stricter in both; I kept them.

## 2. What we feed it (glue: `leo_glue.py`)
- Light curve: the searched, flattened `<lane>/lc/<tic>.npz`, prepared exactly like `run_star.py`: 30-min binning, 0.375 d gap-edge trim, lone-low-point drop (imported from `edgefix/v4_test.py` and `edgefix/fix_test.py`). For peak k of a star, the earlier peaks are masked out (1.5 x expected duration) as the search did before finding peak k.
- Period and T0: the TLS values from `res_v4/<tic>.json`.
- Duration: the v4 expected central-transit duration (`tdur` in `v4_test.py`, from period and star size and mass). TLS's own duration is not stored in `res_v4` and the v4 code already distrusts it. See section 3.1 for why this matters.
- Things LEO wants that we do not have, and what stands in (inferred to be harmless, not tested):
  - Per-point flux errors: not saved in the npz files. Used the robust scatter (1.4826 x median absolute deviation) of each data stretch. LEO's SNR uses its own red-noise estimate on top (paper eq. 2).
  - Raw (undetrended) flux: not saved. Passed the detrended flux. In LEO 1.2.0 the raw flux is only stored and drawn in plots; no test reads it (`grep raw` over the package).
  - Star errors and density: pool.csv has R, M, Teff, logg but no errors. Used 10% on R and M and 100 K on Teff; density from M/R^3. These only set error bars on derived numbers (planet radius etc.), not pass/fail, except through Rp in the "large" (>22 Earth radii) test.
  - Limb darkening: LEO's own `quadratic_ldc(Teff, logg)`.

## 3. Controls (`control.py`, results in `control_planets.csv`, `control_artifacts.csv`, per-signal metrics in `cache/`)

### 3.1 Known planets: 4 of 4 PASS
P and T0 come from a narrow TLS run (period +-0.1%) on the v4-prepared light curve, with planets found earlier in the v4 search order masked first (for TOI-700 d: c and 9.98 d masked, as the v4 control log `edgefix/toi700_v4.log` found them first). Each was vetted twice: with TLS's duration and with the v4 expected duration.

| Planet | P (d) | duration fed (h) | LEO | failing tests | MES | transits kept |
|---|---|---|---|---|---|---|
| TOI-700 c | 16.0511 | 2.58 (v4) | **PASS** | - | 31.6 | 34 of 36 |
| TOI-700 d | 37.4237 | 3.42 (v4) | **PASS** | - | 11.7 | 16 of 20 |
| TOI-2094 b | 18.7931 | 2.54 (v4) | **PASS** | - | 9.9 | 28 of 36 |
| TOI-2095 b | 17.6649 | 2.84 (v4) | **PASS** | - | 17.4 | 40 of 44 |
| TOI-700 d, TLS duration | 37.4237 | 0.79 (TLS) | FAIL | weak, invalid_transits, bad_fit, chi | 5.2 | 1 of 19 |

Why TOI-700 d fails with TLS's duration (verified): TLS reported 0.79 h, but the catalogue duration is 3.37 h (TOI 700.02 in `deep/259541182/catalogue/raw/toi_all.csv`). LEO measures each transit inside a box of the given width, so a box a quarter of the transit's width catches little signal: MES fell to 5.2 (fails "weak", MES < 6.2), and LEO's per-transit checks then threw out 18 of 19 transits (fails "invalid_transits"). With the v4 duration (3.42 h, close to the catalogue's 3.37 h) it passes everything. No threshold was changed; the fix is the input, and gate.py always uses the v4 duration. The other three planets pass with either duration.

### 3.2 Known artifacts: 23 of 23 FAIL
Each star from `v4/vet1/stars.csv` run through gate.py's own code on its matching `res_v4` peak.

| TIC (lane) | P (d) | failing tests |
|---|---|---|
| 219088697 (N) | 1.134 | non_unique, unphysical_duration, secondary |
| 219753277 (N) | 1.083 | non_unique, unphysical_duration, secondary |
| 229611275 (N) | 1.162 | non_unique, bad_fit, unphysical_duration |
| 233077261 (N) | 1.157 | non_unique, bad_fit, chi, secondary |
| 229743976 (N) | 1.585 | non_unique, bad_fit, chi |
| 289622682 (N) | 4.574 | non_unique, bad_fit, unphysical_duration |
| 232602264 (N) | 1.059 | non_unique, bad_fit, sinusoidal, unphysical_duration, chi |
| 229674997 (N) | 1.288 | non_unique, bad_fit, sinusoidal, unphysical_duration, chi, secondary |
| 452465896 (near) | 59.860 | invalid_transits, chases, dmm, single_event, bad_fit, chi, odd_even, secondary |
| 350740953 (S) | 54.346 | invalid_transits, dmm, single_event, bad_fit, chi |
| 402104884 (near) | 56.661 | invalid_transits, chases, bad_fit, odd_even |
| 33864370 (S) | 48.623 | weak, invalid_transits, non_unique, dmm, bad_fit, chi, odd_even |
| 274545692 (near) | 49.062 | weak, invalid_transits, non_unique, chases, dmm, single_event, bad_fit, chi, data_gapped |
| 279055634 (S) | 58.323 | invalid_transits, dmm, bad_fit, unphysical_duration, chi, odd_even |
| 467254810 (near) | 59.478 | weak, invalid_transits, non_unique, dmm, single_event, bad_fit, chi, secondary |
| 300086257 (S) | 54.335 | invalid_transits, non_unique, dmm, bad_fit, chi, secondary |
| 389962392 (N) | 51.922 | weak, invalid_transits, non_unique, dmm, single_event, bad_fit, unphysical_duration, chi |
| 33839044 (S) | 57.866 | invalid_transits, dmm, chi |
| 349196599 (S) | 46.587 | invalid_transits, non_unique, dmm, chi, odd_even |
| 350862484 (S) | 39.956 | invalid_transits, dmm, chi, odd_even |
| 278777358 (S) | 28.245 | invalid_transits, dmm, chi |
| 300445381 (S) | 41.647 | invalid_transits, dmm, bad_fit, chi, secondary |
| 167719995 (S) | 40.496 | invalid_transits, dmm, chi, odd_even |

What the test names mean, in plain words:
- **non_unique**: the dip is not clearly deeper than other dips found elsewhere in the folded light curve.
- **unphysical_duration**: the dip is too long for a planet at that period (typical of a smooth brightness wave).
- **secondary**: there is a second dip (or bump) half an orbit later, as an eclipsing star or a wave would give.
- **sinusoidal**: a sine wave at the period fits strongly (only checked below 10 d).
- **bad_fit**: a planet transit shape does not beat a straight line by enough.
- **chi**: the single transits do not have consistent strength.
- **dmm**: mean depth and median depth disagree, i.e. a few deep events carry it.
- **single_event**: one event carries most of the signal.
- **invalid_transits**: after LEO drops transits that look bad individually (gap edges, missing data, odd shapes), fewer than 3 transits or too little signal is left.
- **chases**: individual events do not stand out from the nearby light curve.
- **odd_even**: odd and even transits have different depths.
- **weak**: total signal-to-noise (MES) below 6.2.
- **data_gapped**: half or more of the transits sit next to data gaps.

How this matches vet1 (verified against `v4/vet1/VET.md`): the 8 brightness-wave stars all fail on wave signatures (non_unique, unphysical_duration, secondary, sinusoidal); the 15 long-period stars all fail on "a few odd events carry it" (invalid_transits in all 15, dmm in 14, chi in 14, single_event in 5). LEO reached vet1's verdicts by its own tests, without being told the vet1 reasons.

## 4. Gate run on current v4 results
Status at 00:39 on 2026-10-20 (partial; the run is still going, see below).

- Peaks that qualify (ok==True, SDE>=9, every `res_v4/*.json` at run time): **664** (hz-north 182, hz-south 190, hz-near 292).
- Vetted so far: **338**, LEO passes: **0**, fails: 338, errors: 0. By lane: hz-north 182 of 182 vetted, 0 pass; hz-south 152 of 190 vetted, 0 pass; hz-near 4 of 292 vetted, 0 pass.
- Still to vet: 326, listed in `pending.csv`. Two shards (`gate.py --shard 0/2`, `1/2`) are still running (they stalled at 0% CPU from 00:38 to 00:47 and were restarted at 00:48) at about 10 peaks a minute, so about 30-35 more minutes. `finalize.sh` waits for both and then runs `gate.py --from-cache`, which rewrites `candidates.csv`, `all_peaks.csv` and `pending.csv`; it logs to `finalize.log`. Re-running `gate.py` with no flags vets anything new (it skips cached peaks).
- `candidates.csv` currently has the header and no rows.

How often each test failed among the 338 vetted (one peak can fail several): chi 321, non_unique 286, bad_fit 259, invalid_transits 227, weak 220, dmm 151, unphysical_duration 76, single_event 37, odd_even 36, secondary 31, sinusoidal 9, chases 6, vshaped 4, data_gapped 2, asymmetric 1, large 1.

Closest misses (failed exactly one test), verified from `all_peaks.csv` and `cache/`:
| lane | TIC | peak | P (d) | SDE | Rp (Re, TLS) | failed |
|---|---|---|---|---|---|---|
| hz-south | 140997853 | 1 | 1.5268 | 57.5 | 3.56 | sinusoidal |
| hz-south | 149450584 | 0 | 12.6677 | 10.3 | 1.01 | chi |
| hz-south | 220473814 | 0 | 4.8792 | 19.6 | 0.92 | chi (CHI 4.6 vs threshold 7.8; MES 6.5) |
| hz-south | 294399648 | 2 | 2.1488 | 11.1 | 0.58 | chi |

Run speed note (verified): early peaks took 5-35 s; around 00:00-00:10 some hz-south peaks took 50-393 s while each process got only ~20% of a CPU (`ps`), with `mediaanalysisd` using ~99% of a core (`top`). After a restart at 00:12 each shard got ~99% of a CPU and throughput was 42 peaks in 4 minutes.

## 5. Files
- `leo_glue.py`: light-curve prep, error estimate, star dict, call into LEO-vetter, pass/fail list.
- `gate.py`: the gate. `gate.py` with no flags uses the cache and writes `candidates.csv` (LEO passes only) and `all_peaks.csv` (every gated peak with verdict and failing tests). `--shard I/N` only fills the cache, for running 2 processes. Cache: `cache/<lane>_<tic>_<iter>.json` (verdict, failing tests, all LEO metrics). A peak is not re-vetted if its cache file exists; delete it if that star's res_v4 changes.
- `control.py planets|artifacts`: the controls; logs `control_planets.log`, `control_artifacts.log`.
- Cost: 5-35 s per peak on 1 thread when the machine is not busy.
- `finalize.sh`: waits for the shards, then writes the CSVs from the cache.
- `pending.csv`: peaks not yet vetted.

## 6. Limits (inferred unless marked)
- Flux-level only; the off-target pixel test was not run. A pass does not rule out a nearby eclipsing star.
- 4 planet controls is a small check of completeness; the paper's 91% figure comes from injections, which we did not redo.
- Our TLS T0 and the v4 duration are fed as is; LEO fits its own transit model but does not re-search the period.
