bench256: main
	cat ../data/input256 | time ./main

bench128: main
	cat ../data/input128 | time ./main

bench1k: main
	cat ../data/input1k | time ./main

bench2k: main
	cat ../data/input2k | time ./main

bench16: main
	cat ../data/input16 | time ./main

main: main.cpp
	g++ -march=native -O3 main.cpp -o main

clean:
	rm -f main