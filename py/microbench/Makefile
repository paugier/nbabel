
all: ju pysum

pysum: vector cffi

vector:
	ipython microbench_sum_x.py

cffi:
	ipython microbench_cffi.py

ju:
	julia microbench_sum_x.jl