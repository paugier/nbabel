
```
python -m cProfile -o profile.pstats bench_pypy4.py ../data/input128
gprof2dot -f pstats profile.pstats | dot -Tpng -o profile.png

```