import sys

from math import sqrt
from random import rand, random_float64
from algorithm import tile, vectorize
from memory import memcpy, memset_zero
from sys.param_env import env_get_int
from time import now

# from python import Python

# from datetime import timedelta

from helpers import string_to_float, read_data
from particles import Particles, accelerate_tile, accelerate_vectorize


fn accelerate[nelts: Int](inout particles: Particles):
    return accelerate_tile[nelts](particles)
    # return accelerate_vectorize[nelts](particles)


# def load_input_data(path: String):
#     pd = Python.import_module("pandas")
#     # Mojo error: keyword args for Python function call not yet supported
#     df = pd.read_csv(
#         path
#         , names=["mass", "x", "y", "z", "vx", "vy", "vz"], delimiter=r"\s+"
#     )
#     masses = df["mass"].values

#     # Mojo error: invalid call to '__getitem__': index #0 cannot be converted from 'slice' to 'PythonObject'
#     positions = df.loc[:, ["x", "y", "z"]].values
#     velocities = df.loc[:, ["vx", "vy", "vz"]].values

#     return masses, positions, velocities


fn advance_positions(inout particles: Particles, time_step: Float64) -> NoneType:
    let position = particles.position
    let velocity = particles.velocity
    let acceleration = particles.acceleration

    for idx in range(particles.size):

        @unroll
        for axis in range(3):
            let vel = velocity[axis][idx]
            let acc = acceleration[axis][idx]
            position[axis][idx] = (
                position[axis][idx] + time_step * vel + 0.5 * time_step**2 * acc
            )


fn advance_velocities(inout particles: Particles, time_step: Float64) -> NoneType:
    let velocity = particles.velocity
    let acceleration = particles.acceleration
    let acceleration1 = particles.acceleration1

    for idx in range(particles.size):

        @unroll
        for axis in range(3):
            let acc = acceleration[axis][idx]
            let acc1 = acceleration1[axis][idx]
            velocity[axis][idx] = velocity[axis][idx] + 0.5 * time_step * (acc + acc1)


fn compute_energy(inout particles: Particles) -> Float64:
    let nb_particules = particles.size
    let position = particles.position
    let velocity = particles.velocity
    let mass = particles.mass

    var kinetic = Float64(0.0)
    var potential = Float64(0.0)

    for idx in range(particles.size):
        let m = mass[idx]

        @unroll
        for axis in range(3):
            let vel = velocity[axis][idx]
            kinetic += 0.5 * m * vel**2

    for i0 in range(nb_particules - 1):
        let mass0 = mass[i0]
        for i1 in range(i0 + 1, nb_particules):
            let delta_x = position[0][i0] - position[0][i1]
            let delta_y = position[1][i0] - position[1][i1]
            let delta_z = position[2][i0] - position[2][i1]
            let distance = sqrt(delta_x**2 + delta_y**2 + delta_z**2)
            potential -= (mass0 * mass[i1]) / distance
    return kinetic + potential


fn loop[
    nelts: Int
](time_step: Float64, nb_steps: Int, inout particles: Particles) -> (Float64, Float64):
    var energy = compute_energy(particles)
    var old_energy = energy
    let energy0 = energy

    print("energy0", energy0)

    accelerate[nelts](particles)
    for step in range(1, nb_steps + 1):
        advance_positions(particles, time_step)
        accelerate[nelts](particles)
        advance_velocities(particles, time_step)
        if not step % 100:
            energy = compute_energy(particles)
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
    alias nelts = env_get_int["nelts", 4]()

    print("nelts:", nelts)
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

    var particles = Particles(nb_particles)

    let position = particles.position
    let velocity = particles.velocity
    let acceleration = particles.acceleration
    let acceleration1 = particles.acceleration1
    let mass = particles.mass

    for idx_part in range(nb_particles):
        m = data[idx_part, 0]
        x = data[idx_part, 1]
        y = data[idx_part, 2]
        z = data[idx_part, 3]
        vx = data[idx_part, 4]
        vy = data[idx_part, 5]
        vz = data[idx_part, 6]

        mass.store(idx_part, m)

        position[0].store(idx_part, x)
        position[1].store(idx_part, y)
        position[2].store(idx_part, z)

        velocity[0].store(idx_part, vx)
        velocity[1].store(idx_part, vy)
        velocity[2].store(idx_part, vz)

        @unroll
        for axis in range(3):
            acceleration[axis].store(idx_part, 0.0)
            acceleration1[axis].store(idx_part, 0.0)

    # masses, positions, velocities = load_input_data(path_input)

    let energy: Float64
    let energy0: Float64

    let t_start = now()
    energy, energy0 = loop[nelts](time_step, nb_steps, particles)
    print(
        "(E - E_init) / E_init = " + String(100 * (energy - energy0) / energy0) + " %"
    )
    print(
        String(nb_steps)
        + " time steps run in "
        + String(Float64(now() - t_start) * 1e-9)
        + " s"
    )
