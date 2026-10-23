# TIC 264151965 vet (v4 GPU TESS red-dwarf search, hz-near lane)

Run 2026-10-22 on the Mac mini, in `~/Scratch/planet-hunt/v4/vet_264151965/`. Python: `hunt4/.venv` (`python -I`, `taskpolicy -a`, at most 3 threads). Input: the search's own light curve `264151965.npz` (sectors 38 and 65 SPOC PDCSAP, 99–102 QLP; flattened, 10-minute bins, 19,285 points; copied from the Spark `hz-near/lc/`) and the search result `evidence/00_search_result_v4_gpu.json`, with the pool row in `evidence/00_pool_row.csv`.

Star: M dwarf, Teff 3430 K, R 0.310 R☉, M 0.289 M☉, Tmag 10.95, 21.2 pc. Gaia DR3 5890960105080869632 (G 12.13, parallax 47.09 mas, RUWE 1.18) sits 3.0″ from the TIC position (`pix/gaia_field.csv`).

## Verdict

**Updated 2026-10-22 (section 6): candidate grade, not validated grade.** With MOLUSC bound-companion limits from Gaia (RUWE + Gaia contrast), no neighbours removed, TRICERATOPS FPP is **0.020 ± 0.009** over 10 runs (range 0.011–0.033; all 10 under 0.035, 4 of 10 under 0.015). That passes the ≤ 0.035 candidate bar and fails the ≤ 0.015 validated bar on the mean. NFPP is 7.3 × 10⁻⁵ ± 0.8 × 10⁻⁵, which passes (≤ 0.001). The remaining FPP is still STP (0.020 ± 0.009). Checks 1–4 pass.

Before MOLUSC (section 5, default companion prior): FPP 0.079 ± 0.004 over 10 runs, which failed both bars; NFPP 7.3 × 10⁻⁵ ± 0.9 × 10⁻⁵. The bullets below describe that section 5 result.

- Checks 1–4 found nothing that fails. There is one dip, about 1.16 Earth radii, every 4.8158 days. It has the same depth in odd and even transits, in every sector and in all three years (2021, 2023, 2026). There is no second dip at any phase. It is in the raw flux. The difference images put it on the target in every sector, and every other Gaia star within 150″ is ruled out.
- TRICERATOPS agrees that nearby stars are not the source: NFPP is 7 × 10⁻⁵. In section 5 the FPP failed because of the target itself. In 7.8% of the probability, the planet orbits an unseen companion star bound to the M dwarf (scenario STP). Eclipsing-binary scenarios on or behind the target are each below 2 × 10⁻⁶; eclipsing binaries on nearby stars total 6.7 × 10⁻⁵ (section 5).
- It is not a TOI or CTOI in the local snapshots up to 16 October; ExoFOP itself was down for maintenance. It is not a SPOC TCE, and not on any Eumemic candidate list. **However, Eumemic found the same 4.8158 d signal and rejected it** because a centroid offset of about 106″ was flagged. Our six-sector pixel fits do not reproduce that offset; they put the dip on the target (section 3).
- The ~0.594 d peaks are neither the star's own variability nor a second planet. [inferred] They are light from a contact binary 77″ away, blended into the aperture (section 1).

## 1. The signal itself

