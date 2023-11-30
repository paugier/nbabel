import sys

from math import sqrt
from random import rand, random_float64
from algorithm import vectorize
from memory import memcpy, memset_zero

from python import Python
from time import now

# from datetime import timedelta

from helpers import string_to_float, read_data

# def load_input_data(path: String):
#     pd = Python.import_module("pandas")

#     df = pd.read_csv(
#         path
#         # , names=["mass", "x", "y", "z", "vx", "vy", "vz"], delimiter=r"\s+"
#     )
# masses = df["mass"].values
# positions = df.loc[:, ["x", "y", "z"]].values
# velocities = df.loc[:, ["vx", "vy", "vz"]].values

# return masses, positions, velocities


fn fill_3D_tuple(n: Int) -> StaticTuple[3, DTypePointer[DType.float64]]:
    var result = StaticTuple[3, DTypePointer[DType.float64]]()

    @unroll
    for i in range(3):
        let ptr = DTypePointer[DType.float64].alloc(n)
        rand(ptr, n)
        result[i] = ptr
    return result


struct Particles:
    var nparts: Int
    var position: StaticTuple[3, DTypePointer[DType.float64]]
    var velocity: StaticTuple[3, DTypePointer[DType.float64]]
    var acceleration: StaticTuple[3, DTypePointer[DType.float64]]
    var acceleration1: StaticTuple[3, DTypePointer[DType.float64]]
    var mass: DTypePointer[DType.float64]

    fn __init__(inout self, nparts: Int):
        self.nparts = nparts
        print("creating the particles data")
        self.position = fill_3D_tuple(nparts)
        self.velocity = fill_3D_tuple(nparts)
        self.acceleration = fill_3D_tuple(nparts)
        self.acceleration1 = fill_3D_tuple(nparts)
        self.mass = DTypePointer[DType.float64].alloc(nparts)
        rand(self.mass, nparts)

    fn __del__(owned self):
        #     @unroll
        #     for axis in range(3):
        #         self.position[axis].free()
        #         self.velocity[axis].free()
        #         self.acceleration[axis].free()
        #         self.acceleration1[axis].free()

        self.mass.free()


@always_inline
fn norm_cube[
    _nelts: Int
](
    x: SIMD[DType.float64, _nelts],
    y: SIMD[DType.float64, _nelts],
    z: SIMD[DType.float64, _nelts],
) -> SIMD[DType.float64, _nelts]:
    let norm2_ = norm2[_nelts](x, y, z)
    return norm2_ * sqrt(norm2_)


@always_inline
fn norm2[
    _nelts: Int
](
    x: SIMD[DType.float64, _nelts],
    y: SIMD[DType.float64, _nelts],
    z: SIMD[DType.float64, _nelts],
) -> SIMD[DType.float64, _nelts]:
    return x**2 + y**2 + z**2


alias nelts = 32


fn accelerate(inout particles: Particles):
    let position = particles.position
    let acceleration = particles.acceleration
    let acceleration1 = particles.acceleration1
    let mass = particles.mass
    let nparts = particles.nparts

    # store current acceleration as acceleration1
    @unroll
    for axis in range(3):
        memcpy(acceleration1[axis], acceleration[axis], nparts)
        memset_zero(acceleration[axis], nparts)

    for i0 in range(nparts - 1):

        @parameter
        fn other_particles[_nelts: Int](i_tail: Int):
            let i1 = i0 + i_tail + 1
            let delta_x = position[0].load(i0) - position[0].simd_load[_nelts](i1)
            let delta_y = position[1].load(i0) - position[1].simd_load[_nelts](i1)
            let delta_z = position[2].load(i0) - position[2].simd_load[_nelts](i1)
            let distance_cube = norm_cube(delta_x, delta_y, delta_z)
            let delta = StaticTuple[3, SIMD[DType.float64, _nelts]](
                delta_x, delta_y, delta_z
            )

            @unroll
            for axis in range(3):
                let new_acc_p0 = acceleration[axis].load(i0) - (
                    mass.simd_load[_nelts](i1) / distance_cube * delta[axis]
                ).reduce_add()
                acceleration[axis].store(i0, new_acc_p0)
                let new_acc_p1 = acceleration[axis].simd_load[_nelts](i1) + mass.load(
                    i0
                ) / distance_cube * delta[axis]
                acceleration[axis].simd_store[_nelts](i1, new_acc_p1)

        vectorize[nelts, other_particles](nparts - i0 - 1)


fn advance_positions(inout particles: Particles, time_step: Float64) -> NoneType:
    let position = particles.position
    let velocity = particles.velocity
    let acceleration = particles.acceleration

    for idx in range(particles.nparts):

        @unroll
        for axis in range(3):
            let pos = position[axis].load(idx)
            let vel = velocity[axis].load(idx)
            let acc = acceleration[axis].load(idx)
            position[axis].store(
                idx, pos + time_step * vel + 0.5 * time_step**2 * acc
            )


fn advance_velocities(inout particles: Particles, time_step: Float64) -> NoneType:
    let velocity = particles.velocity
    let acceleration = particles.acceleration
    let acceleration1 = particles.acceleration1

    for idx in range(particles.nparts):

        @unroll
        for axis in range(3):
            let vel = velocity[axis].load(idx)
            let acc = acceleration[axis].load(idx)
            let acc1 = acceleration1[axis].load(idx)
            velocity[axis].store(idx, vel + 0.5 * time_step * (acc + acc1))


fn compute_energy(inout particles: Particles) -> Float64:
    let nb_particules = particles.nparts
    let position = particles.position
    let velocity = particles.velocity
    let mass = particles.mass

    var kinetic = Float64(0.0)
    var potential = Float64(0.0)

    for idx in range(particles.nparts):
        let m = mass.load(idx)

        @unroll
        for axis in range(3):
            let vel = velocity[axis].load(idx)
            kinetic += 0.5 * m * vel**2

    # for i0 in range(nb_particules - 1):
    #     let p0 = particles[i0]
    #     for i1 in range(i0 + 1, nb_particules):
    #         let p1 = particles[i1]
    #         let vector = p0.position - p1.position
    #         let distance = sqrt(norm2(vector))
    #         potential -= (p0.mass * p1.mass) / distance
    return kinetic + potential


fn loop(
    time_step: Float64, nb_steps: Int, inout particles: Particles
) -> (Float64, Float64):
    var energy = compute_energy(particles)
    var old_energy = energy
    let energy0 = energy

    print("energy0", energy0)

    accelerate(particles)
    for step in range(1, nb_steps + 1):
        advance_positions(particles, time_step)
        accelerate(particles)
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

    particles = Particles(nb_particles)

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
    energy, energy0 = loop(time_step, nb_steps, particles)
    print("Final dE/E = " + String((energy - energy0) / energy0))
    print(
        String(nb_steps)
        + " time steps run in "
        + String(Float64(now() - t_start) * 1e-9)
        + " s"
    )
