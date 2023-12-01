from math import sqrt
from random import rand, random_float64
from algorithm import vectorize, tile
from memory import memcpy, memset_zero
from testing import assert_equal, assert_almost_equal

import benchmark

alias Vec4floats = SIMD[DType.float64, 4]
alias vec4zeros = Vec4floats(0)
alias VecParticles = InlinedFixedVector[Particle, 4]

alias nb_particles = 1024
alias benchmark_iterations = 500
alias nelts = 16


fn rand_fill_3_values() -> Vec4floats:
    var x = Vec4floats(0)
    let ptr = DTypePointer[DType.float64].alloc(3)
    rand(ptr, 3)
    x[0] = ptr.load(0)
    x[1] = ptr.load(1)
    x[2] = ptr.load(2)
    return x


@register_passable("trivial")
struct Particle:
    var position: Vec4floats
    var velocity: Vec4floats
    var acceleration: Vec4floats
    var acceleration1: Vec4floats
    var mass: Float64

    fn __init__() -> Self:
        let position = rand_fill_3_values()
        let velocity = rand_fill_3_values()
        let acceleration = rand_fill_3_values()
        let acceleration1 = vec4zeros
        let mass = random_float64()
        return Self {
            position: position,
            velocity: velocity,
            acceleration: acceleration,
            acceleration1: acceleration1,
            mass: mass,
        }


@always_inline
fn norm_cube(vec: Vec4floats) -> Float64:
    let norm2_ = norm2(vec)
    return norm2_ * sqrt(norm2_)


@always_inline
fn norm2(vec: Vec4floats) -> Float64:
    return vec[0] ** 2 + vec[1] ** 2 + vec[2] ** 2 + vec[3] ** 2


@always_inline
fn accelerate(inout particles: VecParticles) -> NoneType:
    for idx in range(len(particles)):
        var particle = particles[idx]
        particle.acceleration1 = particle.acceleration
        particle.acceleration = Vec4floats(0)
        particles[idx] = particle

    let nb_particules = len(particles)
    for i0 in range(nb_particules - 1):
        var p0 = particles[i0]
        for i1 in range(i0 + 1, nb_particules):
            var p1 = particles[i1]
            let delta = p0.position - p1.position
            let distance_cube = norm_cube(delta)
            p0.acceleration -= p1.mass / distance_cube * delta
            p1.acceleration += p0.mass / distance_cube * delta

            particles[i0] = p0
            particles[i1] = p1


fn fill_3D_tuple[n: Int]() -> StaticTuple[3, DTypePointer[DType.float64]]:
    var result = StaticTuple[3, DTypePointer[DType.float64]]()

    @unroll
    for i in range(3):
        let ptr = DTypePointer[DType.float64].alloc(n)
        rand(ptr, n)
        result[i] = ptr
    return result


struct Particles[n: Int]:
    var position: StaticTuple[3, DTypePointer[DType.float64]]
    var velocity: StaticTuple[3, DTypePointer[DType.float64]]
    var acceleration: StaticTuple[3, DTypePointer[DType.float64]]
    var acceleration1: StaticTuple[3, DTypePointer[DType.float64]]
    var mass: DTypePointer[DType.float64]

    fn __init__(inout self):
        self.position = fill_3D_tuple[n]()
        self.velocity = fill_3D_tuple[n]()
        self.acceleration = fill_3D_tuple[n]()
        self.acceleration1 = fill_3D_tuple[n]()
        self.mass = DTypePointer[DType.float64].alloc(n)
        rand(self.mass, n)


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


fn accelerate_vectorize[n: Int](inout particles: Particles[n]):
    let position = particles.position
    let acceleration = particles.acceleration
    let acceleration1 = particles.acceleration1
    let mass = particles.mass

    # store current acceleration as acceleration1
    @unroll
    for axis in range(3):
        memcpy(
            acceleration1[axis],
            acceleration[axis],
            n,
        )
        memset_zero(acceleration[axis], n)

    for i0 in range(n - 1):

        @parameter
        fn other_particles[_nelts: Int](i_tail: Int):
            let i1 = i0 + i_tail + 1
            let delta_x = position[0].load(i0) - position[0].simd_load[_nelts](i1)
            let delta_y = position[1].load(i0) - position[1].simd_load[_nelts](i1)
            let delta_z = position[2].load(i0) - position[2].simd_load[_nelts](i1)
            let distance_cube = norm_cube(delta_x, delta_y, delta_z)
            let delta = StaticTuple[3, SIMD[DType.float64, _nelts]](
                delta_x / distance_cube,
                delta_y / distance_cube,
                delta_z / distance_cube,
            )

            @unroll
            for axis in range(3):
                let acc_ptr = acceleration[axis]
                acc_ptr.store(
                    i0,
                    acc_ptr.load(i0)
                    - (mass.simd_load[_nelts](i1) * delta[axis]).reduce_add(),
                )

                acc_ptr.simd_store[_nelts](
                    i1,
                    acc_ptr.simd_load[_nelts](i1) + mass.load(i0) * delta[axis],
                )

        vectorize[nelts, other_particles](n - i0 - 1)


