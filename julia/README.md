
## Alternative implementations of the Julia version:

`nbabel.jl` is the implementation mentioned in the main README.

The `nbabel4` implementations use a custom Particle struct with 4
Float64 fields to maximize the performance of SIMD operations.

`nbabel4_serial.jl`:  only runs in serial.

`nbabel4_threads.jl`: runs with one or multiple processors. (use the `-tN` flag)

Benchmarks measure the time reported by sytem time, as output by the `Makefile` commands.

`@inbounds` flags are added to O(N^2) loops, but the benchmark appears to be somewhat
dependent on bounds checking anyway, particularly for the parallel version, which
allocates larger arrays for non-concurrent sums. Thus, two benchmarks were performed, with and
without a global flag to avoid bounds checking:

### Single-threaded in a Intel(R) Core(TM) i7-8550U CPU @ 1.80GHz:

With julia flags `-O3 --check-bounds=no`:

| # particles |  nbabel.jl | nbabel_serial.jl | nbabel4_threads.jl |
|-------------|------------|------------------|--------------------|
|     1024    |    50.7    |    29.1          |      30.0          |
|     2048    |   191.1    |   123.1          |     114.4          |

With julia flag `-O3` only:

| # particles |  nbabel.jl | nbabel_serial.jl | nbabel4_threads.jl |
|-------------|------------|------------------|--------------------|
|     1024    |    48.9    |    31.2          |    45.1            |
|     2048    |   205.7    |   131.9          |   173.8            |


### With 3 processors (the laptop has 4):

With julia flags `-O3 --check-bounds=no -t3`:

| # particles | nbabel4_threads.jl |
|-------------|--------------------|
|     1024    |   20.6             |
|     2048    |   80.2             |

- Differences smaller than about 10% are not probably not significant.

## Requirements

All versions require the `DelimitedFiles` package. Install with:

```julia
julia> ] add DelimitedFiles

```

(Julia version 1.5 or greater is recommended)




