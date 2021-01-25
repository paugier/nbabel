from math import sqrt
import numpy as np

from transonic import boost
from transonic.util import timeit_verbose as timeit

dim = 3


@boost
def compute(
    accelerations: "float[:,:]", masses: "float[:]", positions: "float[:,:]"
):
    nb_particules = masses.size
    vector = np.empty(dim)
    for index_p0 in range(nb_particules - 1):
        position0 = positions[index_p0]
        mass0 = masses[index_p0]
        for index_p1 in range(index_p0 + 1, nb_particules):
            mass1 = masses[index_p1]
            for i in range(dim):
                vector[i] = position0[i] - positions[index_p1, i]
            distance = sqrt(sum(vector ** 2))
            coef = 1.0 / distance ** 3
            for i in range(dim):
                accelerations[index_p0, i] -= coef * mass1 * vector[i]
                accelerations[index_p1, i] += coef * mass0 * vector[i]


@boost
def compute_opt(
    accelerations: "float[:,:]", masses: "float[:]", positions: "float[:,:]"
):
    nb_particules = masses.size
    vector = np.empty(dim)
    for index_p0 in range(nb_particules - 1):
        position0 = positions[index_p0]
        mass0 = masses[index_p0]
        for index_p1 in range(index_p0 + 1, nb_particules):
            for i in range(dim):
                vector[i] = position0[i] - positions[index_p1, i]
            distance2 = sum(vector ** 2)
            distance3 = distance2 * sqrt(distance2)
            coef1 = masses[index_p1] / distance3
            coef0 = mass0 / distance3
            for i in range(dim):
                accelerations[index_p0, i] -= coef1 * vector[i]
                accelerations[index_p1, i] += coef0 * vector[i]


@boost
def compute_opt1(
    accelerations: "float[:,3]", masses: "float[:]", positions: "float[:,3]"
):
    nb_particules = masses.size
    vector = np.empty_like(positions[0])
    acc0 = np.empty_like(accelerations[0])
    for index_p0 in range(nb_particules - 1):
        np.copyto(acc0, accelerations[index_p0])
        for index_p1 in range(index_p0 + 1, nb_particules):
            np.copyto(vector, positions[index_p0] - positions[index_p1])
            distance = sqrt(np.sum(vector ** 2))
            coef = np.power(distance, -3)
            np.copyto(acc0, acc0 + coef * masses[index_p1] * vector)
            accelerations[index_p1] += coef * masses[index_p0] * vector
        accelerations[index_p0] = -acc0


@boost
def compute_opt2(
    accelerations: "float[:,:]", masses: "float[:]", positions: "float[:,:]"
):
    nb_particules = masses.size
    vector = np.empty(dim)
    accs = np.empty(dim)
    for index_p0 in range(nb_particules - 1):
        position0 = positions[index_p0]
        mass0 = masses[index_p0]
        accs.fill(0)
        for index_p1 in range(index_p0 + 1, nb_particules):
            for i in range(dim):
                vector[i] = position0[i] - positions[index_p1, i]
            d2 = 0.0
            for i in range(dim):
                d2 = d2 + vector[i] * vector[i]
            distance3 = d2 * sqrt(d2)
            coef1 = masses[index_p1] / distance3
            coef0 = mass0 / distance3
            for i in range(dim):
                accs[i] = accs[i] + coef1 * vector[i]
                accelerations[index_p1, i] = (
                    accelerations[index_p1, i] + coef0 * vector[i]
                )
        accelerations[index_p0] -= accs


shape = 1024, dim
print("shape=", shape)

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
timeit("compute_opt(accelerations, masses, positions)", globals=glo, norm=norm)

timeit("compute_opt1(accelerations, masses, positions)", globals=glo, norm=norm)
timeit("compute_opt2(accelerations, masses, positions)", globals=glo, norm=norm)


"""
Oh, `pythran -P` gives:
```
coef = (1.0 / (np.square(math.sqrt(builtins.sum(np.square(vector)))) * math.sqrt(builtins.sum(np.square(vector)))))
```
I guess the C++ compiler is smart enough to simplify that, but it's a bit strange...
"""
