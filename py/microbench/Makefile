
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
	transonic microbench_pythran.py -af "-march=native -Ofast -mfma"


pythran_omp: __pythran__/microbench_pythran_omp.py
	python microbench_pythran_omp.py

__pythran__/microbench_pythran_omp.py: microbench_pythran_omp.py
	transonic microbench_pythran_omp.py -af "-march=native -Ofast -fopenmp"



julia_tuple:
	julia microbench_ju_tuple.jl
