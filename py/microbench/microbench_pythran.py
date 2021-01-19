from math import sqrt
import numpy as np

from transonic import boost
from transonic.util import timeit_verbose as timeit


@boost
def compute(accelerations: "float[:,3]", masses: "float[:]", positions: "float[:,3]"):
    nb_particules = masses.size
    vector = np.empty(3)
    for index_p0 in range(nb_particules - 1):
        position0 = positions[index_p0]
        mass0 = masses[index_p0]
        for index_p1 in range(index_p0 + 1, nb_particules):
            mass1 = masses[index_p1]
            for i in range(3):
                vector[i] = position0[i] - positions[index_p1, i]
            distance = sqrt(sum(vector ** 2))
            coef = 1.0 / distance ** 3
            for i in range(3):
                accelerations[index_p0, i] -= coef * mass1 * vector[i]
                accelerations[index_p1, i] += coef * mass0 * vector[i]


@boost
def compute2(accelerations: "float[:,3]", masses: "float[:]", positions: "float[:,3]"):
    nb_particules = masses.size
    vector = np.empty(3)
    for index_p0 in range(nb_particules - 1):
        position0 = positions[index_p0]
        mass0 = masses[index_p0]
        for index_p1 in range(index_p0 + 1, nb_particules):
            for i in range(3):
                vector[i] = position0[i] - positions[index_p1, i]
            distance2 = sum(vector ** 2)
            distance3 = distance2 * sqrt(distance2)
            coef1 = masses[index_p1] / distance3
            coef0 = mass0 / distance3
            for i in range(3):
                accelerations[index_p0, i] -= coef1 * vector[i]
                accelerations[index_p1, i] += coef0 * vector[i]


shape = 1024, 3

masses = np.zeros(shape[0])
positions = np.zeros(shape)
velocities = np.zeros_like(positions)
accelerations = np.zeros_like(positions)

x = 0.0
for ip in range(shape[0]):
    positions[ip, 0] = x
    x += 1.0


glo = globals()
norm = timeit("compute(accelerations, masses, positions)", globals=glo)
timeit("compute2(accelerations, masses, positions)", globals=glo, norm=norm)
