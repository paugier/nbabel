# Micro benchmarks Julia and PyPy

## Julia

`julia microbench_ju4.jl` gives:

```
Main.NB.MutablePoint3D  12.004 ms (1048576 allocations: 32.00 MiB)
Main.NB.Point3D  3.262 ms (0 allocations: 0 bytes)
Main.NB.Point4D  2.546 ms (0 allocations: 0 bytes)
```

- Huge effect of adding the mutable keyword (3.7 x slower)
- Using Point4D instead of Point3D leads to a 1.3 speedup.

## PyPy

### Language features

1. Python has no fixed size homogeneous mutable sequence that
can contain instances of user-defined classes, so `Vector` needs to be
implemented (with a list, an extendable inhomogeneous sequence).

2. There is no notion of immutability for instances of user-defined class in
Python. So the `Point` objects are mutable (by default). One can subclass
`tuple` but it is not faster (see `bench_pypy4_tuple.py`).

### Performance

`pypy microbench_pypy4.py` gives

```
Point3D: 11.301 ms
Point4D: 22.050 ms
```

- With Point3D, PyPy is 3.5 times slower than PyPy.
- Using Point4D instead of Point3D decreases the perf (ratio 1.67).
