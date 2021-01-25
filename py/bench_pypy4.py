from math import sqrt
from time import perf_counter
from datetime import timedelta

from vector import Vector


class Point3D:
    @classmethod
    def _zero(cls):
        return cls(0.0, 0.0, 0.0)

    def norm(self):
        return sqrt(self.norm2())

    def norm_cube(self):
        norm2 = self.norm2()
        return norm2 * sqrt(norm2)

    def __repr__(self):
        return f"[{self.x:.10f}, {self.y:.10f}, {self.z:.10f}]"

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def norm2(self):
        return self.x ** 2 + self.y ** 2 + self.z ** 2

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


class Points(Vector):
    def reset_to_0(self):
        for point in self:
            point.reset_to_0()

    def compute_squares(self):
        result = []
        for point in self:
            result.append(point.norm2())
        return result


def load_input_data(path):

    masses = []
    positions_tuples = []
    velocities_tuples = []

    with open(path) as input_file:
        for line in input_file:
            if not line.strip():
                continue

            mass, x, y, z, vx, vy, vz = [float(x) for x in line.split()[1:]]
            masses.append(mass)
            positions_tuples.append((x, y, z))
            velocities_tuples.append((vx, vy, vz))

    number_particles = len(masses)

    VectorPoints = Points[Point3D]

    positions = VectorPoints.empty(number_particles)
    velocities = VectorPoints.empty(number_particles)

    for index in range(number_particles):
        positions[index] = Point3D(*[n for n in positions_tuples[index]])
        velocities[index] = Point3D(*[n for n in velocities_tuples[index]])

    return masses, positions, velocities


def advance_positions(positions, velocities, accelerations, time_step):
    for i in range(len(positions)):
        positions[i] += (
            time_step * velocities[i] + 0.5 * time_step ** 2 * accelerations[i]
        )


def advance_velocities(velocities, accelerations, accelerations1, time_step):
    for i in range(len(positions)):
        velocities[i] += 0.5 * time_step * (accelerations[i] + accelerations1[i])


def compute_accelerations(accelerations, masses, positions):
    """
    This needs to be very efficient!! >90% of the time spent here.

    In Julia, the loops are written::

      @inbounds for i = 1:N - 1
      @simd for j = i + 1:N

    However, `@inbounds` and `@simd` do not seem to be very important for
    performance in this case.

    """
    nb_particules = len(masses)
    for i0 in range(nb_particules - 1):
        mass0 = masses[i0]
        position0 = positions[i0]
        for i1 in range(i0 + 1, nb_particules):
            mass1 = masses[i1]
            position1 = positions[i1]
            delta = position0 - position1
            distance_cube = delta.norm_cube()
            accelerations[i0] -= mass1 / distance_cube * delta
            accelerations[i1] += mass0 / distance_cube * delta


def loop(time_step: float, nb_steps: int, masses, positions, velocities):

    accelerations = positions.zeros_like()
    accelerations1 = positions.zeros_like()

    compute_accelerations(accelerations, masses, positions)

    time = 0.0
    energy0, _, _ = compute_energies(masses, positions, velocities)
    energy_previous = energy0

    for step in range(nb_steps):
        advance_positions(positions, velocities, accelerations, time_step)
        # swap acceleration arrays
        accelerations, accelerations1 = accelerations1, accelerations
        accelerations.reset_to_0()
        compute_accelerations(accelerations, masses, positions)
        advance_velocities(velocities, accelerations, accelerations1, time_step)
        time += time_step

        if not step % 100:
            energy, _, _ = compute_energies(masses, positions, velocities)
            print(
                f"t = {time_step * step:4.2f}, E = {energy:.6f}, "
                f"dE/E = {(energy - energy_previous) / energy_previous:+.6e}"
            )
            energy_previous = energy

    return energy, energy0


def compute_kinetic_energy(masses, velocities):
    return 0.5 * sum(
        m * v2 for m, v2 in zip(masses, velocities.compute_squares())
    )


def compute_potential_energy(masses, positions):
    nb_particules = len(masses)
    pe = 0.0
    for i0 in range(nb_particules - 1):
        mass0 = masses[i0]
        position0 = positions[i0]
        for i1 in range(i0 + 1, nb_particules):
            mass1 = masses[i1]
            position1 = positions[i1]
            delta = position0 - position1
            distance = delta.norm()
            pe -= (mass0 * mass1) / distance
    return pe


def compute_energies(masses, positions, velocities):
    energy_kin = compute_kinetic_energy(masses, velocities)
    energy_pot = compute_potential_energy(masses, positions)
    return energy_kin + energy_pot, energy_kin, energy_pot


if __name__ == "__main__":

    import sys

    t_start = perf_counter()
    try:
        time_end = float(sys.argv[2])
    except IndexError:
        time_end = 10.0

    time_step = 0.001
    nb_steps = int(time_end / time_step) + 1

    path_input = sys.argv[1]
    masses, positions, velocities = load_input_data(path_input)

    energy, energy0 = loop(time_step, nb_steps, masses, positions, velocities)
    print(f"Final dE/E = {(energy - energy0) / energy0:.6e}")
    print(
        f"{nb_steps} time steps run in {timedelta(seconds=perf_counter()-t_start)}"
    )
