
bench1k:
	time julia -O3 --check-bounds=no -- run.jl nbabel.jl ../data/input1k false
	time julia -O3 --check-bounds=no -- run.jl nbabel3.jl ../data/input1k false
	time julia -O3 --check-bounds=no -- run.jl nbabel4.jl ../data/input1k false

bench2k:
	time julia -O3 --check-bounds=no -- run.jl nbabel.jl ../data/input2k false
	time julia -O3 --check-bounds=no -- run.jl nbabel3.jl ../data/input2k false
	time julia -O3 --check-bounds=no -- run.jl nbabel4.jl ../data/input2k false

benchparallel:
	time julia -t3 -O3 --check-bounds=no -- run.jl nbabel3.jl ../data/input1k false
	time julia -t3 -O3 --check-bounds=no -- run.jl nbabel4.jl ../data/input1k false
	time julia -t3 -O3 --check-bounds=no -- run.jl nbabel3.jl ../data/input2k false
	time julia -t3 -O3 --check-bounds=no -- run.jl nbabel4.jl ../data/input2k false
