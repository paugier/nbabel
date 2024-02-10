from math import sqrt
from random import rand, random_float64
from algorithm import vectorize, tile
from memory import memcpy, memset_zero
from testing import assert_equal, assert_almost_equal
from sys.info import simdwidthof
from collections.vector import InlinedFixedVector

import benchmark

from particles import Particles, accelerate_tile, accelerate_vectorize

alias Vec4floats = SIMD[DType.float64, 4]
alias vec4zeros = Vec4floats(0)
alias VecParticles = InlinedFixedVector[Particle]

alias nb_particles = 1024
alias benchmark_iterations = 500


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

    for i0 in range(nb_particules):
        var p0 = particles[i0]

        for i1 in range(i0 + 1, nb_particules):
            var p1 = particles[i1]
            let delta = p0.position - p1.position
            let distance_cube = norm_cube(delta)
            p0.acceleration -= p1.mass / distance_cube * delta
            p1.acceleration += p0.mass / distance_cube * delta
            particles[i1].acceleration = p1.acceleration

        particles[i0].acceleration = p0.acceleration


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
    var particles = Particles(nb_particles)

    @parameter
    fn wrapper():
        for i in range(benchmark_iterations):
            func(particles)

    let rep = benchmark.run[wrapper]()
    # using particles to delay its destruction
    let size = particles.size
    print("Time: ", rep.mean(), "seconds")
    return rep.mean()


fn correctness_check[func: fn (inout Particles) -> None]():
    var p = VecParticles(nb_particles)
    for _ in range(nb_particles):
        p.append(Particle())

    var p_ = Particles(nb_particles)
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
            try:
                assert_almost_equal(p[i].mass, p_.mass.load(i))
            except Error:
                print("mass mismatch", i)
                is_correct = False
            for j in range(3):
                try:
                    assert_almost_equal(p[i].position[j], p_.position[j].load(i))
                except Error:
                    print("position mismatch", i, j)
                    is_correct = False
                try:
                    assert_almost_equal(p[i].velocity[j], p_.velocity[j].load(i))
                except:
                    print("velocity mismatch", i, j)
                    is_correct = False
                try:
                    assert_almost_equal(
                        p[i].acceleration[j], p_.acceleration[j].load(i)
                    )
                except Error:
                    print("acceleration mismatch", i, j)
                    is_correct = False
                try:
                    assert_almost_equal(
                        p[i].acceleration1[j], p_.acceleration1[j].load(i)
                    )
                except Error:
                    print("acceleration1 mismatch", i, j)
                    is_correct = False
        return is_correct

    if not check_equal():
        print("correctness check failed before accelarate")
    accelerate(p)
    func(p_)
    if not check_equal():
        print("correctness check failed after accelarate")
    let size = p_.size
    # using p_ to delay its destruction


fn check_bench_1_nelts[nelts: Int](original_time: Float64):
    print("nelts:", nelts)
    correctness_check[accelerate_vectorize[nelts]]()
    correctness_check[accelerate_tile[nelts]]()

    var new_time = bench2[accelerate_vectorize[nelts]]()
    print("Speedup: ", original_time / new_time, " (vectorize)")

    new_time = bench2[accelerate_tile[nelts]]()
    print("Speedup: ", original_time / new_time, " (tile)")


fn main():
    alias simd_width = simdwidthof[DType.float64]()
    print("simd_width:", simd_width)

    let original_time = bench[accelerate]()

    check_bench_1_nelts[2](original_time)
    check_bench_1_nelts[4](original_time)
    check_bench_1_nelts[8](original_time)
    check_bench_1_nelts[16](original_time)
    check_bench_1_nelts[32](original_time)
