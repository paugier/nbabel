# Mojo implementations of the n-body problem

- bench.mojo: reference implementation with a Particle struct
- bench_no_part.mojo: implementation without Particle struct
  (instead `InlinedFixedVector[Vec4floats]`)
- bench_simd.mojo: explicit simd with tile or vectorize

## Issue with SIMD

There is a interesting implementation using SIMD. The code is in the files
particles.mojo and bench_simd.mojo, and the code in particles.mojo is also
tested for different sizes of SIMD vector (`nelts`) in
mokowals_experiments.mojo. These tests seem to pass. The only function that uses
SIMD is `accelerate` (if has 2 variants using `tile` and `vectorize`).

Unfortunately, the results of bench_simd.mojo do not seem numerically reliable
and I observe something like a numerical instability. The results are different
for different values of the alias `nelts`, and also when using `accelerate_tile`
or `accelerate_vectorize`.



