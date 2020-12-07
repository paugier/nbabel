import sys
from itertools import combinations
from math import sqrt
from time import perf_counter
from datetime import timedelta

import piconumpy_purepy as np


class Particle:
    """
    A Particle has mass, position, velocity and acceleration.
    """

    def __init__(self, mass, x, y, z, vx, vy, vz):
        self.mass = mass
        self.position = np.array([x, y, z])
        self.velocity = np.array([vx, vy, vz])
        self.acceleration = np.array([0.0, 0.0, 0.0])
        self.acceleration1 = np.array([0.0, 0.0, 0.0])

    @property
    def ke(self):
        return 0.5 * self.mass * (self.velocity ** 2).sum()


class Cluster(list):
    """
    A Cluster is just a list of particles with methods to accelerate and
    advance them.
    """

    @property
    def ke(self):
        return sum(particle.ke for particle in self)

    @property
    def energy(self):
        return self.ke + self.pe

    def step(self, dt):
        self.__advance_positions(dt)
        self.accelerate()
        self.__advance_velocities(dt)

    def accelerate(self):
        for particle in self:
            particle.acceleration1 = particle.acceleration
            particle.acceleration = np.array([0.0, 0.0, 0.0])
        pe = 0.0
        for p1, p2 in combinations(self, 2):
            vector = p1.position - p2.position
            distance_square = (vector ** 2).sum()
            distance = sqrt(distance_square)
            distance_cube = distance_square * distance
            p1.acceleration -= (p2.mass / distance_cube) * vector
            p2.acceleration += (p1.mass / distance_cube) * vector
            pe -= (p1.mass * p2.mass) / distance
        self.pe = pe

    def __advance_positions(self, dt):
        for p in self:
            p.position += dt * p.velocity + 0.5 * dt ** 2 * p.acceleration

    def __advance_velocities(self, dt):
        for p in self:
            p.velocity += 0.5 * dt * (p.acceleration + p.acceleration1)


if __name__ == "__main__":

    t_start = perf_counter()
    tend, dt = 10.0, 0.001  # end time, timestep
    cluster = Cluster()
    with open(sys.argv[1]) as input_file:
        for line in input_file:
            # try/except is a blunt instrument to clean up input
            try:
                cluster.append(Particle(*[float(x) for x in line.split()[1:]]))
            except:
                pass

    old_energy = energy0 = -0.25
    cluster.accelerate()
    for step in range(1, int(tend / dt + 1)):
        cluster.step(dt)
        if not step % 100:
            print(
                f"t = {dt * step:.2f}, E = {cluster.energy:.10f}, "
                f"dE/E = {(cluster.energy - old_energy) / old_energy:.10f}"
            )
            old_energy = cluster.energy
    print(f"Final dE/E = {(cluster.energy - energy0) / energy0:.6e}")

    print(f"run in {timedelta(seconds=perf_counter()-t_start)}")
