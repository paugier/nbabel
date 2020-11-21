bench256: nbabel
	time ./nbabel ../data/input256 256

bench1k: nbabel
	time ./nbabel ../data/input1k 1024

nbabel: nbabel.f03
	gfortran -O3 nbabel.f03 -o nbabel
