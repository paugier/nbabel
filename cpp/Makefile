bench256: main
	cat ../data/input256 | time ./main

bench16: main
	cat ../data/input16 | time ./main

main: main.cpp
	g++ -O4 main.cpp -o main
