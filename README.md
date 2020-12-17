# Benchmark N-Body system

Here are some elapsed times (in s) for 5 **implementations** (of course, these
numbers do not characterized the languages but only particular implementations
in some languages).

| # particles |  Py | C++ | Fortran | Julia | Rust |
|-------------|-----|-----|---------|-------|------|
|     1024    |  30 |  55 |   41    |   45  |   34 |
|     2048    | 124 | 231 |  166    |  173  |  137 |

The implementations in C++, Fortran and Julia come from https://www.nbabel.org/
and have recently been used in an article published in Nature Astronomy
([Zwart, 2020](https://arxiv.org/pdf/2009.11295.pdf)). The implementation in
Python-Numpy is very simple, but uses
[Transonic](https://transonic.readthedocs.io) and
[Pythran](https://pythran.readthedocs.io) (>=0.9.8).

To run these benchmarks, go into the different directories and run `make
bench1k` or `make bench2k`.

To give an idea of what it gives compared to the figure published in Nature Astronomy:

![image](https://raw.githubusercontent.com/paugier/nbabel/master/py/fig/fig_ecolo_impact_transonic.png)

**Note:** these benchmarks are run sequentially with a Intel(R) Core(TM)
i5-8400 CPU @ 2.80GHz.

**Note 2:** With Numba, the elapsed times are 46 s and 181 s, respectively.

**Note 3:** With PyPy, a pure Python implementation (bench_pypy4.py) runs for
1024 particles in 151 s, i.e. only 3 times slower than the C++ implementation
(compared to ~50 times slower as shown in the figure taken from Zwart, 2020).

**Note 4:** The directory "julia" contains some more advanced and faster
implementations. The sequential optimized Julia implementation runs on my PC in
27.2 s and 104.4 s, respectively (i.e. 1.1-1.2 times faster than our fast and
simple Python implementation).

## Smaller benchmarks between different Python solutions

We can also compare different solutions in Python. Since some solutions are
very slow, we need to compare on a much smaller problem (only 128 particles).
Here are the elapsed times (in s):

| Transonic-Pythran | Numba | High-level Numpy | PyPy OOP | PyPy lists |
|-------------------|-------|------------------|----------|------------|
| 0.48              | 0.87  | 686              |  3.4     |  4.3       |

For comparison, we have for this case `{"c++": 0.85, "Fortran": 0.62, "Julia":
2.57}`.

Note that just adding `from transonic import jit` to the simple high-level
Numpy code and then decorating the function `loop` with `@jit`, the elapsed
time decreases to 2.1 s (a ~ x300 speedup!, with Pythran 0.9.8).