- [verified, `evidence/01b_box_checks.json`, `plots/01_fold_secondary_oddeven.png`] One dip every **4.815798 d** (T0 BTJD 2336.1772), **1,255 ± 66 ppm** deep in a box fit (box SNR 19.0). TLS refit over 4.80–4.83 d gives the same period, 4.815810 ± 0.000095 d, T0 2336.1772 and depth 1,282 ppm (`evidence/01a_tls_refit.json`; TLS's duration output of 0.0037 d is not physical on this narrow grid and is not used).
- [verified, `evidence/01c_transit_fit.json`, `plots/01_transit_fit.png`] Transit fit (batman + emcee, limb darkening fixed at u = 0.25, 0.35 [inferred typical M3V TESS values]):
  - Rp/R* 0.0342 (+0.0015/−0.0012), so **Rp 1.16 (+0.05/−0.04) Earth radii** with the TIC radius.
  - b 0.35 (+0.31/−0.24); no grazing solutions in the chain (0 of the samples have b > 1 − Rp/R*).
  - Duration 1.16 ± 0.05 h. The expected central-transit duration for the TIC star at this period is 1.44 h; the fitted b accounts for it.
  - Stellar density from the fit 23.7 (+5.7/−11.4) g/cc against 13.7 g/cc from the TIC: consistent at about 1σ. Fixing the density to the TIC value fits equally well (Δχ² = 0.2, b 0.63, Rp/R* 0.035, about 1.18 Earth radii).
  - The shape is U-shaped with a flat bottom in the fold; the fit puts ingress/egress at about 4 minutes each. [inferred] A V shape is not favoured, but 10-minute bins cannot rule it out on shape alone.
- [verified, `evidence/01b_box_checks.json`] Depth per sector (ppm): S38 1,323 ± 177; S65 1,023 ± 202; S99 1,281 ± 154; S100 1,134 ± 149; S101 1,298 ± 142; S102 1,465 ± 159. Per year: 2021 (S38) 1,323 ± 177; 2023 (S65) 1,023 ± 202; 2026 (S99–102) 1,293 ± 76. All within 1.3σ of the mean.
- [verified, same file, `plots/01_per_epoch.png`] 29 single transits, none negative; no single transit carries more than 10.6% of the total SNR². Scatter of single-transit depths: χ² 43.2 for 28 degrees of freedom (p = 0.033). [inferred] Slightly more scatter than the error bars, not driven by one event.
- **Secondary at every phase** [verified, same file, panel 3 of the plot]: box scan over phases 0.03–0.97 in steps of 0.0025. Strongest point is phase 0.7275 at 262 ± 71 ppm (3.7σ); 3 of 375 phases exceed 3σ, which is what noise gives over 375 trials [inferred]. At phase 0.5: −98 ± 76 ppm (nothing). No second dip anywhere near the primary's depth. This is the check that killed TIC 350933889; it passes here.
- **Odd/even** [verified]: odd 1,258 ± 93, even 1,266 ± 93 ppm, 0.06σ apart. At 2P the two halves are the same two numbers, so the true period is not 9.63 d with two equal eclipses. At P/2 the would-be other half (phase 0.5) is empty, so the period is not 2.41 d.
- **The ~0.594 d peaks** [verified, `evidence/01d_short_period.json`, `evidence/01e_short_period_neighbours.json`, `plots/01_short_period.png`]: the light curve with the 4.82 d transits masked, folded at 0.5942 d, shows three smooth waves per cycle of about ±250 ppm, not a dip. A periodogram of the same light curve peaks at **0.19816 d** (power 0.028) and **0.52390 d** (power 0.020). These match two catalogued neighbours: the contact binary ASASSN-V J142912.22-584458.1 (type EW, P 0.396213 d, 76.7″ away; an EW light curve repeats at P/2 = 0.1981 d, and 3 × 0.1981 = 0.594 d) and the Gaia DR3 RR Lyrae 5890936706111098752 (P 0.52389 d, 24.5″ away). Harmonic fits: 159 ppm at the EW's P/2, 180 ppm at the RR Lyrae's period. [inferred] The 0.594 d peaks are blended light from the contact binary, not the M dwarf and not a second planet. Eumemic's pipeline also found and failed the 0.5926 d and 0.5239 d signals on this star (see step 2). 4.8158 / 0.5942 = 8.105, so the transit is not a harmonic of either.

## 2. Is it already known?

- [verified, `evidence/02_known_checks.json`] ExoFOP target page (fetched 2026-10-22, `_sources/exofop_target_264151965.html`): **ExoFOP was down for maintenance**; the TOI and CTOI CSV endpoints returned the same page. Local TOI/CTOI snapshots from 8, 10 and 16 October 2026 (8,152 TOIs, 5,139 CTOIs): no entry for TIC 264151965. NASA Exoplanet Archive TOI and planet tables: 0 rows (`_sources/nea_*.csv`).
- [verified] SPOC TCE tables: 132 files in `hz-near/_sources/tce/`, including the S38, S65 and S1–S65 runs that had this star at 2-minute cadence: 0 hits.
- [verified, fresh clone `_sources/eumemic` at HEAD e26c507, 2026-10-21] **Not a Eumemic candidate**: 0 hits in all six `candidates*.csv`. But Eumemic **did find this exact signal and rejected it**:
  - `results_public/vetted_signals.csv.gz`: P 4.815785 d, 1,264 ppm, rank 11, 0 LEO-Vetter failures, `known_status` new.
  - `results_public/followup_kmdwarfs.csv`: flags `offset,close_nb`, offset_qual 106.5, offset_mean 87.2, nearest depth-capable star 8.2″.
  - `README.md` line 853: "It rejects TIC 264151965, which we had set aside, with a 106″ offset."
  - Step 3 below tests that offset directly.
- [verified, `evidence/02_catalogs_raw.json`] VizieR within 120″: the target is in VSX as Gaia DR3 type ROT (G 12.12–12.15, no period) and in Gaia DR3 vclassre as SOLAR_LIKE (score 0.04). It is not in Gaia DR3 eclipsing binaries or short-timescale variables. Neighbour variables: the RR Lyrae at 24.5″, two Gaia "L" (long-period) stars at 12.4″ and 18.4″ (G 17.7–18.6), the EW at 76.7″, and another Gaia eclipsing binary at 101.6″ (P 0.403 d).

## 3. Pixels: where does the dip come from?

Method copied from `tic240488148-localize/diff.py` (`glue/diff.py`, `glue/common.py`, `glue/post.py`). For each sector: a 21×21 TESScut FFI stamp; each transit measured as in-transit mean against a straight-line fit to the nearby out-of-transit data; transits stacked; per-pixel noise taken from 120 stacks at random phases. The TESS PRF (`tess_prf`) is then fitted at the target and at every Gaia DR3 star within 150″ (G < 20.5, 734 stars; 480 within 120″).

[verified, `evidence/03_pixel_summary.json`, `pix/out/diff_s*.json`, `plots/03_diff_s*.png`]

| Sector (cadence) | Transits | Dimming fitted at target (e/s) | Needed for the light-curve depth (e/s) | Free-position best fit, offset from target |
|---|---|---|---|---|
| 38 (10 min) | 6 | 7.60 ± 1.60 | 6.79 | 2.6″ |
| 65 (200 s) | 5 | 6.39 ± 2.03 | 6.93 | 70.7″ (weak, wide 1σ region) |
| 99 (200 s) | 4 | 6.55 ± 1.67 | 7.12 | 169″ (weak, wide 1σ region) |
| 100 (200 s) | 6 | 8.85 ± 1.44 | 6.79 | 5.4″ |
| 101 (200 s) | 5 | 9.22 ± 1.31 | 6.60 | 5.7″ |
| 102 (200 s) | 6 | 9.48 ± 2.38 | 6.81 | 15.1″ |

- In every sector the target shows the dimming the light curve needs, within 2σ (z from −0.3 to +2.0). Summed over six sectors, forcing the target to the required depth costs Δχ² = 21 against its best free amplitude.
- In the four sectors with the most signal (38, 100, 101, 102) the free-position fit lands 2.6–15″ from the target, inside one 21″ pixel. In S65 and S99 the free fit wanders, but the target-only fit still has the right amplitude. [inferred] With 4–6 transits per sector the free fit is noise-limited in those two.
- **Neighbours** [verified, `pix/out/neighbour_summary.csv`, `pix/out/neighbour_tests.csv`]: of the 733 other Gaia stars within 150″, 702 would need an eclipse deeper than 100% to make the signal, and the other 31 are ruled out by the pixels (forced-fit Δχ² > 25, summed over six sectors). **No star other than the target is left.** The closest cases:
  - G 18.98 at 6.4″: needs a 79% eclipse, Δχ² = 32.
  - G 18.42 at 8.9″: needs 32%, Δχ² = 59.
  - G 18.47 at 11.2″: needs 50%, Δχ² = 93.
  - G 17.57 at 14.6″: needs 23%, Δχ² = 135.
  [inferred] The 6.4″ star is the weakest exclusion: its Δχ² is only 11 worse than the target forced to its own required depth. A 79% eclipse on a G 19 star is itself unusual, and TRICERATOPS weighs it below.
- The stars near Eumemic's 87–106″ offset are ruled out by both tests. The G 11.74 star at 106.8″ needs a 36% eclipse, forced Δχ² = 2×10⁷. The Gaia eclipsing binary at 101.6″ (P 0.403 d) needs 570%. [inferred] Eumemic's centroid offset is probably pulled by bright stars about a pixel away, or by the two variables in the aperture. The difference images put the dimming on the target.
- Caveats [inferred]: the neighbour fluxes come from Gaia G and BP−RP through the TIC v8 G→T relation. The QLP apertures for S99–102 are not in the files, so a 3×3 stand-in was used there; the target test and the Δχ² comparisons do not depend on it. Gaia IDs in the `pix/` CSVs are float-rounded in their last 3–4 digits; positions and magnitudes are exact.
- All TESScut FITS were deleted after reading (`pix/cut/` removed; the TRICERATOPS cutouts in `~/.lightkurve/cache/tesscut/` for this position also removed). Only the stacked difference images remain (`pix/out/diff_s*.npz`).

## 4. SAP vs PDCSAP

[verified, `evidence/04_sap_vs_pdcsap.json`, `plots/04_sap_vs_pdcsap.png`]; same detrending (biweight 0.5 d, transits masked) for both columns.

| Sector | Raw (SAP) depth | SAP ÷ CROWDSAP | Corrected (PDCSAP / QLP DET_FLUX) |
|---|---|---|---|
| 38 (SPOC 2 min) | 915 ± 169 | 1,029 ± 190 (CROWDSAP 0.889) | 1,206 ± 159 |
| 65 (SPOC 2 min) | 940 ± 165 | 1,089 ± 191 (CROWDSAP 0.863) | 1,035 ± 189 |
| 99 (QLP) | 1,152 ± 160 | — | 1,199 ± 161 |
| 100 (QLP) | 1,135 ± 162 | — | 1,003 ± 159 |

The dip is in the raw flux in every sector, at the depth the corrected flux shows once the known crowding is divided out (all pairs within 0.7σ). It is not made by PDC or QLP detrending.

## 5. TRICERATOPS

[verified, `glue/trc_run.py`, `trc/out/stars_with_tdepth.csv`] Setup: TRICERATOPS 1.1.0, 2,129 stars within its search radius, **none removed**. 64 of them could physically produce the dip (required depth ≤ 100%); the nearest are TIC 264151972 at 8.2″ (needs 48%), TIC 1037412521 at 8.7″ (90%) and TIC 1037412516 at 12.3″ (72%). Input (from `trc/out/res_0.json`): the search light curve folded at P 4.815798 d, ±0.25 d, binned to 10 minutes (72 bins), depth 1,223 ppm, per-bin error 182 ppm. Apertures: SPOC for S38 and S65, 5×5 boxes for the QLP sectors. Settings: N = 1,000,000, nsamples 20, exptime 10 min, TESS filter, no contrast curve, seeds 1000–1009.

[verified, `evidence/05_triceratops_summary.json`, `trc/out/res_{0..9}.json`, `trc/out/probs_{0..9}.csv`; summary by `glue/trc_summary.py`]

| | Mean ± scatter (1σ, 10 runs) | Range | Bar | Result |
|---|---|---|---|---|
| FPP | **0.0789 ± 0.0039** | 0.0748–0.0868 | ≤ 0.015 validated, ≤ 0.035 candidate | **fails both** |
| NFPP | **7.3 × 10⁻⁵ ± 0.9 × 10⁻⁵** | max 8.5 × 10⁻⁵ | ≤ 0.001 | passes |

Per-run FPP: 0.0795, 0.0781, 0.0754, 0.0749, 0.0804, 0.0826, 0.0763, 0.0868, 0.0802, 0.0748. Every run is above 0.035.

Scenario probabilities (mean ± scatter over 10 runs, summed over stars):

| Scenario | Meaning | Probability |
|---|---|---|
| TP | planet on the target | 0.781 ± 0.010 |
| PTP | planet on the target, which has an unseen bound companion | 0.089 ± 0.006 |
| **STP** | **planet on an unseen bound companion of the target** | **0.078 ± 0.004** |
| DTP | planet on the target, diluted by an unseen background star | 0.051 ± 0.004 |
| BTP | planet on an unseen background star | 0.0004 ± 0.0003 |
| NEB | eclipsing binary on a nearby star | 6.7 × 10⁻⁵ |
| NTP | planet on a nearby star | 4.9 × 10⁻⁶ |
| EB, EBx2P, PEB, SEB, BEB, DEB (all variants) | eclipsing binaries on or behind the target | each < 2 × 10⁻⁶ |

- TRICERATOPS defines FPP = 1 − (TP + PTP + DTP) (`triceratops.py` line 1697); 1 − (0.781 + 0.089 + 0.051) = 0.079. **Almost the whole FPP is STP**, a planet around a companion star that the data cannot see. Eclipsing binaries contribute almost nothing.
- The largest nearby-star terms are NEB on TIC 290844767 (31.4″, Tmag 15.9, needs 17%) at 2.5 × 10⁻⁵ and TIC 290844761 (18.4″, Tmag 16.2, needs 18%) at 2.2 × 10⁻⁵. The 8.2″ star does not appear among the top terms.
- [inferred] STP is the term high-resolution imaging removes: TRICERATOPS uses a contrast curve to cap how bright an unseen companion can be. With no contrast curve, its default companion prior applies. The FPP here reflects having no imaging, not anything that failed in checks 1–4. Whether a contrast curve would bring it under 0.035 was not tested.
- Eumemic: [verified, section 2] Eumemic rejected this signal for a centroid offset of about 106″ (`followup_kmdwarfs.csv`: offset_qual 106.5). Our six-sector pixel fits put the dimming on the target and rule out every Gaia star within 150″, including the stars near 87–106″ (section 3). TRICERATOPS's NFPP of 7 × 10⁻⁵ is independent and agrees: nearby stars are very unlikely to be the source.

How it was run [verified, `glue/trc_launch_spark.sh`]: the Mac mini was at load 118–125 (`uptime`, 11:56), so the runs moved to the DGX Spark in a separate venv (`~/planet-hunt/trc_venv`; same TRICERATOPS 1.1.0, numpy 1.26.4, numba 0.68.0, pytransit 2.2.0 pins as `hunt4/.venv`). The inputs were the same `target.pkl`, light curve and box-check JSON; the Spark rebuilt `stars_with_tdepth.csv` with the same star list (IDs and Tmag identical). `~/planet-hunt/.venv` and the GPU search were not touched. The first launch ran for 3.5 hours without finishing: 94% of its CPU time was in the kernel (`/proc/<pid>/stat`: about 10,400 s system vs 670 s user per run). Sampling showed the time sat in fresh large numpy allocations (`np.full(N, …)` and array arithmetic in `marginal_likelihoods.py`). [inferred] NumPy requests huge pages for large arrays, and on the Spark (THP defrag = madvise, `compact_stall` 2.16 million in `/proc/vmstat`, swap nearly full) each request triggered memory compaction. Rerunning with `NUMPY_MADVISE_HUGEPAGE=0` (allocation only; the arithmetic and seeds are unchanged) plus `NUMBA_NUM_THREADS=1` finished each run in 731–766 s, all 10 in parallel. [inferred] The Mac mini runs stalled for a different reason: a load average of 300–530 and, before that, numba's thread pool.

## 6. TRICERATOPS with MOLUSC bound-companion limits

[verified, `glue/molusc_run.py`, `glue/molusc_all.sh`, `glue/molusc_summary.py`, `glue/trc_run_molusc.py`, `glue/trc_all_molusc.sh`, `glue/trc_molusc_summary.py`, `molusc_out/`, `trc_molusc/out/`, `evidence/07_triceratops_molusc_summary.json`] Run 2026-10-22: MOLUSC on the Mac mini 15:44–15:46 EDT, TRICERATOPS on the DGX Spark 12:47–13:00 PDT.

Same method as TIC 270573718 (`hz-wide/vet_270573718/VET.md` section 6) and the TIC 240488148 note: MOLUSC's surviving companions replace TRICERATOPS's default companion prior (`molusc_file=`). That changes only the bound-companion scenarios (PTP, PEB, PEBx2P, STP, SEB, SEBx2P).

**MOLUSC settings:**

- Code: same checkout, github.com/woodml/MOLUSC commit `b26efbf3`, same wrapper (`glue/molusc_run.py` is a byte copy of the TIC 270573718 one). Gaia queries go to VizieR I/355/gaiadr3.
- Command, seeds 11–14: `molusc_run.py --ruwe --gaia -a molusc_out/m50k_s{seed} 14h29m18.192s -- -58d45m59.04s 50000 0.289` (TIC RA 217.3258, Dec −58.7664; 50,000 companions per seed; primary 0.289 M☉; default age 5 Gyr).
- Tests: RUWE and Gaia contrast only. No RV, AO or imaging contrast curve. The log matched Gaia DR3 5890960105080869632, RUWE 1.181 (`molusc_out/m50k_s11.log`).
- **Kept fraction: 92,534 of 200,000 = 46.3%** (per seed 46.1–46.7%). RUWE rejects 18.2%, Gaia contrast rejects 37.3%. Of stellar-mass companions (m₂ ≥ 0.08 M☉), 25.9% are kept (`molusc_out/summary.txt`).
- File passed to TRICERATOPS: 462,670 rows (46.3% of N = 10⁶), resampled with `default_rng(7)` (`molusc_out/molusc_for_trc_N1e6.csv`; same MD5 on Mac and Spark, `1cd5966a…`).
- TRICERATOPS uses only rows with a(1−e) > 10 AU: **164,654 rows, 16.5% of N.** Mass ratios below 0.1/M★ = 0.347 (TRICERATOPS M★ 0.2885) are raised to 0.347; that is 148,879 of those rows (90%). Kept companions with a(1−e) > 10 AU and m₂ ≥ 0.1 M☉ are 1.6% of all generated, against 35.1% before rejection.

**TRICERATOPS:** same `target.pkl`, light curve, depth (1,223 ppm), 10-minute bins, apertures, 2,129 stars, N = 10⁶, nsamples 20, `filt='TESS'`, seeds 1000–1009 as section 5. **No neighbours removed.** The only change is `molusc_file=`. Spark venv `~/planet-hunt/trc_venv`, `NUMPY_MADVISE_HUGEPAGE=0 NUMBA_NUM_THREADS=1`, nice 10; 10 runs in parallel, 728–802 s each. `~/planet-hunt/.venv` and the GPU search were not touched.

| | Mean ± scatter (1σ, 10 runs) | Range | Bar | Result |
|---|---|---|---|---|
| FPP | **0.020 ± 0.009** | 0.0106–0.0335 | ≤ 0.015 validated, ≤ 0.035 candidate | **passes candidate (10 of 10 runs); fails validated on the mean (4 of 10 runs under 0.015)** |
| NFPP | **7.3 × 10⁻⁵ ± 0.8 × 10⁻⁵** | max 9.5 × 10⁻⁵ | ≤ 0.001 | passes |

Per-run FPP (seeds 1000–1009): 0.0152, 0.0142, 0.0106, 0.0324, 0.0109, 0.0207, 0.0335, 0.0236, 0.0138, 0.0275.

Scenario probabilities (mean ± scatter over 10 runs, summed over stars):

| Scenario | Section 5 (default prior) | Section 6 (MOLUSC) |
|---|---|---|
| TP | 0.781 ± 0.010 | 0.789 ± 0.021 |
| PTP | 0.089 ± 0.006 | 0.140 ± 0.017 |
| DTP | 0.051 ± 0.004 | 0.051 ± 0.003 |
| **STP** | **0.078 ± 0.004** | **0.020 ± 0.009** |
| BTP | 0.0004 | 0.0001 |
| NEB | 6.7 × 10⁻⁵ | 6.8 × 10⁻⁵ |
| all other EB and NTP terms | each < 2 × 10⁻⁶ | each < 4 × 10⁻⁶ |

- **The dominant remaining scenario is still STP on the target, 0.020 of the 0.020 FPP.** Every other false-positive term is under 1.3 × 10⁻⁴ (BTP 1.2 × 10⁻⁴, NEB on TIC 290844767 2.5 × 10⁻⁵, TIC 290844761 2.2 × 10⁻⁵, TIC 290844640 1.3 × 10⁻⁵).
- MOLUSC cut STP by about 4× (0.078 → 0.020). PTP rose from 0.089 to 0.140; it is a planet scenario and does not count toward FPP.
- The run-to-run scatter (0.009) is much larger than in section 5 (0.004) and comes almost entirely from STP (per-run 0.010–0.033). [inferred] With 90% of usable rows piled at the 0.347 mass-ratio floor, the STP likelihood rests on few distinct companion draws per run, so seed noise is larger. This was not isolated.
- Verdict against the bar: FPP mean 0.020 is ≤ 0.035 (candidate) and > 0.015 (validated). NFPP passes. [inferred] Reaching the validated bar on the mean would need a further cut to STP, which is what a high-resolution imaging contrast curve does; none exists here and none was used.

## Files

- `plots/01_fold_secondary_oddeven.png`: fold, full phase, secondary scan, odd/even. `plots/01_transit_fit.png`. `plots/01_per_epoch.png`. `plots/01_short_period.png`: periodograms and 0.594 d folds. `plots/03_diff_s{38,65,99,100,101,102}.png`: out-of-transit image, difference image, difference/noise (green + target, magenta × free fit). `plots/04_sap_vs_pdcsap.png`.
- `evidence/00_*`: search result and pool row. `evidence/01a–01e`: TLS, box checks, transit fit, short-period checks. `evidence/02_*`: catalogue lookups. `evidence/03_pixel_summary.json` plus `pix/out/`. `evidence/04_*`. `evidence/05_triceratops_summary.json`; `trc/out/`: TRICERATOPS per-run JSON (`res_*.json`) and probability tables (`probs_*.csv`), star list with required depths (`stars_with_tdepth.csv`, Spark copy `stars_with_tdepth_spark.csv`).
- `evidence/07_triceratops_molusc_summary.json` plus `molusc_out/` (MOLUSC logs, all/kept CSVs, `summary.txt`, `molusc_for_trc_N1e6.csv`) and `trc_molusc/out/` (`res_*.json`, `probs_*.csv`, `log_*.txt`): section 6. `glue/trc_all_molusc.sh` launches those runs on the Spark (`~/planet-hunt/trc_264151965`).
- `_sources/`: ExoFOP page (maintenance), NASA archive replies, Eumemic clone, each with a `.url` sidecar.
- `lcfits/`: only `.url` sidecars remain; the light-curve FITS were deleted after the SAP/PDCSAP and aperture steps.
- `glue/*.py`: every script (`glue/trc_launch_spark.sh` launches the 10 runs on the Spark). Run from this folder with `python -I glue/X.py`.
