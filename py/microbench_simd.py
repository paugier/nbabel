import numpy as np

from transonic import jit, wait_for_all_extensions


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


shape = 256, 3

positions = np.zeros(shape)
velocities = np.zeros_like(positions)
accelerations = np.zeros_like(positions)

time_step = 1.0

advance_positions_nosimd(positions, velocities, accelerations, time_step)
advance_positions_simd(positions, velocities, accelerations, time_step)
advance_positions_loops(positions, velocities, accelerations, time_step)

wait_for_all_extensions()
