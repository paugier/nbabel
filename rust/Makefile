SHELL := /bin/bash

bench128: nbabel
		time ./nbabel ../data/input128

bench256: nbabel
		time ./nbabel ../data/input256

bench1k: nbabel
		time ./nbabel ../data/input1k

bench2k: nbabel
		time ./nbabel ../data/input2k

nbabel: 
	rustc -C opt-level=3 nbabel.rs

clean:
	rm -f nbabel