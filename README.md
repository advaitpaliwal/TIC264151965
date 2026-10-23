# TIC 264151965.01: a 1.16 Earth-radius, 4.82-day transiting planet candidate at 21 pc

Discovered by Advait Paliwal on 2026-10-20 in public TESS photometry (search result written 2026-10-20 06:25 PDT, `data/search/264151965_search_result.json`).

## Summary

TIC 264151965 (Gaia DR3 5890960105080869632) is an M dwarf (Teff 3430 K, 0.310 R☉, 0.289 M☉) at 21.2 pc. TESS light curves from Sectors 38 and 65 (SPOC 2-minute) and 99 to 102 (QLP full-frame images), spanning 2021 to 2026, show 29 transits with period 4.815798 d, depth 1,255 ± 66 ppm and duration 1.16 h, which implies a radius of 1.16 (+0.05 / −0.04) Earth radii and an insolation of 8.8 times Earth's. Odd and even depths agree, there is no secondary eclipse, the dip is in the raw (SAP) flux, and difference images in all six sectors place it on the target and rule out every Gaia star within 150″ brighter than G = 20.5. As of 2026-10-16 the star is not a TOI or a CTOI, and it is not a NASA Exoplanet Archive host or a SPOC TCE.

**This is a planet candidate, not a validated or confirmed planet.** The TRICERATOPS false-positive probability is 0.079 ± 0.004 (NFPP 7 × 10⁻⁵) without companion limits, and 0.020 ± 0.009 with Gaia companion limits from MOLUSC (Wood, Mann & Kraus 2021, AJ 162, 128). No neighbours were removed in either run. Both values are above the 0.015 threshold for statistical validation, and almost all of the remaining probability is a planet orbiting an unresolved bound companion. There is no high-resolution imaging of this star.

Eumemic (2026), https://github.com/eumemic/exoplanets (commit e26c507), found the same 4.8158 d signal and rejected it because their highest-quality difference-image centroid lay 106.5″ from the target (`results_public/followup_kmdwarfs.csv`, flags `offset,close_nb`; README: "It rejects TIC 264151965, which we had set aside, with a 106″ offset."). Our six-sector pixel fits put the dip on the target: the fitted flux loss at the target matches the light-curve depth in every sector (z = −0.3 to 2.0), and forcing the signal onto the G = 11.74 star at 106.8″ needs a 36% eclipse and gives Δχ² = 2 × 10⁷. A free-position fit lands 2.6″ to 15″ from the target in four sectors, and 71″ and 169″ away in Sectors 65 and 99, which have 5 and 4 transits.

| | |
|---|---|
| Star | TIC 264151965, RA 217.32580°, Dec −58.76642° (J2000), Tmag 10.95, G 12.13 |
| Period | 4.8157979 ± 0.0000050 d |
| Mid-transit (T0) | BJD_TDB 2459336.1785 ± 0.0015 |
| Depth | 1,255 ± 66 ppm |
| Duration | 1.16 (+0.05 / −0.04) h |
| Radius | 1.16 (+0.05 / −0.04) R⊕ |
| Insolation | 8.8 S⊕ |
| False-positive probability | 0.079 ± 0.004 (no companion limits), 0.020 ± 0.009 (MOLUSC Gaia limits); no neighbours removed |
| High-resolution imaging | none |

## Contents

- `note/TIC264151965_note.md`, `note/TIC264151965_note.pdf`: the research note (draft; not submitted to a journal).
- `note/figure1_TIC264151965.png`: the six sectors folded on the period, the Sector 101 light curve, odd and even transits, and phase 0.5.
- `ephemeris.csv`: predicted mid-transit times from 2026-10-23 to 2027-12-31 with 1σ timing uncertainty.
- `code/search/`: the star search (`run_star.py` for Transit Least Squares, `run_star_gpu.py` and `drive_gpu.py` for the cuvarbase GPU box search, `GPU.md` for its calibration and control planets, `edgefix/` for the light-curve preparation tests).
- `code/leo/`: the LEO-vetter gate (`gate.py`, `leo_glue.py`, `control.py`, `LEO.md`).
- `code/vet/`: the vetting scripts (box checks, transit fit, short-period checks, catalogue checks, SAP against PDCSAP, pixel difference images, TRICERATOPS and MOLUSC runs).
- `code/ephemeris/`: the ephemeris fit (`fit_ephemeris.py`) and the prediction table (`ephemeris.py`).
- `code/note/fig1.py`: Figure 1.
- `data/search/`: the search result for this star, the LEO-vetter control results and its pass list.
- `data/vet/`: the vetting report (`VET.md`), its evidence files and plots, and the flattened search light curve (`264151965.npz`).
- `data/pixels/`: stacked difference images per sector and the neighbour tests.
- `data/triceratops/`, `data/triceratops_molusc/`: per-run TRICERATOPS outputs without and with MOLUSC limits.
- `data/molusc/`: MOLUSC logs and summary.
- `data/fit/`: the ephemeris posterior (`chain.npz`) and fit log.
- `data/exofop_ctoi_row.txt`: the prepared ExoFOP community-candidate parameter row (not uploaded).

