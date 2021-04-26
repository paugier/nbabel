build: main

bench16: main
	cat ../data/input16 | time ./main

bench256: main
	cat ../data/input256 | time ./main

bench128: main
	cat ../data/input128 | time ./main

bench1k: main
	cat ../data/input1k | time ./main

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

main: main.cpp
	g++ -march=native -Ofast main.cpp -o main

main_opt: main_opt.cpp
	g++ -march=native -Ofast main_opt.cpp -o main_opt

clean:
	rm -f main