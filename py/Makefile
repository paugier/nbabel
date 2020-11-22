
CC=gcc
CXX=g++

bench_pypy:
	pypy bench_purepy.py ../data/input16

bench64_pypy:
	pypy bench_purepy.py ../data/input64

bench0:
	python bench0.py ../data/input16

bench1k: __pythran__/bench.py
	python bench.py ../data/input1k

bench2k: __pythran__/bench.py
	python bench.py ../data/input2k

bench256: __pythran__/bench.py
	python bench.py ../data/input256

bench128: __pythran__/bench.py
	python bench.py ../data/input128

bench64: __pythran__/bench.py
	python bench.py ../data/input64

__pythran__/bench.py: bench.py
	transonic bench.py -af "-march=native -Ofast"

	# transonic bench.py -af "-march=native -DUSE_XSIMD -Ofast"

clean:
	rm -rf __pythran__
