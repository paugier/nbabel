from math import sqrt
from time import perf_counter
from datetime import timedelta

import numpy as np
import pandas as pd

from piconumpy_purepy import array, Vectors


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
    coef2 = 0.5 * time_step ** 2
    for i in range(len(velocities)):
        positions[i] += time_step * velocities[i] + coef2 * accelerations[i]


def advance_velocities(velocities, accelerations, accelerations1, time_step):
    coef = 0.5 * time_step
    for i in range(len(velocities)):
        velocities[i] += coef * (accelerations[i] + accelerations1[i])


def compute_distance(vec):
    tmp = 0.0
    for i in range(3):
        tmp += vec[i] ** 2
    return sqrt(tmp)


def compute_accelerations_lowlevel(accelerations, masses, positions):
    nb_particules = masses.size
    vector = [0.0, 0.0, 0.0]
    for index_p0 in range(nb_particules - 1):
        position0 = positions.get_vector(index_p0)
        mass0 = masses[index_p0]
        for index_p1 in range(index_p0 + 1, nb_particules):
            mass1 = masses[index_p1]
            position1 = positions.get_vector(index_p1)
            for i in range(3):
                vector[i] = position0[i] - position1[i]
            distance = compute_distance(vector)
            coef = 1.0 / distance ** 3
            for i in range(3):
                accelerations[3 * index_p0 + i] -= coef * mass1 * vector[i]
                accelerations[3 * index_p1 + i] += coef * mass0 * vector[i]


def loop(
    time_step: float,
    nb_steps: int,
    masses: "float[]",
    positions: "float[:,:]",
    velocities: "float[:,:]",
):

    accelerations = Vectors(np.zeros(positions.size))
    accelerations1 = Vectors(np.zeros(positions.size))

    compute_acc = compute_accelerations_lowlevel
    # compute_acc = compute_accelerations_alt_lowlevel
    # compute_acc = compute_accelerations
    # compute_acc = compute_accelerations_alt

    compute_acc(accelerations, masses, positions)

    time = 0.0
    energy0, _, _ = compute_energies(masses, positions, velocities)
    energy_previous = energy0

    for step in range(nb_steps):
        advance_positions(positions, velocities, accelerations, time_step)
        # swap acceleration arrays
        accelerations, accelerations1 = accelerations1, accelerations
        accelerations.fill(0)
        compute_acc(accelerations, masses, positions)
        advance_velocities(velocities, accelerations, accelerations1, time_step)
        time += time_step

        if not step % 100:
            energy, energy_kin, energy_pot = compute_energies(
                masses, positions, velocities
            )
            # no f-strings and format because not supported by Pythran
            print(
                "t = %4.2f, E = %.6f, " % (time_step * step, energy)
                + "dE/E = %+.6e" % ((energy - energy_previous) / energy_previous)
            )
            # alternative for Numba (doesn't support string formatting!)
            # print(time_step * step, energy, (energy - energy_previous) / energy_previous)
            energy_previous = energy

    return energy, energy0


def compute_kinetic_energy(masses, velocities):
    return 0.5 * sum(
        m * v2 for m, v2 in zip(masses, velocities.compute_squares())
    )


def compute_potential_energy(masses, positions):
    nb_particules = masses.size
    pe = 0.0
    for index_p0 in range(nb_particules - 1):
        for index_p1 in range(index_p0 + 1, nb_particules):
            mass0 = masses[index_p0]
            mass1 = masses[index_p1]
            position0 = positions.get_vector(index_p0)
            position1 = positions.get_vector(index_p1)
            vector = [p0 - p1 for p0, p1 in zip(position0, position1)]
            distance = compute_distance(vector)
            pe -= (mass0 * mass1) / distance
    return pe


def compute_energies(masses, positions, velocities):
    energy_kin = compute_kinetic_energy(masses, velocities)
    energy_pot = compute_potential_energy(masses, positions)
    return energy_kin + energy_pot, energy_kin, energy_pot


if __name__ == "__main__":

    import sys

    t_start = perf_counter()
    time_end, time_step = 1.0, 0.001
    nb_steps = int(time_end / time_step) + 1

    path_input = sys.argv[1]
    masses, positions, velocities = load_input_data(path_input)

    masses = array(masses)
    positions = Vectors(positions.flatten())
    velocities = Vectors(velocities.flatten())

    energy, energy0 = loop(time_step, nb_steps, masses, positions, velocities)
    print(f"Final dE/E = {(energy - energy0) / energy0:.6e}")
    print(
        f"{nb_steps} time steps run in {timedelta(seconds=perf_counter()-t_start)}"
    )
