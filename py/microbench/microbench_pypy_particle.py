from math import sqrt
from time import perf_counter


class Point3D:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    @classmethod
    def _zero(cls):
        return cls(0.0, 0.0, 0.0)

    def norm(self):
        return sqrt(self.norm2())

    def norm_cube(self):
        norm2 = self.norm2()
        return norm2 * sqrt(norm2)

    def norm2(self):
        return self.x ** 2 + self.y ** 2 + self.z ** 2

    def __repr__(self):
        return f"[{self.x:.10f}, {self.y:.10f}, {self.z:.10f}]"

    def __add__(self, other):
        return Point3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Point3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other):
        return Point3D(other * self.x, other * self.y, other * self.z)

    __rmul__ = __mul__

    def reset_to_0(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0


def make_inlined_point(name):
    x = f"_{name}_x"
    y = f"_{name}_y"
    z = f"_{name}_z"

    def get(self):
        return Point3D(getattr(self, x), getattr(self, y), getattr(self, z))

    def set(self, value):
        setattr(self, x, value.x)
        setattr(self, y, value.y)
        setattr(self, z, value.z)

    return property(get, set)


class Particle:
    position = make_inlined_point("position")
    acceleration = make_inlined_point("acceleration")

    def __init__(self, mass, position, acceleration):
        self.mass = mass
        self.position = position
        self.acceleration = acceleration


def compute_accelerations(particles):
    nb_particules = len(particles)
    for i0 in range(nb_particules - 1):
        for i1 in range(i0 + 1, nb_particules):
            p0 = particles[i0]
            p1 = particles[i1]
            delta = p0.position - p1.position
            distance_cube = delta.norm_cube()
            p0.acceleration -= p1.mass / distance_cube * delta
            p1.acceleration += p0.mass / distance_cube * delta


number_particles = 1000


def main(Point):

    masses = number_particles * [1.0]
    positions = [Point(0.0, 0.0, 0.0) for i in range(number_particles)]

    x = 0.0
    for position in positions:
        position.x = x
        x += 1.0

    particles = [
        Particle(masses[i], positions[i], Point(0.0, 0.0, 0.0))
        for i in range(number_particles)
    ]

    compute_accelerations(particles)
    t_start = perf_counter()
    compute_accelerations(particles)
    clock_time = perf_counter() - t_start

    nb_steps = int(2 / clock_time) or 4
    times = []

    for step in range(nb_steps):
        t_start = perf_counter()
        compute_accelerations(particles)
        times.append(perf_counter() - t_start)

    print(f"{Point.__name__}: {min(times) * 1000:.3f} ms")


if __name__ == "__main__":

    main(Point3D)
