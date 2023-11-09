SHELL=bash

all : bench1k bench2k benchparallel bench1k-nobounds bench2k-nobounds benchparallel-nobounds

bench_table:
	# time julia -O3 -- run.jl nbabel4_serial.jl ../data/input1k true
	# time julia -O3 -- run.jl nbabel4_serial.jl ../data/input2k true
	time julia -O3 -- run.jl nbabel5_serial.jl ../data/input1k true
	time julia -O3 -- run.jl nbabel5_serial.jl ../data/input2k true

bench_big:
	# time julia -O3 --check-bounds=no -- run.jl nbabel4_serial.jl ../data/input16k false 0.2
	# time julia -t2 -O3 --check-bounds=no -- run.jl nbabel4_threads.jl ../data/input16k false 0.2
	time julia -O3 --check-bounds=no -- run.jl nbabel5_serial.jl ../data/input16k false 0.2
	time julia -t2 -O3 --check-bounds=no -- run.jl nbabel5_threads.jl ../data/input16k false 0.2

bench_part4:
	# time julia -O3 -- run.jl nbabel4_serial.jl ../data/input1k false
	time julia -O3 -- run.jl nbabel5_serial.jl ../data/input1k false
	time julia -O3 -- run.jl nbabel_oop_serial.jl ../data/input1k false

bench1k:
	time julia -O3 -- run.jl nbabel.jl ../data/input1k true
	# time julia -O3 -- run.jl nbabel4_serial.jl ../data/input1k true
	# time julia -O3 -- run.jl nbabel4_threads.jl ../data/input1k true
	time julia -O3 -- run.jl nbabel5_serial.jl ../data/input1k true
	time julia -O3 -- run.jl nbabel5_threads.jl ../data/input1k true

bench2k:
	time julia -O3 -- run.jl nbabel.jl ../data/input2k true
	# time julia -O3 -- run.jl nbabel4_serial.jl ../data/input2k true
	# time julia -O3 -- run.jl nbabel4_threads.jl ../data/input2k true
	time julia -O3 -- run.jl nbabel5_serial.jl ../data/input2k true
	time julia -O3 -- run.jl nbabel5_threads.jl ../data/input2k true

benchparallel:
	# time julia -t4 -O3 -- run.jl nbabel4_threads.jl ../data/input1k true
	# time julia -t4 -O3 -- run.jl nbabel4_threads.jl ../data/input2k true
	time julia -t4 -O3 -- run.jl nbabel5_threads.jl ../data/input1k true
	time julia -t4 -O3 -- run.jl nbabel5_threads.jl ../data/input2k true

bench1k-nobounds:
	time julia -O3 --check-bounds=no -- run.jl nbabel.jl ../data/input1k true
	# time julia -O3 --check-bounds=no -- run.jl nbabel4_serial.jl ../data/input1k true
	# time julia -O3 --check-bounds=no -- run.jl nbabel4_threads.jl ../data/input1k true
	time julia -O3 --check-bounds=no -- run.jl nbabel5_serial.jl ../data/input1k true
	time julia -O3 --check-bounds=no -- run.jl nbabel5_threads.jl ../data/input1k true

bench2k-nobounds:
	time julia -O3 --check-bounds=no -- run.jl nbabel.jl ../data/input2k true
	# time julia -O3 --check-bounds=no -- run.jl nbabel4_serial.jl ../data/input2k true
	# time julia -O3 --check-bounds=no -- run.jl nbabel4_threads.jl ../data/input2k true
	time julia -O3 --check-bounds=no -- run.jl nbabel5_serial.jl ../data/input1k true
	time julia -O3 --check-bounds=no -- run.jl nbabel5_threads.jl ../data/input1k true

benchparallel-nobounds:
	# time julia -t4 -O3 --check-bounds=no -- run.jl nbabel4_threads.jl ../data/input1k false
	# time julia -t4 -O3 --check-bounds=no -- run.jl nbabel4_threads.jl ../data/input2k false
	time julia -t4 -O3 --check-bounds=no -- run.jl nbabel5_threads.jl ../data/input1k false
	time julia -t4 -O3 --check-bounds=no -- run.jl nbabel5_threads.jl ../data/input2k false
