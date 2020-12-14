
all : bench1k bench2k benchparallel bench1k-nobounds bench2k-nobounds benchparallel-nobounds

bench1k:
	time julia -O3 -- run.jl nbabel.jl ../data/input1k true
	time julia -O3 -- run.jl nbabel4_serial.jl ../data/input1k true
	time julia -O3 -- run.jl nbabel4_threads.jl ../data/input1k true

bench2k:
	time julia -O3 -- run.jl nbabel.jl ../data/input2k true
	time julia -O3 -- run.jl nbabel4_serial.jl ../data/input2k true
	time julia -O3 -- run.jl nbabel4_threads.jl ../data/input2k true

benchparallel:
	time julia -t3 -O3 -- run.jl nbabel4_threads.jl ../data/input1k true
	time julia -t3 -O3 -- run.jl nbabel4_threads.jl ../data/input2k true

bench1k-nobounds:
	time julia -O3 --check-bounds=no -- run.jl nbabel.jl ../data/input1k true
	time julia -O3 --check-bounds=no -- run.jl nbabel4_serial.jl ../data/input1k true
	time julia -O3 --check-bounds=no -- run.jl nbabel4_threads.jl ../data/input1k true

bench2k-nobounds:
	time julia -O3 --check-bounds=no -- run.jl nbabel.jl ../data/input2k true
	time julia -O3 --check-bounds=no -- run.jl nbabel4_serial.jl ../data/input2k true
	time julia -O3 --check-bounds=no -- run.jl nbabel4_threads.jl ../data/input2k true

benchparallel-nobounds:
	time julia -t3 -O3 --check-bounds=no -- run.jl nbabel4_threads.jl ../data/input1k true
	time julia -t3 -O3 --check-bounds=no -- run.jl nbabel4_threads.jl ../data/input2k true

