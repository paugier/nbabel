from math import sqrt
import numpy as np

import omp

from transonic import boost
from transonic.util import timeit_verbose as timeit

dim = 3


@boost
def compute(
    accelerations: "float[:, :,:]", masses: "float[:]", positions: "float[:,:]"
):
    nb_particules = masses.size
    vector = np.empty(dim)

    nthreads = accelerations.shape[0]

    # omp parallel for schedule(static,8)
    for index_p0 in range(nb_particules - 1):
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

    # omp parallel for schedule(static,8)
    for index_p0 in range(nb_particules - 1):
        for i_thread in range(1, nthreads):
            for i in range(dim):
                accelerations[0, index_p0, i] += accelerations[i_thread, index_p0, i]


@boost
def get_num_threads():
    nthreads = -1
    # omp parallel
    if 1:
        # omp single
        nthreads = omp.get_num_threads()
    return nthreads


shape = 1024, dim
print("shape=", shape)
nthreads = get_num_threads()
print(nthreads)

masses = np.zeros(shape[0])
positions = np.zeros(shape)
velocities = np.zeros_like(positions)

accelerations = np.zeros([nthreads, shape[0], dim])

x = 0.0
for ip in range(shape[0]):
    positions[ip, 0] = x
    x += 1.0

glo = globals()
norm = timeit("compute(accelerations, masses, positions)", globals=glo)
# timeit("compute_opt(accelerations, masses, positions)", globals=glo, norm=norm)