fn accelerate_tile[n: Int](inout particles: Particles[n]):
    let position = particles.position
    let acceleration = particles.acceleration
    let acceleration1 = particles.acceleration1
    let mass = particles.mass

    # store current acceleration as acceleration1
    @unroll
    for axis in range(3):
        memcpy(
            acceleration1[axis],
            acceleration[axis],
            n,
        )
        memset_zero(acceleration[axis], n)

    for i0 in range(n - 1):

        @parameter
        fn other_particles[_nelts: Int](i1: Int):
            let delta_x = position[0].load(i0) - position[0].simd_load[_nelts](i1)
            let delta_y = position[1].load(i0) - position[1].simd_load[_nelts](i1)
            let delta_z = position[2].load(i0) - position[2].simd_load[_nelts](i1)
            let distance_cube = norm_cube(delta_x, delta_y, delta_z)
            let delta = StaticTuple[3, SIMD[DType.float64, _nelts]](
                delta_x / distance_cube,
                delta_y / distance_cube,
                delta_z / distance_cube,
            )

            @unroll
            for axis in range(3):
                let acc_ptr = acceleration[axis]
                acc_ptr.store(
                    i0,
                    acc_ptr.load(i0)
                    - (mass.simd_load[_nelts](i1) * delta[axis]).reduce_add(),
                )

                acc_ptr.simd_store[_nelts](
                    i1,
                    acc_ptr.simd_load[_nelts](i1) + mass.load(i0) * delta[axis],
                )

        tile[
            other_particles,
            VariadicList(nelts, nelts // 2, nelts // 4, 1),
        ](i0 + 1, n)


fn bench[func: fn (inout VecParticles) -> None]() -> Float64:
    var particles = VecParticles(nb_particles)
    for _ in range(nb_particles):
        particles.append(Particle())

    @parameter
    fn wrapper():
        for i in range(benchmark_iterations):
            func(particles)

    let rep = benchmark.run[wrapper]()
    print("Time: ", rep.mean(), "seconds")

    return rep.mean()


fn bench2[func: fn (inout Particles) -> None]() -> Float64:
    var particles = Particles[nb_particles]()

    @parameter
    fn wrapper():
        for i in range(benchmark_iterations):
            func(particles)

    let rep = benchmark.run[wrapper]()
    print("Time: ", rep.mean(), "seconds")

    return rep.mean()


fn correctness_check[func: fn (inout Particles) -> None]():
    var p = VecParticles(nb_particles)
    for _ in range(nb_particles):
        p.append(Particle())

    var p_ = Particles[nb_particles]()
    for ii in range(nb_particles):
        let i = ii
        p_.mass.store(i, p[i].mass)
        for j in range(3):
            p_.position[j].store(i, p[i].position[j])
            p_.velocity[j].store(i, p[i].velocity[j])
            p_.acceleration[j].store(i, p[i].acceleration[j])
            p_.acceleration1[j].store(i, p[i].acceleration1[j])

    @parameter
    fn check_equal() -> Bool:
        var is_correct = True
        for i in range(nb_particles):
            if not assert_almost_equal(p[i].mass, p_.mass.load(i)):
                print("mass mismatch", i)
                is_correct = False
            for j in range(3):
                if not assert_almost_equal(p[i].position[j], p_.position[j].load(i)):
                    print("position mismatch", i, j)
                    is_correct = False
                if not assert_almost_equal(p[i].velocity[j], p_.velocity[j].load(i)):
                    print("velocity mismatch", i, j)
                    is_correct = False
                if not assert_almost_equal(
                    p[i].acceleration[j], p_.acceleration[j].load(i)
                ):
                    print("acceleration mismatch", i, j)
                    is_correct = False
                if not assert_almost_equal(
                    p[i].acceleration1[j], p_.acceleration1[j].load(i)
                ):
                    print("acceleration1 mismatch", i, j)
                    is_correct = False
        return is_correct

    if not check_equal():
        print("correctness check failed before accelarate")
    accelerate(p)
    func(p_)
    if not check_equal():
        print("correctness check failed after accelarate")


fn main():
    print("nelts:", nelts)
    correctness_check[accelerate_vectorize]()
    correctness_check[accelerate_tile]()

    let original_time = bench[accelerate]()
    var new_time = bench2[accelerate_vectorize]()
    print("Speedup: ", original_time / new_time, " (vectorize)")

    new_time = bench2[accelerate_tile]()
    print("Speedup: ", original_time / new_time, " (tile)")
