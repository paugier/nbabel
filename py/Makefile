SHELL = bash

build: __pythran__/bench.py
	# launching to "warm the jit"
	python bench_numpy_highlevel_jit.py ../data/input16 0.1

bench0:
	python bench0.py ../data/input16

bench_compyler:
	python bench_compyler.py ../data/input16

bench_pypy_Point:
	pypy bench_purepy_Point.py ../data/input16

bench_pypy:
	pypy bench_purepy_Particle.py ../data/input16

bench1k_pypy:
	pypy bench_purepy_Particle.py ../data/input1k

bench1k: __pythran__/bench.py
	time python bench.py ../data/input1k

bench1k_opti: __pythran__/bench_more_opti.py
	time python bench_more_opti.py ../data/input1k

bench1k_omp: __pythran__/bench_omp.py
	time python bench_omp.py ../data/input1k

bench2k: __pythran__/bench.py
	time python bench.py ../data/input2k

bench16k: __pythran__/bench.py
	time python bench.py ../data/input16k 0.2

bench256: __pythran__/bench.py
	python bench.py ../data/input256

bench128: __pythran__/bench.py
	python bench.py ../data/input128

bench64: __pythran__/bench.py
	python bench.py ../data/input64

__pythran__/bench.py: bench.py
	# transonic bench.py -af "-march=native -Ofast"
	transonic bench.py -af "-march=native -DUSE_XSIMD -Ofast"

__pythran__/bench_more_opti.py: bench_more_opti.py
	transonic bench_more_opti.py -af "-march=native -DUSE_XSIMD -Ofast"

__pythran__/bench_omp.py: bench_omp.py
	transonic bench_omp.py -af "-march=native -DUSE_XSIMD -Ofast -fopenmp"

clean:
	rm -rf __pythran__

create_venv_pypy:
	uv python install pypy
	$(shell uv python find pypy) -m venv .venv_pypy --upgrade-deps
