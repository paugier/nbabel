import sys
import numpy
from itertools import combinations


class Particle(object):
    """
    A Particle has mass, position, velocity and acceleration.
    """

    def __init__(self, mass, x, y, z, vx, vy, vz):
        self.mass = mass
        self.position = numpy.array([x, y, z])
        self.velocity = numpy.array([vx, vy, vz])
        self.acceleration = numpy.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])

    @property
    def ke(self):
        return 0.5 * self.mass * numpy.sum(v ** 2 for v in self.velocity)


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
            vector = numpy.subtract(p1.position, p2.position)
            distance = numpy.sqrt(numpy.sum(vector ** 2))
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
        if not step % 10:
            print(
                "t = %.2f, E = % .10f, dE/E = % .10f"
                % (
                    dt * step,
                    cluster.energy,
                    (cluster.energy - old_energy) / old_energy,
                )
            )
            old_energy = cluster.energy
    print("Final dE/E = %.6e" % ((cluster.energy + 0.25) / -0.25))
