
all: ju pysum

pysum: vector cffi

vector:
	ipython microbench_sum_x.py

cffi:
	ipython microbench_cffi.py

ju:
	julia microbench_sum_x.jl

icy: util_cython.pyx
	cythonize -a -i util_cython.pyx
	ipython microbench_cython.py
