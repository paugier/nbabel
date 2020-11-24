bench256: nbabel
	time ./nbabel ../data/input256 256

bench1k: nbabel
	time ./nbabel ../data/input1k 1024

bench2k: nbabel
	time ./nbabel ../data/input2k 2048

nbabel: nbabel.f03
	gfortran -march=native -Ofast nbabel.f03 -o nbabel

clean:
	rm -f nbabel *.mod