import sys

from math import sqrt
from python import Python
from utils.vector import InlinedFixedVector
from time import now

# from datetime import timedelta

from helpers import string_to_float, read_data

alias Vec4floats = SIMD[DType.float64, 4]
alias VecVec4floats = InlinedFixedVector[Vec4floats]


fn norm(vec: Vec4floats) -> Float64:
    return sqrt(norm2(vec))


fn norm_cube(vec: Vec4floats) -> Float64:
    let norm2_ = norm2(vec)
    return norm2_ * sqrt(norm2_)


fn norm2(vec: Vec4floats) -> Float64:
    return vec[0] ** 2 + vec[1] ** 2 + vec[2] ** 2 + vec[3] ** 2


fn accelerate(
    masses: InlinedFixedVector[Float64],
    inout accelerations: VecVec4floats,
    inout accelerations1: VecVec4floats,
    positions: VecVec4floats,
) -> NoneType:
    let nb_particules = len(masses)

    accelerations1 = accelerations
    for idx_part in range(nb_particules):
        accelerations[idx_part] = Vec4floats(0)

    for i0 in range(nb_particules):
        let m0 = masses[0]
        for i1 in range(i0 + 1, nb_particules):
            let delta = positions[i0] - positions[i1]
            let distance_cube = norm_cube(delta)
            let m1 = masses[i1]
            accelerations[i0] -= m1 / distance_cube * delta
            accelerations[i1] += m0 / distance_cube * delta


fn advance_positions(
    inout positions: VecVec4floats,
    velocities: VecVec4floats,
    accelerations: VecVec4floats,
    time_step: Float64,
):
    let nb_particules = len(positions)
    for idx in range(nb_particules):
        positions[idx] += (
            time_step * velocities[idx] + 0.5 * time_step**2 * accelerations[idx]
        )


fn advance_velocities(
    inout velocities: VecVec4floats,
    accelerations: VecVec4floats,
    accelerations1: VecVec4floats,
    time_step: Float64,
):
    let nb_particules = len(velocities)
    for idx in range(nb_particules):
        velocities[idx] += 0.5 * time_step * (accelerations[idx] + accelerations1[idx])


fn kinetic_energy_part(mass: Float64, velocity: Vec4floats) -> Float64:
    return 0.5 * mass * norm2(velocity)


fn compute_energy(
    masses: InlinedFixedVector[Float64],
    positions: VecVec4floats,
    velocities: VecVec4floats,
) -> Float64:
    let nb_particules = len(masses)

    var kinetic = Float64(0.0)
    for idx in range(nb_particules):
        kinetic += kinetic_energy_part(masses[idx], velocities[idx])

    var potential = Float64(0.0)
    for i0 in range(nb_particules):
        for i1 in range(i0 + 1, nb_particules):
            let vector = positions[i0] - positions[i1]
            let distance = sqrt(norm2(vector))
            potential -= (masses[i0] * masses[i1]) / distance
    return kinetic + potential


fn loop(
    time_step: Float64,
    nb_steps: Int,
    masses: InlinedFixedVector[Float64],
    inout positions: VecVec4floats,
    inout velocities: VecVec4floats,
) -> (Float64, Float64):
    var energy = compute_energy(masses, positions, velocities)
    var old_energy = energy
    let energy0 = energy

    print("energy0 =", energy0)

    var accelerations = VecVec4floats(len(masses))
    for idx_part in range(len(masses)):
        accelerations[idx_part] = Vec4floats(0)
    var accelerations1 = accelerations

    accelerate(masses, accelerations, accelerations1, positions)
    for step in range(1, nb_steps + 1):
        advance_positions(positions, velocities, accelerations, time_step)
        accelerate(masses, accelerations, accelerations1, positions)
        advance_velocities(velocities, accelerations, accelerations1, time_step)
        if not step % 100:
            energy = compute_energy(masses, positions, velocities)
            print(
                "t = "
                + String(time_step * step)
                + ", E = "
                + String(energy)
                + ", dE/E = "
                + String((energy - old_energy) / old_energy)
            )
            old_energy = energy

    return energy, energy0


def main():
    args = sys.argv()

    let time_end: Float64
    if len(args) > 2:
        time_end = string_to_float(args[2])
    else:
        time_end = 10.0

    time_step = 0.001
    nb_steps = (time_end / time_step).to_int() + 1

    path_input = args[1]
    print(path_input)

    data = read_data(path_input)

    nb_particles = data.n0

    masses = InlinedFixedVector[Float64](nb_particles)
    positions = VecVec4floats(nb_particles)
    velocities = VecVec4floats(nb_particles)

    for idx_part in range(nb_particles):
        m = data[idx_part, 0]
        x = data[idx_part, 1]
        y = data[idx_part, 2]
        z = data[idx_part, 3]
        vx = data[idx_part, 4]
        vy = data[idx_part, 5]
        vz = data[idx_part, 6]

        masses.append(m)

        positions.append(Vec4floats(x, y, z, 0))

        velocities.append(Vec4floats(vx, vy, vz, 0))

    let energy: Float64
    let energy0: Float64

    let t_start = now()
    energy, energy0 = loop(time_step, nb_steps, masses, positions, velocities)
    print("(E - E_init) / E_init = " + String(100 * (energy - energy0) / energy0) + " %")
    print(
        String(nb_steps)
        + " time steps run in "
        + String(Float64(now() - t_start) * 1e-9)
        + " s"
    )
