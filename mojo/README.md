# Mojo implementations of the n-body problem

- bench.mojo: reference implementation with a Particle struct
- bench_no_part.mojo: implementation without Particle struct (instead
  `InlinedFixedVector[Vec4floats]`)
- bench_simd.mojo: explicit simd with tile or vectorize

The code using explicit SIMD is in particles.mojo and bench_simd.mojo, and the
code in particles.mojo is also tested for different sizes of SIMD vector (`nelts`)
in mokowals_experiments.mojo. These tests seem to pass. The only function that
uses SIMD is `accelerate` (if has 2 variants using `tile` and `vectorize`).

## Performance

I compare sequential implementation in Python, Julia and Mojo. We have a quite
efficient implementation in pure Python using PyPy. On recent computers with a
good CPU, we can get interesting speedup with Julia and Mojo.

On a computer for which `simdwidthof[DType.float64]()` gives 4 (AMD Ryzen 7
7730U), I get:

- PyPy: 45 s
- Julia advanced (nbabel5_serial.jl): 20 s
- bench.mojo: 23 s
- bench_no_part.mojo: 22 s
- mojo -D nelts=2 bench_simd.mojo 16.4 s
- mojo -D nelts=4 bench_simd.mojo 9.2 s
- mojo -D nelts=16 bench_simd.mojo 7.3 s

## Correctness

I am a bit septical about the correctness of the implementations in Mojo. The
results do not seem numerically reliable and I observe something like a numerical
instability. The energy is not conserved and for some time steps, there is a
discontinuity in energy.

Moreover, the results can be different for different values of the alias `nelts`,
and also when using `accelerate_tile` or `accelerate_vectorize`.
