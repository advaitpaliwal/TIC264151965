# GPU drop-in for the v4 star search (DGX Spark, 2026-10-20)

**Result: built and passing controls.** `run_star_gpu.py` found all 6 control planets (TOI-700 b, c, d; TOI-2094 b; TOI-2095 b, c) end to end, each as the top peak of a pass and each passed by LEO-vetter. It did **not** find LHS 1140 b (24.737 d). A star takes about 1 to 9 s of GPU search; a CPU TLS search takes 200 to 440 s (bake-off). Nothing was launched on the pool; the live CPU search, `run_star.py`, `drive.py`, `res_v4/`, `lc/` and `~/planet-hunt/.venv` were not modified. No `res_v4_gpu/` folder exists in any lane yet (checked 03:52).

## Files (on the Spark, `~/planet-hunt/v4/`)
- `run_star_gpu.py`: the GPU search for one star or a list of stars. Same light curve as `run_star.py` (lane `lc/<tic>.npz`, or the lane's `run1.py` in LC_ONLY mode, run with the live venv's Python read-only), same prep (bin30, trim, unlone), same period range (hz-near 0.5 d, others 1 d, up to min(60, span/3)), same `good_epochs` rule (ok = 3 or more), up to 4 passes masking 1.5x the expected duration. Writes `<lane>/res_v4_gpu/<tic>.json` with `settings='v4gpu'` and the same peak fields as res_v4 (P, T0, SDE, snr, depth_ppm, rp_re, exp_dur_h, good_epochs, ok, oe, S_earth), plus `nfreq`, `lc_secs`, `search_secs`, `stop`, `cand`.
- `drive_gpu.py`: one process holds the GPU and does every search; N CPU threads (default 4) build light curves ahead of it. Resumable: skips any star with `res_v4/<tic>.json` or `res_v4_gpu/<tic>.json`, checked again just before each search. It takes stars from the opposite end of each pool to `drive.py`, and interleaves the three lanes.
- `gpu_ctrl/`: control and calibration scripts and outputs (`ctrl.py`, `calib.py`, `an.py`, `leo_gpu.py`, `out_stop0/`, `out_stopdefault/`, `calib_inv/`, `calib_fwd/`, logs).

## How it differs from TLS (verified in code)
- Search: cuvarbase 0.3.0 `eebls_transit_gpu(use_fast=True, ignore_negative_delta_sols=True)` on a `transit_autofreq` grid (stellar density M/R^3, duration 0.5x to 2x Keplerian), 2 samples per peak (3 on hz-near, mirroring TLS oversampling 2 and 3). SDE = (power - mean) / std of the spectrum.
- The fast kernel gives no epoch, depth or odd-even, so: T0 from the bake-off phase fold (`fold_t0`, resolution a quarter of the expected duration); depth, snr and odd-even from a box at that T0 with the expected duration; rp_re = sqrt(depth) x R. These are box estimates, not TLS model fits.
- GPU out-of-memory: cuvarbase grabs the GPU when it is imported (`pycuda.autoprimaryctx`, cuvarbase/bls.py line 15), so the import is retried every 10 s for up to an hour; a search that hits out-of-memory is retried every 10 s up to 120 times. The first version used `make_context` and failed on all 21 stars with "make_default_context() wasn't able to create a context" (gpu_ctrl/calib.log, first run); the import-retry version opened on the first try in every run since.

## Score calibration (inverted flux, 20 already-searched pool stars)
Flux flipped (f -> 2-f), all 4 passes forced (stop 0), 7 hz-north, 7 hz-south, 6 hz-near stars (`gpu_ctrl/calib_inv/`, summary from `an.py`).
- Top score of the first pass: median 9.84, **95th percentile 20.42, maximum 21.70**.
- All 80 pass scores: median 8.56, 95th percentile 20.36, maximum 21.70.
- The tail comes from three stars: 20305594 (0.581 d, 21.7), 350432766 (1.621 d, 20.3), 367279806 (50.66 d, 18.7). The other 17 sit at 7.4 to 12.4. Inference: short-period spots or variability on those stars make dips once the flux is flipped.
- **Set: stop threshold 20.4 (95th percentile), candidate threshold 21.7 (maximum).** These are the defaults in `run_star_gpu.py` (override with `GPU_STOP` / `GPU_CAND`). The TLS equivalent was 9.
- Consequence (measured): with stop 20.4, most stars end after one pass. In the drive test all 6 stars stopped after pass 1 (scores 10.2 to 19.7). A second planet behind a weak first peak is never searched; this is what hides LHS 1140 c (below).

Same 20 stars un-inverted, against their TLS res_v4 first peak (`gpu_ctrl/calib_fwd/`): the GPU's top period matched TLS's (within 1%) on 6 of 20 (219763889 10.320 d; 279161271 56.91; 350095895 47.75; 350432766 47.17; 149423103 58.84; 20305594 0.581). The rest differ, all with TLS SDE 7.5 to 15.4, i.e. near the noise floor on both scales.

