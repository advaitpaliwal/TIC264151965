cd ~/planet-hunt/trc_264151965
rm -f glue/trc_probe.py trc/probe*.log trc/probe_* bench/b2.py
for k in 0 1 2 3 4 5 6 7 8 9; do
  NUMPY_MADVISE_HUGEPAGE=0 NUMBA_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 nohup nice -n 19 ~/planet-hunt/trc_venv/bin/python -I glue/trc_run.py $k > trc/run_$k.log 2>&1 &
done
sleep 1; ps -eo args | grep -c "^/home/advaitpaliwal/planet-hunt/trc_venv/bin/python -I glue/trc_run"; date
