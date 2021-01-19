
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

pythran: __pythran__/microbench_pythran.py
	python microbench_pythran.py

__pythran__/microbench_pythran.py: microbench_pythran.py
	transonic microbench_pythran.py -af "-march=native -Ofast"

julia_tuple:
	julia microbench_ju_tuple.jl
