SHELL := /bin/bash

build: main

bench16: main
	time cat ../data/input16 | ./main

bench256: main
	time cat ../data/input256 | ./main

bench128: main
	time cat ../data/input128 | ./main

bench1k: main
	time cat ../data/input1k | ./main

bench1k_opt_all: main_opt_all
	time cat ../data/input1k | ./main_opt_all

bench1k_opt_algo: main_opt_algo
	time cat ../data/input1k | ./main_opt_algo

bench2k: main
	time cat ../data/input2k | ./main

bench16k: main
	time cat ../data/input16k | ./main 0.5

bench1k_opt: main_opt
	time cat ../data/input1k | ./main_opt

bench2k_opt: main_opt
	time cat ../data/input2k | ./main_opt

bench16k_opt: main_opt
	time cat ../data/input16k | ./main_opt 0.5

bench1k_arrays: main_arrays
	time cat ../data/input1k | ./main_arrays

bench2k_arrays: main_arrays
	time cat ../data/input2k | ./main_arrays

bench16k_arrays: main_arrays
	time cat ../data/input16k | ./main_arrays 0.5

%: %.cpp
	g++ -march=native -Ofast $< -o $@

clean:
	rm -f main
