SHELL := /bin/bash

bench128: nbabel
		time ./nbabel-nbody/target/release/nbabel ../data/input128 0
		time ./nbabel-nbody/target/release/nbabel ../data/input128 1
		time ./nbabel-nbody/target/release/nbabel ../data/input128 2 4

bench256: nbabel
		time ./nbabel-nbody/target/release/nbabel ../data/input256 0
		time ./nbabel-nbody/target/release/nbabel ../data/input256 1
		time ./nbabel-nbody/target/release/nbabel ../data/input256 2 4

bench1k: nbabel
		time ./nbabel-nbody/target/release/nbabel ../data/input1k 0
		time ./nbabel-nbody/target/release/nbabel ../data/input1k 1
		time ./nbabel-nbody/target/release/nbabel ../data/input1k 2 4

bench2k: nbabel
		time ./nbabel-nbody/target/release/nbabel ../data/input2k 0
		time ./nbabel-nbody/target/release/nbabel ../data/input2k 1
		time ./nbabel-nbody/target/release/nbabel ../data/input2k 2 4

nbabel:
	cd ./nbabel-nbody/ && cargo build --release

clean:
	rm -rf ./nbabel-nbody/target/*