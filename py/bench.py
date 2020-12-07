from math import sqrt
from time import perf_counter
from datetime import timedelta

import numpy as np
import pandas as pd

from transonic import boost


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
    positions += time_step * velocities + 0.5 * time_step ** 2 * accelerations


def advance_velocities(velocities, accelerations, accelerations1, time_step):
    velocities += 0.5 * time_step * (accelerations + accelerations1)


def compute_distance(vec):
    # with pythran>=0.9.8, good perf with
    return sqrt(sum(vec ** 2))


def compute_accelerations(accelerations, masses, positions):
    nb_particules = masses.size
    vector = np.empty(3)
    for index_p0 in range(nb_particules - 1):
        position0 = positions[index_p0]
        mass0 = masses[index_p0]
        for index_p1 in range(index_p0 + 1, nb_particules):
            mass1 = masses[index_p1]
            for i in range(3):
                vector[i] = position0[i] - positions[index_p1, i]
            distance = compute_distance(vector)
            coef = 1.0 / distance ** 3
            for i in range(3):
                accelerations[index_p0, i] -= coef * mass1 * vector[i]
                accelerations[index_p1, i] += coef * mass0 * vector[i]


@boost
def loop(
    time_step: float,
    nb_steps: int,
    masses: "float[]",
    positions: "float[:,:]",
    velocities: "float[:,:]",
):

    accelerations = np.zeros_like(positions)
    accelerations1 = np.zeros_like(positions)

    compute_accelerations(accelerations, masses, positions)

    time = 0.0
    energy0, _, _ = compute_energies(masses, positions, velocities)
    energy_previous = energy0

    for step in range(nb_steps):
        advance_positions(positions, velocities, accelerations, time_step)
        # swap acceleration arrays
        accelerations, accelerations1 = accelerations1, accelerations
        accelerations.fill(0)
        compute_accelerations(accelerations, masses, positions)
        advance_velocities(velocities, accelerations, accelerations1, time_step)
        time += time_step

        if not step % 100:
            energy, energy_kin, energy_pot = compute_energies(
                masses, positions, velocities
            )
            # f-strings supported by Pythran>=0.9.8
            print(
                f"t = {time_step * step:.2f}, E = {energy:.10f}, "
                f"dE/E = {(energy - energy_previous) / energy_previous:.10f}"
            )
            energy_previous = energy

    return energy, energy0


def compute_kinetic_energy(masses, velocities):
    return 0.5 * np.sum(masses * np.sum(velocities ** 2, 1))


def compute_potential_energy(masses, positions):
    nb_particules = masses.size
    pe = 0.0
    for index_p0 in range(nb_particules - 1):
        for index_p1 in range(index_p0 + 1, nb_particules):
            mass0 = masses[index_p0]
            mass1 = masses[index_p1]
            vector = positions[index_p0] - positions[index_p1]
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
    time_end, time_step = 10.0, 0.001
    nb_steps = int(time_end / time_step) + 1

    path_input = sys.argv[1]
    masses, positions, velocities = load_input_data(path_input)

    energy, energy0 = loop(time_step, nb_steps, masses, positions, velocities)
    print(f"Final dE/E = {(energy - energy0) / energy0:.6e}")
    print(
        f"{nb_steps} time steps run in {timedelta(seconds=perf_counter()-t_start)}"
    )
