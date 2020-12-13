
bench1k:
	time julia -O3 --check-bounds=no -- nbabel.jl ../data/input1k false
	time julia -O3 --check-bounds=no -- nbabel3.jl ../data/input1k false
	time julia -O3 --check-bounds=no -- nbabel4.jl ../data/input1k false

bench2k:
	time julia -O3 --check-bounds=no -- nbabel.jl ../data/input2k false
	time julia -O3 --check-bounds=no -- nbabel3.jl ../data/input2k false
	time julia -O3 --check-bounds=no -- nbabel4.jl ../data/input2k false

benchparallel:
	time julia -t3 -O3 --check-bounds=no -- nbabel3.jl ../data/input1k false
	time julia -t3 -O3 --check-bounds=no -- nbabel4.jl ../data/input1k false
	time julia -t3 -O3 --check-bounds=no -- nbabel3.jl ../data/input2k false
	time julia -t3 -O3 --check-bounds=no -- nbabel4.jl ../data/input2k false
