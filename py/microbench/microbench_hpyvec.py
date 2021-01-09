from time import perf_counter
from math import sqrt

from hpyvec import Vector


class Point(Vector[float].subclass(size=3)):

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]

    @property
    def z(self):
        return self[2]

    def norm(self):
        return sqrt(self.norm2())

    def norm_cube(self):
        norm2 = self.norm2()
        return norm2 * sqrt(norm2)

    def norm2(self):
        return self.x ** 2 + self.y ** 2 + self.z ** 2


Points = Vector[Point]


def compute_accelerations(accelerations, masses, positions):
    nb_particules = len(positions)
    for i0, position0 in enumerate(positions):
        for i1 in range(i0 + 1, nb_particules):
            delta = position0 - positions[i1]
            distance_cube = delta.norm_cube()
            accelerations[i0] -= masses[i1] / distance_cube * delta
            accelerations[i1] += masses[i0] / distance_cube * delta


number_particles = 1000


def main():

    masses = Vector[float].ones(number_particles)
    positions = Points.zeros(number_particles)

    x = 0.0
    for position in positions:
        position.x = x
        x += 1.0

    accelerations = positions.zeros_like()

    compute_accelerations(accelerations, masses, positions)
    t_start = perf_counter()
    compute_accelerations(accelerations, masses, positions)
    clock_time = perf_counter() - t_start

    nb_steps = int(2 / clock_time) or 4
    times = []

    for step in range(nb_steps):
        t_start = perf_counter()
        compute_accelerations(accelerations, masses, positions)
        times.append(perf_counter() - t_start)

    print(f"{Point.__name__}: {min(times) * 1000:.3f} ms")


if __name__ == "__main__":

    main()
