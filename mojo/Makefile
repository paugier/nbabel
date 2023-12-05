bench:
	mojo bench_simd.mojo ../data/input1k

bench_simple:
	mojo bench.mojo ../data/input1k

bench_no_part:
	mojo bench_no_part.mojo ../data/input1k

bench_simd:
	mojo -D nelts=2 bench_simd.mojo  ../data/input1k 1
	mojo -D nelts=4 bench_simd.mojo  ../data/input1k 1
	mojo -D nelts=8 bench_simd.mojo  ../data/input1k 1
	mojo -D nelts=16 bench_simd.mojo  ../data/input1k 1