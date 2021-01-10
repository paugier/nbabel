# Micro benchmarks Julia and PyPy

## Function compute_accelerations

### Julia

`julia microbench_ju4.jl` gives:

```
Main.NB.MutablePoint3D  12.004 ms (1048576 allocations: 32.00 MiB)
Main.NB.Point3D  3.262 ms (0 allocations: 0 bytes)
Main.NB.Point4D  2.546 ms (0 allocations: 0 bytes)
```

- Huge effect of adding the mutable keyword (3.7 x slower)
- Using Point4D instead of Point3D leads to a 1.3 speedup.

### PyPy

#### Language features

1. Python has no fixed size homogeneous mutable sequence that
can contain instances of user-defined classes, so `Vector` needs to be
implemented (with a list, an extendable inhomogeneous sequence).

2. There is no notion of immutability for instances of user-defined class in
Python. So the `Point` objects are mutable (by default). One can subclass
`tuple` but it is not faster (see `bench_pypy4_tuple.py`).

#### Performance

`pypy microbench_pypy4.py` gives `Point3D: 10.888 ms` and `pypy
microbench_pypy4.py 4` gives `Point4D: 12.633 ms`.

- With Point3D, PyPy is 3.5 times slower than PyPy.
- Using Point4D instead of Point3D decreases the perf (ratio 1.16).

## Functions `sum_few_x` and `sum_few_norm2`

### Julia

`make ju` gives:

```
julia microbench_sum_x.jl
sum_few_x(points)
  996.000 ns (1 allocation: 16 bytes)
sum_all_x(points)
  1.005 μs (1 allocation: 16 bytes)
sum_few_norm2(points)
  1.007 μs (1 allocation: 16 bytes)
```

The three functions run in approximately 1 μs.

- In `sum_few_x`, we loop over a vector of `struct` (only few elements) and
compute the sum of the `x` attr.

- In `sum_all_x`, we loop over a vector of `struct` (all elements) and compute
the sum of the `x` attr.

- In `sum_few_norm2`, we loop over a vector of `struct` (only few elements) and
compute the sum of the square of the norm of the elements with a function
`norm` associated with the type of the element `Point`.

### PyPy

`make pysum` gives something like:

```
ipython microbench_sum_x.py
sum_few_x(points)
  2.1 µs ± 21.4 ns
sum_all_x(points)
  2.38 µs ± 10.8 ns
sum_few_norm2(points)
  3.1 µs ± 19.6 ns
sum_few_norm2_func(points)
  3.13 µs ± 19.8 ns

ipython microbench_cffi.py
sum_few_x(points)
  1.86 µs ± 42 ns
sum_all_x(points)
  1.38 µs ± 10.9 ns
sum_few_norm2_func(points)
  2.43 µs ± 82.3 ns
```

We see that these simple functions are 2 to 3 times slower than in Julia.
Having less dynamic objects (pointers and C struct, using cffi) helps a bit
(but one cannot associated a method with the type of the elements). However, we
can guess that there is a problem of vectorization with `sum_few_norm2`, which
is still 2.4 slower than in Julia.
