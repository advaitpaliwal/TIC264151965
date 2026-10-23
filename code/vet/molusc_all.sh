#!/bin/zsh
# 4 MOLUSC runs (seeds 11-14), 50,000 companions each, RUWE + Gaia contrast only, age default 5 Gyr; copied from hz-wide/vet_270573718/glue/molusc_all.sh; coords from TIC RA 217.3258 Dec -58.7664, M 0.289.
cd ~/Scratch/planet-hunt/v4/vet_264151965
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 NUMBA_NUM_THREADS=1
P=~/Scratch/planet-hunt/tic240488148-companions/.venv-molusc/bin/python
O=$PWD/molusc_out
run(){ SEED=$1 taskpolicy -a $P glue/molusc_run.py --ruwe --gaia -a $O/m50k_s$1 14h29m18.192s -- -58d45m59.04s 50000 0.289 > $O/m50k_s$1.log 2>&1 }
run 11 & run 12 & run 13 & wait; run 14
echo DONE > $O/DONE
