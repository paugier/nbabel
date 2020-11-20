
CC=gcc
CXX=g++

bench:
	pypy bench_purepy.py ../data/input16

bench64:
	pypy bench_purepy.py ../data/input64

bench0:
	python bench0.py ../data/input16

bench1k_pythran: __pythran__/bench.py
	python bench.py ../data/input1k

bench256_pythran: __pythran__/bench.py
	python bench.py ../data/input256

__pythran__/bench.py: bench.py
	transonic bench.py -af "-march=native -Ofast"

	# transonic bench.py -af "-march=native -DUSE_XSIMD -Ofast"

clean:
	rm -rf __pythran__