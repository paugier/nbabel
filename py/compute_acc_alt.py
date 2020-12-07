from math import sqrt
import numpy as np


def compute_accelerations_alt(accelerations, masses, positions):
    """
    Alternative implementation (more computation but better for OMP)

    It seems that the C++ implementation uses this method.
    """
    nb_particules = masses.size
    for index_p0 in range(nb_particules):
        position0 = positions[index_p0]
        acceleration = np.zeros_like(position0)
        for index_p1 in range(nb_particules):
            if index_p1 == index_p0:
                continue
            vector = position0 - positions[index_p1]
            distance = sqrt(sum(vector ** 2))
            acceleration -= (masses[index_p1] / distance ** 3) * vector
        accelerations[index_p0] = acceleration


def compute_accelerations_alt_lowlevel(accelerations, masses, positions):
    """
    Alternative implementation (more computation but better for OMP)

    It seems that the C++ implementation uses this method.
    """
    nb_particules = masses.size
    vector = np.empty(3)
    for index_p0 in range(nb_particules):
        position0 = positions[index_p0]
        acceleration = np.zeros_like(position0)
        for index_p1 in range(nb_particules):
            if index_p1 == index_p0:
                continue
            for i in range(3):
                vector[i] = position0[i] - positions[index_p1, i]
            distance = compute_distance(vector)
            for i in range(3):
                acceleration[i] -= (masses[index_p1] / distance ** 3) * vector[i]
        for i in range(3):
            accelerations[index_p0, i] = acceleration[i]