## Next predicted transits

From `ephemeris.csv` (1σ timing uncertainty 1.5 minutes now, growing to 2.1 minutes by end of 2027):

| Epoch | Mid-transit BJD_TDB | Mid-transit UTC | ±1σ |
|---|---|---|---|
| 416 | 2461339.55038 | 2026-10-26 01:17 | 1.5 min |
| 417 | 2461344.36618 | 2026-10-30 20:51 | 1.6 min |
| 418 | 2461349.18198 | 2026-11-04 16:26 | 1.6 min |
| 419 | 2461353.99778 | 2026-11-09 12:01 | 1.6 min |
| 420 | 2461358.81357 | 2026-11-14 07:36 | 1.6 min |
| 421 | 2461363.62937 | 2026-11-19 03:11 | 1.6 min |

Times are propagated from every posterior sample of a transit fit with the period free (`code/ephemeris/fit_ephemeris.py`, same model and limb darkening as the vetting fit), so the correlation between T0 and P is kept. UTC times are geocentric (BJD_TDB minus the light-travel delay to the star, then TDB to UTC); ingress and egress are mid-transit ± 0.58 h. Epochs count from T0 = BJD_TDB 2459336.1785.

## Reproducing

Python 3.12 with numpy, scipy, pandas, matplotlib, astropy, astroquery, lightkurve, transitleastsquares, wotan, cuvarbase (GPU search), batman-package, emcee, TESS_PRF, LEO-vetter 1.2.0 (https://github.com/mkunimoto/LEO-Vetter), TRICERATOPS 1.1.0 and MOLUSC (https://github.com/woodml/MOLUSC, commit b26efbf3, not bundled).

1. Light curves. SPOC 2-minute PDCSAP for Sectors 38 and 65 and QLP full-frame-image light curves for Sectors 99 to 102, from MAST. FITS files and TESScut cutouts are not included; they are public at MAST. The flattened, binned light curve used for every step is `data/vet/264151965.npz`.
2. Search. `code/search/run_star_gpu.py` (GPU) or `code/search/run_star.py` (CPU), then `code/leo/gate.py` for LEO-vetter.
3. Vetting. `code/vet/` from a working folder holding `264151965.npz` and an `evidence/` folder: `s1_tls.py`, `s1_checks.py`, `s1_fit.py`, `short_period.py`, `short_period2.py`, `s2_catalogs.py`, `sap_pdc.py`, `pix_dl.py`, `diff.py`, `post.py`, then `trc_run.py` and `trc_summary.py`, then `molusc_all.sh`, `molusc_summary.py`, `trc_all_molusc.sh` and `trc_molusc_summary.py`. The 10⁶-row MOLUSC file passed to TRICERATOPS and the full MOLUSC outputs are not included because of their size; `molusc_summary.py` regenerates them from MOLUSC.
4. Ephemeris. `python code/ephemeris/fit_ephemeris.py data/vet/264151965.npz data/vet/01b_box_checks.json data/fit/chain.npz`, then `python code/ephemeris/ephemeris.py data/fit/chain.npz ephemeris.csv`.

Some scripts use paths relative to the original working folders; adjust them to your layout.

## Credits

This work uses data collected by the TESS mission, funded by the NASA Science Mission Directorate, obtained from the Mikulski Archive for Space Telescopes (MAST), including SPOC (Jenkins et al. 2016) and QLP (Huang et al. 2020) light curves and TESScut cutouts. It uses data from the European Space Agency mission Gaia (https://www.cosmos.esa.int/gaia), processed by the Gaia Data Processing and Analysis Consortium, and the TESS Input Catalog (Stassun et al. 2019). Companion limits use MOLUSC (Wood, Mann & Kraus 2021, AJ 162, 128); false-positive probabilities use TRICERATOPS (Giacalone & Dressing 2020; Giacalone et al. 2021); vetting uses LEO-vetter (Kunimoto et al. 2025). Full references are in the note.

## Licence and citation

Code is under the MIT licence (`LICENSE`). Text, figures and data are under CC BY 4.0 (`LICENSE-CC-BY-4.0`). Please cite with `CITATION.cff`.

## Contact

Advait Paliwal, advaitpaliwal@gmail.com
