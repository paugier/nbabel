from math import sqrt
from time import perf_counter
from time import time as perf_time
from datetime import timedelta

import numpy as np
import pandas as pd

# pythran specific omp module
import omp

from transonic import boost

dim = 3


def load_input_data(path):
    df = pd.read_csv(
        path, names=["mass", "x", "y", "z", "vx", "vy", "vz"], delimiter=r"\s+"
    )

    # warning: copy() is for Pythran...
    masses = df["mass"].values.copy()
    positions = df.loc[:, ["x", "y", "z"]].values.copy()
    velocities = df.loc[:, ["vx", "vy", "vz"]].values.copy()

    return masses, positions, velocities


def advance_positions(positions, velocities, accelerations, time_step):
    positions_ra = positions.ravel()
    velocities_ra = velocities.ravel()
    accelerations_ra = accelerations.ravel()

    # omp parallel for
    for i in range(len(positions_ra)):
        positions_ra[i] += (
            time_step * velocities_ra[i]
            + 0.5 * time_step ** 2 * accelerations_ra[i]
        )


def advance_velocities(velocities, accelerations, accelerations1, time_step):
    velocities_ra = velocities.ravel()
    accelerations_ra = accelerations.ravel()
    accelerations1_ra = accelerations1.ravel()

    # omp parallel for
    for i in range(len(velocities_ra)):
        velocities_ra[i] += (
            0.5 * time_step * (accelerations_ra[i] + accelerations1_ra[i])
        )


def compute_accelerations(accelerations, masses, positions):
    nb_particules = masses.size
    nthreads = accelerations.shape[0]

    # omp parallel for schedule(static,8)
    for index_p0 in range(nb_particules - 1):
        vector = np.empty(dim)
        rank = omp.get_thread_num()
        position0 = positions[index_p0]
        mass0 = masses[index_p0]
        for index_p1 in range(index_p0 + 1, nb_particules):
            mass1 = masses[index_p1]
            for i in range(dim):
                vector[i] = position0[i] - positions[index_p1, i]
            distance = sqrt(sum(vector ** 2))
            coef = 1.0 / distance ** 3
            for i in range(dim):
                accelerations[rank, index_p0, i] -= coef * mass1 * vector[i]
                accelerations[rank, index_p1, i] += coef * mass0 * vector[i]

    # omp parallel for
    for i_part in range(nb_particules):
        for i_thread in range(1, nthreads):
            for i in range(dim):
                accelerations[0, i_part, i] += accelerations[i_thread, i_part, i]


def get_num_threads():
    nthreads = -1
    # omp parallel
    if 1:
        # omp single
        nthreads = omp.get_num_threads()
    return nthreads


@boost
def loop(
    time_step: float,
    nb_steps: int,
    masses: "float[]",
    positions: "float[:,:]",
    velocities: "float[:,:]",
):

    nthreads = get_num_threads()
    nb_parts, dim = positions.shape

    accelerations = np.zeros([nthreads, nb_parts, dim])
    accelerations1 = np.zeros_like(accelerations)

    compute_accelerations(accelerations, masses, positions)

    time = 0.0
    energy0, _, _ = compute_energies(masses, positions, velocities)
    energy_previous = energy0

    perf_time_pos = 0.0
    perf_time_acc = 0.0
    perf_time_vel = 0.0
    perf_time_swap = 0.0
    perf_time_ener = 0.0

    for step in range(nb_steps):

        t0 = perf_time()
        advance_positions(positions, velocities, accelerations[0], time_step)
        t1 = perf_time()
        perf_time_pos += t1 - t0

        # swap acceleration arrays
        accelerations, accelerations1 = accelerations1, accelerations
        accelerations.fill(0)
        t2 = perf_time()
        perf_time_swap += t2 - t1

        compute_accelerations(accelerations, masses, positions)
        t3 = perf_time()
        perf_time_acc += t3 - t2

        advance_velocities(
            velocities, accelerations[0], accelerations1[0], time_step
        )
        t4 = perf_time()
        perf_time_vel += t4 - t3

        time += time_step

        if not step % 100:
            energy, _, _ = compute_energies(masses, positions, velocities)
            # f-strings supported by Pythran>=0.9.8
            print(
                f"t = {time_step * step:5.2f}, E = {energy:.10f}, "
                f"dE/E = {(energy - energy_previous) / energy_previous:+.10f}"
            )
            energy_previous = energy

        t5 = perf_time()
        perf_time_ener += t5 - t4

    print(
        f"perf_time_pos:  {perf_time_pos:5.2f} s\n"
        f"perf_time_swap: {perf_time_swap:5.2f} s\n"
        f"perf_time_acc:  {perf_time_acc:5.2f} s\n"
        f"perf_time_vel:  {perf_time_vel:5.2f} s\n"
        f"perf_time_ener: {perf_time_ener:5.2f} s\n"
    )

    return energy, energy0


def compute_kinetic_energy(masses, velocities):
    return 0.5 * sum(masses * np.sum(velocities ** 2, 1))


def compute_potential_energy(masses, positions):
    nb_particules = masses.size
    pe = 0.0
    # omp parallel for reduction(+:pe)
    for index_p0 in range(nb_particules - 1):
        vector = np.empty(3)
        mass0 = masses[index_p0]
        position0 = positions[index_p0]
        for index_p1 in range(index_p0 + 1, nb_particules):
            for i in range(3):
                vector[i] = position0[i] - positions[index_p1, i]
            distance = sqrt(sum(vector ** 2))
            pe -= (mass0 * masses[index_p1]) / distance
    return pe


def compute_energies(masses, positions, velocities):
    energy_kin = compute_kinetic_energy(masses, velocities)
    energy_pot = compute_potential_energy(masses, positions)
    return energy_kin + energy_pot, energy_kin, energy_pot


if __name__ == "__main__":

    import sys

    t_start = perf_counter()
    try:
        time_end = float(sys.argv[2])
    except IndexError:
        time_end = 10.0

    time_step = 0.001
    nb_steps = int(time_end / time_step) + 1

    path_input = sys.argv[1]
    masses, positions, velocities = load_input_data(path_input)

    energy, energy0 = loop(time_step, nb_steps, masses, positions, velocities)
    print(f"Final dE/E = {(energy - energy0) / energy0:.6e}")
    print(
        f"{nb_steps} time steps run in {timedelta(seconds=perf_counter()-t_start)}"
    )
