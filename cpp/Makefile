build: main

bench16: main
	cat ../data/input16 | time ./main

bench256: main
	cat ../data/input256 | time ./main

bench128: main
	cat ../data/input128 | time ./main

bench1k: main
	cat ../data/input1k | time ./main

bench1k_opt_all: main_opt_all
	cat ../data/input1k | time ./main_opt_all

bench1k_opt_algo: main_opt_algo
	cat ../data/input1k | time ./main_opt_algo

bench2k: main
	cat ../data/input2k | time ./main

bench16k: main
	cat ../data/input16k | time ./main 0.5

bench1k_opt: main_opt
	cat ../data/input1k | time ./main_opt

bench2k_opt: main_opt
	cat ../data/input2k | time ./main_opt

bench16k_opt: main_opt
	cat ../data/input16k | time ./main_opt 0.5

bench1k_arrays: main_arrays
	cat ../data/input1k | time ./main_arrays

bench2k_arrays: main_arrays
	cat ../data/input2k | time ./main_arrays

bench16k_arrays: main_arrays
	cat ../data/input16k | time ./main_arrays 0.5

%: %.cpp
	g++ -march=native -Ofast $< -o $@

clean:
	rm -f main
