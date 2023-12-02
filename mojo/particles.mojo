from math import sqrt
from random import rand, random_float64
from algorithm import vectorize, tile
from memory import memcpy, memset_zero


fn fill_3D_tuple(n: Int) -> StaticTuple[3, DTypePointer[DType.float64]]:
    var result = StaticTuple[3, DTypePointer[DType.float64]]()

    @unroll
    for i in range(3):
        let ptr = DTypePointer[DType.float64].alloc(n)
        rand(ptr, n)
        result[i] = ptr
    return result


struct Particles:
    var size: Int
    var position: StaticTuple[3, DTypePointer[DType.float64]]
    var velocity: StaticTuple[3, DTypePointer[DType.float64]]
    var acceleration: StaticTuple[3, DTypePointer[DType.float64]]
    var acceleration1: StaticTuple[3, DTypePointer[DType.float64]]
    var mass: DTypePointer[DType.float64]

    fn __init__(inout self, size: Int):
        self.size = size
        self.position = fill_3D_tuple(size)
        self.velocity = fill_3D_tuple(size)
        self.acceleration = fill_3D_tuple(size)
        self.acceleration1 = fill_3D_tuple(size)
        self.mass = DTypePointer[DType.float64].alloc(size)
        rand(self.mass, size)

    fn __del__(owned self):
        @unroll
        for axis in range(3):
            self.position[axis].free()
            self.velocity[axis].free()
            self.acceleration[axis].free()
            self.acceleration1[axis].free()

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


fn accelerate_vectorize[nelts: Int](inout particles: Particles):
    let size = particles.size
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
            size,
        )
        memset_zero(acceleration[axis], size)

    for i0 in range(size):

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

        vectorize[nelts, other_particles](size - i0 - 1)


fn accelerate_tile[nelts: Int](inout particles: Particles):
    let size = particles.size
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
            size,
        )
        memset_zero(acceleration[axis], size)

    for i0 in range(size):

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
            VariadicList[Int](nelts, 1),
        ](i0 + 1, size)
