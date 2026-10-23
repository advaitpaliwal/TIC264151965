#!/bin/bash
# 10 MOLUSC-mode TRICERATOPS runs (none removed, seeds 1000-1009) on the Spark; env as glue/trc_launch_spark.sh, nice 10.
cd ~/planet-hunt/trc_264151965
mkdir -p trc_molusc/out
for k in 0 1 2 3 4 5 6 7 8 9; do
  NUMPY_MADVISE_HUGEPAGE=0 NUMBA_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 nohup nice -n 10 ~/planet-hunt/trc_venv/bin/python -I glue/trc_run_molusc.py $k > trc_molusc/out/log_$k.txt 2>&1 &
done
sleep 1; ps -eo args | grep -c "trc_run_molusc"; date
