import sys
import numpy as np
from itertools import combinations
from time import perf_counter
from datetime import timedelta


class Particle:
    """
    A Particle has mass, position, velocity and acceleration.
    """

    def __init__(self, mass, x, y, z, vx, vy, vz):
        self.mass = mass
        self.position = np.array([x, y, z])
        self.velocity = np.array([vx, vy, vz])
        self.acceleration = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])

    @property
    def ke(self):
        return 0.5 * self.mass * sum(v ** 2 for v in self.velocity)


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
        self.__accelerate()
        self.__advance_positions(dt)
        self.__accelerate()
        self.__advance_velocities(dt)

    def __accelerate(self):
        for particle in self:
            particle.acceleration[1] = particle.acceleration[0]
            particle.acceleration[0] = 0.0
            self.pe = 0.0
        for p1, p2 in combinations(self, 2):
            vector = np.subtract(p1.position, p2.position)
            distance = np.sqrt(np.sum(vector ** 2))
            p1.acceleration[0] = (
                p1.acceleration[0] - (p2.mass / distance ** 3) * vector
            )
            p2.acceleration[0] = (
                p2.acceleration[0] + (p1.mass / distance ** 3) * vector
            )
            self.pe -= (p1.mass * p2.mass) / distance

    def __advance_positions(self, dt):
        for p in self:
            p.position = (
                p.position + p.velocity * dt + 0.5 * dt ** 2 * p.acceleration[0]
            )

    def __advance_velocities(self, dt):
        for p in self:
            p.velocity = (
                p.velocity + 0.5 * (p.acceleration[0] + p.acceleration[1]) * dt
            )


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
    old_energy = -0.25
    for step in range(1, int(tend / dt + 1)):
        cluster.step(dt)
        if not step % 100:
            print(
                f"t = {dt * step:.2f}, E = {cluster.energy:.10f}, "
                f"dE/E = {(cluster.energy - old_energy) / old_energy:.10f}"
            )
            old_energy = cluster.energy
    print(f"Final dE/E = {(cluster.energy + 0.25) / -0.25:.6e}")
    print(f"run in {timedelta(seconds=perf_counter()-t_start)}")
