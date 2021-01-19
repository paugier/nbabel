
import numpy as np
from transonic import jit, wait_for_all_extensions
from transonic.util import timeit_verbose as timeit


def advance_positions(positions, velocities, accelerations, time_step):
    positions += time_step * velocities + 0.5 * time_step ** 2 * accelerations


@jit(native=True, xsimd=False)
def advance_positions_nosimd(positions, velocities, accelerations, time_step):
    positions += time_step * velocities + 0.5 * time_step ** 2 * accelerations


@jit(native=True, xsimd=True)
def advance_positions_simd(positions, velocities, accelerations, time_step):
    positions += time_step * velocities + 0.5 * time_step ** 2 * accelerations


@jit(native=True, xsimd=False)
def advance_positions_loops(positions, velocities, accelerations, time_step):
    n0, n1 = positions.shape
    for i0 in range(n0):
        for i1 in range(n1):
            positions[i0, i1] += (
                time_step * velocities[i0, i1]
                + 0.5 * time_step ** 2 * accelerations[i0, i1]
            )


@jit(native=True, xsimd=False)
def advance_positions_nosimd_ra(positions, velocities, accelerations, time_step):
    size = positions.size
    positions_ra = positions.ravel()
    velocities_ra = velocities.ravel()
    accelerations_ra = accelerations.ravel()
    positions_ra += (
        time_step * velocities_ra + 0.5 * time_step ** 2 * accelerations_ra
    )


@jit(native=True, xsimd=True)
def advance_positions_simd_ra(positions, velocities, accelerations, time_step):
    size = positions.size
    positions_ra = positions.ravel()
    velocities_ra = velocities.ravel()
    accelerations_ra = accelerations.ravel()
    positions_ra += (
        time_step * velocities_ra + 0.5 * time_step ** 2 * accelerations_ra
    )


@jit(native=True, xsimd=False)
def advance_positions_loops_ra(positions, velocities, accelerations, time_step):
    size = positions.size
    positions_ra = positions.ravel()
    velocities_ra = velocities.ravel()
    accelerations_ra = accelerations.ravel()

    for ind in range(size):
        positions_ra[ind] += (
            time_step * velocities_ra[ind] + 0.5 * time_step ** 2 * accelerations_ra[ind]
        )

coef = 1
# coef = 16
shape = 256 * 4 // coef, 4 * coef
print("shape:", shape)
positions = np.zeros(shape)
velocities = np.zeros_like(positions)
accelerations = np.zeros_like(positions)
time_step = 1.0

advance_positions_nosimd(positions, velocities, accelerations, time_step)
advance_positions_simd(positions, velocities, accelerations, time_step)
advance_positions_loops(positions, velocities, accelerations, time_step)

advance_positions_nosimd_ra(positions, velocities, accelerations, time_step)
advance_positions_simd_ra(positions, velocities, accelerations, time_step)
advance_positions_loops_ra(positions, velocities, accelerations, time_step)


wait_for_all_extensions()

norm = timeit(
    "advance_positions(positions, velocities, accelerations, time_step)",
    globals=locals(),
)
timeit(
    "advance_positions_simd(positions, velocities, accelerations, time_step)",
    globals=locals(),
    norm=norm,
)
timeit(
    "advance_positions_nosimd(positions, velocities, accelerations, time_step)",
    globals=locals(),
    norm=norm,
)
timeit(
    "advance_positions_loops(positions, velocities, accelerations, time_step)",
    globals=locals(),
    norm=norm,
)

timeit(
    "advance_positions_simd_ra(positions, velocities, accelerations, time_step)",
    globals=locals(),
    norm=norm,
)
timeit(
    "advance_positions_nosimd_ra(positions, velocities, accelerations, time_step)",
    globals=locals(),
    norm=norm,
)
timeit(
    "advance_positions_loops_ra(positions, velocities, accelerations, time_step)",
    globals=locals(),
    norm=norm,
)
