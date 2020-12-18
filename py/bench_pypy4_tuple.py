from math import sqrt
from time import perf_counter
from datetime import timedelta

import pandas as pd

from vector import Vector


class PointND(tuple):
    @classmethod
    def _zero(cls):
        return cls(0.0, 0.0, 0.0)

    def norm(self):
        return sqrt(self.norm2())

    def norm_cube(self):
        norm2 = self.norm2()
        return norm2 * sqrt(norm2)

    def __repr__(self):
        return f"({self[0]:.10f}, {self[1]:.10f}, {self[2]:.10f})"


class Point4D(PointND):
    def __new__(cls, x, y, z, w=0.0):
        return super(Point4D, cls).__new__(cls, (x, y, z, w))

    def norm2(self):
        return self[0] ** 2 + self[1] ** 2 + self[2] ** 2 + self[3] ** 2

    def __add__(self, other):
        return Point4D(
            self[0] + other[0],
            self[1] + other[1],
            self[2] + other[2],
            self[3] + other[3],
        )

    def __sub__(self, other):
        return Point4D(
            self[0] - other[0],
            self[1] - other[1],
            self[2] - other[2],
            self[3] - other[3],
        )

    def __mul__(self, other):
        return Point4D(
            other * self[0], other * self[1], other * self[2], other * self[3]
        )

    __rmul__ = __mul__

    def __repr__(self):
        return f"[{self[0]:.10f}, {self[1]:.10f}, {self[2]:.10f}]"


class Point3D(PointND):
    def __new__(cls, x, y, z):
        return super(Point3D, cls).__new__(cls, (x, y, z))

    def norm2(self):
        return self[0] ** 2 + self[1] ** 2 + self[2] ** 2

    def __add__(self, other):
        return Point3D(self[0] + other[0], self[1] + other[1], self[2] + other[2])

    def __sub__(self, other):
        return Point3D(self[0] - other[0], self[1] - other[1], self[2] - other[2])

    def __mul__(self, other):
        return Point3D(other * self[0], other * self[1], other * self[2])

    __rmul__ = __mul__


class Points(Vector):
    def reset_to_0(self):
        for i in range(len(self)):
            self[i] = self.dtype._zero()

    def compute_squares(self):
        result = []
        for point in self:
            result.append(point.norm2())
        return result


def load_input_data(path):
    df = pd.read_csv(
        path, names=["mass", "x", "y", "z", "vx", "vy", "vz"], delimiter=r"\s+"
    )

    masses_np = df["mass"].values
    positions_np = df.loc[:, ["x", "y", "z"]].values
    velocities_np = df.loc[:, ["vx", "vy", "vz"]].values

    number_particles = len(masses_np)

    masses = []
    positions = []
    velocities = []

    Point = Point3D
    Points_ = Points[Point]

    positions = Points_.empty(number_particles)
    velocities = Points_.empty(number_particles)

    for index, mass in enumerate(masses_np):
        masses.append(float(mass))
        positions[index] = Point(*[float(n) for n in positions_np[index]])
        velocities[index] = Point(*[float(n) for n in velocities_np[index]])

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
    time_end, time_step = 10.0, 0.001
    nb_steps = int(time_end / time_step) + 1

    path_input = sys.argv[1]
    masses, positions, velocities = load_input_data(path_input)

    energy, energy0 = loop(time_step, nb_steps, masses, positions, velocities)
    print(f"Final dE/E = {(energy - energy0) / energy0:.6e}")
    print(
        f"{nb_steps} time steps run in {timedelta(seconds=perf_counter()-t_start)}"
    )
