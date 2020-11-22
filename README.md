# Benchmark N-Body system

Here are some elapsed times (in s) for 3 implementations.

| # particles |  Py | C++ | Fortran |
|-------------|-----|-----|---------|
|     1024    |  29 |  58 |   43    |
|     2048    | 123 | 239 |  174    |

The implementations in C++ and Fortran come from https://www.nbabel.org/ and
have recently been used in an article published in Nature Astronomy ([Zwart,
2020](https://arxiv.org/pdf/2009.11295.pdf)). The implementation in
Python-Numpy is very simple, but uses
[Transonic](https://transonic.readthedocs.io) and
[Pythran](https://pythran.readthedocs.io).

To run these benchmarks, go into the different directories and run `make
bench1k` or `make bench2k`.

To give an idea of what it gives compared to the figure published in Nature Astronomy:

![image](https://raw.githubusercontent.com/paugier/nbabel/master/py/fig/fig_ecolo_impact_transonic.png)
