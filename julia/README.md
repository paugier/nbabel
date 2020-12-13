
## Alternative implementations of the Julia version:

`nbabel.jl` is the implementation mentioned in the main README.

`nbabel3.jl` solves a series of allocations and uses static arrays. A simple parallelization
is implemented. 

`nbabel4.jl` uses a custom struct with 4 fields to take the most from SIMD operations.   

Benchmarks measure the time reported by sytem time, as output by the `Makefile` commands.

Single-threaded, in a Intel(R) Core(TM) i7-8550U CPU @ 1.80GHz:

| # particles |  nbabel.jl | nbabel3.jl | nbabel4.jl |
|-------------|------------|------------|------------|
|     1024    |    51.3    |   40.2     |    29.6    |
|     2048    |   191.1    |  147.1     |   119.1    |

With 3 processors (the laptop has 4):

| # particles |  nbabel.jl | nbabel3.jl | nbabel4.jl |
|-------------|------------|------------|------------|
|     1024    |     -      |   26.9     |   23.8     |
|     2048    |     -      |   91.0     |   86.6     |