## Controls (stop 20.4, one process, `gpu_ctrl/out_stopdefault/`, `ctrl_default.log`)
| star | pass: P (d) / score / good epochs | known planets | found? |
|---|---|---|---|
| TOI-700 | 0: **16.0511** / 198.9 / 35; 1: **9.9772** / 58.1 / 70; 2: **37.4234** / 45.0 / 19; 3: 27.8099 / 19.5 / 22 | c 16.0512, b 9.9773, d 37.4246 | all 3 |
| TOI-2094 | 0: **18.7932** / 45.9 / 36; 1: 8.4417 / 9.3 / 83 | b 18.7933 | yes |
| TOI-2095 | 0: **17.6647** / 43.8 / 43; 1: **28.1722** / 43.1 / 29; 2: 54.5611 / 10.3 / 7 | b 17.6648, c 28.1723 | both |
| LHS 1140 (hz-near settings, 0.5 to 60 d) | 0: 59.7816 / 12.6 / 3, then stop | b 24.737, c 3.778 | **no** |

- All 6 planets score 43 to 199, well above the candidate threshold 21.7; all have ok = True.
- LHS 1140: b is not found. With all 4 passes forced (`out_stop0/92226327.json`) the passes are 59.78 (12.6), **3.7779 (37.1, 10 good epochs; this is LHS 1140 c)**, 7.62 (9.7), 3.71 (7.7); b never appears. The light curve has 3 sectors (3, 30, 107) over 2,904 days, 8,776 points. Inference: b's few transits are mostly not in those sectors, the known limit. With the default stop 20.4 the search ends after the 12.6 first peak, so c is not reached either.
- LEO-vetter, run with gate.py's own glue (`leo_glue.py`, unchanged) on the GPU P and T0 and the v4 expected duration (`gpu_ctrl/leo_gpu.py`, `leo_gpu.log`): all 6 known planets **PC** (MES 10.2 to 31.5). TOI-2094 8.44 d and TOI-2095 54.56 d FAIL. TOI-700 27.81 d (score 19.5) and LHS 1140 59.78 d (score 12.6, 3 good epochs) were also returned PC; both are below the 21.7 candidate threshold.

## Time
- Per star, GPU search only, stop 0 (all 4 passes), 20 pool stars: hz-north median 4.3 s (max 7.4), hz-south 7.0 s (max 9.0), hz-near 9.9 s (max 15.2) (`an.py`). LHS 1140 54.9 s (1.83 million frequencies; its span is 2,904 d).
- Per star at the default stop: TOI-700 8.9 s, TOI-2094 3.0 s, TOI-2095 3.4 s, LHS 1140 4.3 s; whole 4-star process 20.3 s including start-up and GPU open (`ctrl_default.log`).
- Light-curve build (MAST download + lane run1), into scratch copies of the lanes: hz-north 326258961 11.4 s, hz-near 325052944 8.6 s, LHS 1140 21.0 s (`/tmp/lcb.log`).
- `drive_gpu.py` end to end on a scratch tree (`/tmp/dg`, 7 stars: 3 with saved light curves, 3 downloaded, 1 already in res_v4): 6 searched, 1 skipped, 41.2 s total including start-up; searches 0.9 to 4.8 s; a rerun found 0 to do (resume works).
- **Remaining (stars without res_v4/<tic>.json, 03:52):** hz-north 832 (827 need a download), hz-south 996 (990), hz-near 924 (906); **2,752 total, 2,723 need a download.**
- Projection (inference from the numbers above): downloads dominate. At about 14 s per build and 4 build threads, about 3.5 s per star, so **about 2.5 to 3 hours** for all 2,752, if MAST and the CPU keep pace. The GPU part alone is about 1 to 5 s per star (one pass at stop 20.4), about 1.5 to 3 hours if it were the bottleneck. For comparison the CPU search at 200 to 440 s per star on 15 workers is roughly 10 to 22 hours for the same stars.

## Things to know before launching
- The live `drive.py` built its to-do list at start and does not look at `res_v4_gpu/`; once the two meet in the middle of a pool, those stars get searched by both (the GPU result is not overwritten, the CPU result lands in res_v4). `drive_gpu.py` skips res_v4 stars as they appear.
- The light-curve builds run the lane `run1.py` on the CPU, which is already at load 24 to 26 on 20 cores from the 15 TLS workers.
- **LEO gate:** not a one-line change, so `gate.py` was not touched. It needs: (1) the glob at line 36 to also read `res_v4_gpu/*.json`; (2) the score cut `p['SDE']>=9` (line 16) to be 21.7 for `settings=='v4gpu'` (else nearly every GPU first peak is vetted); (3) a different cache key for GPU peaks (`cache/{lane}_{tic}_{iter}.json` would collide when a star is in both folders). Its inputs otherwise match: `res_v4_gpu` has P, T0, R, M, Teff and the same peak fields, and the vetting itself works on GPU peaks (above).

## Launch command (not run)
```
cd ~/planet-hunt/v4 && PATH=/usr/local/cuda/bin:$PATH OMP_NUM_THREADS=1 nohup nice -n 5 ../gpu_bakeoff/.venv/bin/python -I drive_gpu.py --prefetch 4 hz-north hz-south hz-near > drive_gpu.log 2>&1 & echo $! > drive_gpu.pid
```
