import sys

from math import sqrt
from python import Python
from utils.vector import InlinedFixedVector
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


alias Vec4floats = SIMD[DType.float64, 4]
alias vec4zeros = Vec4floats(0)
alias VecParticles = InlinedFixedVector[Particle]


@register_passable("trivial")
struct Particle:
    var position: Vec4floats
    var velocity: Vec4floats
    var acceleration: Vec4floats
    var acceleration1: Vec4floats
    var mass: Float64

    fn __init__(
        pos: Vec4floats,
        vel: Vec4floats,
        mass: Float64,
    ) -> Self:
        return Self {
            position: pos,
            velocity: vel,
            acceleration: vec4zeros,
            acceleration1: vec4zeros,
            mass: mass,
        }

    # not yet supported...
    fn __str__(self) -> String:
        # Mojo is still very basic for string formatting
        return (
            "Particle(mass="
            + String(self.mass)
            + ", position="
            + String(self.position)
            + ", velocity="
            + String(self.velocity)
            + ", ...)"
        )

    fn kinetic_energy(self) -> Float64:
        return 0.5 * self.mass * norm2(self.velocity)


fn norm(vec: Vec4floats) -> Float64:
    return sqrt(norm2(vec))


fn norm_cube(vec: Vec4floats) -> Float64:
    let norm2_ = norm2(vec)
    return norm2_ * sqrt(norm2_)


fn norm2(vec: Vec4floats) -> Float64:
    return vec[0] ** 2 + vec[1] ** 2 + vec[2] ** 2 + vec[3] ** 2


fn accelerate(inout particles: VecParticles) -> NoneType:
    for idx in range(len(particles)):
        var particle = particles[idx]
        particle.acceleration1 = particle.acceleration
        particle.acceleration = Vec4floats(0)
        particles[idx] = particle

    let nb_particules = len(particles)
    for i0 in range(nb_particules):
        var p0 = particles[i0]
        for i1 in range(i0 + 1, nb_particules):
            var p1 = particles[i1]
            let delta = p0.position - p1.position
            let distance_cube = norm_cube(delta)
            p0.acceleration -= p1.mass / distance_cube * delta
            p1.acceleration += p0.mass / distance_cube * delta

            particles[i0] = p0
            particles[i1] = p1


fn advance_positions(inout particles: VecParticles, time_step: Float64) -> NoneType:
    for idx in range(len(particles)):
        var p = particles[idx]
        p.position += time_step * p.velocity + 0.5 * time_step**2 * p.acceleration
        particles[idx] = p


fn advance_velocities(inout particles: VecParticles, time_step: Float64) -> NoneType:
    for idx in range(len(particles)):
        var p = particles[idx]
        p.velocity += 0.5 * time_step * (p.acceleration + p.acceleration1)
        particles[idx] = p


fn compute_energy(inout particles: VecParticles) -> Float64:
    var kinetic = Float64(0.0)
    for p in particles:
        kinetic += p.kinetic_energy()

    var potential = Float64(0.0)
    let nb_particules = len(particles)

    for i0 in range(nb_particules):
        let p0 = particles[i0]
        for i1 in range(i0 + 1, nb_particules):
            let p1 = particles[i1]
            let vector = p0.position - p1.position
            let distance = sqrt(norm2(vector))
            potential -= (p0.mass * p1.mass) / distance
    return kinetic + potential


fn loop(
    time_step: Float64, nb_steps: Int, inout particles: VecParticles
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

    particles = InlinedFixedVector[Particle](nb_particles)

    for idx_part in range(nb_particles):
        m = data[idx_part, 0]
        x = data[idx_part, 1]
        y = data[idx_part, 2]
        z = data[idx_part, 3]
        vx = data[idx_part, 4]
        vy = data[idx_part, 5]
        vz = data[idx_part, 6]

        particles.append(Particle(Vec4floats(x, y, z, 0), Vec4floats(vx, vy, vz, 0), m))

    if len(particles) != nb_particles:
        raise Error("len(particles) != nb_particles")

    # masses, positions, velocities = load_input_data(path_input)

    let energy: Float64
    let energy0: Float64

    let t_start = now()
    energy, energy0 = loop(time_step, nb_steps, particles)
    print("(E - E_init) / E_init = " + String(100 * (energy - energy0) / energy0) + " %")
    print(
        String(nb_steps)
        + " time steps run in "
        + String(Float64(now() - t_start) * 1e-9)
        + " s"
    )
