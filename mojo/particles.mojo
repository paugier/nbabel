from math import sqrt
from random import rand, random_float64
from algorithm import vectorize, tile, parallelize
from memory import memcpy, memset_zero, stack_allocation

from sys.info import num_performance_cores


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
        var acc_0 = StaticTuple[3, DTypePointer[DType.float64]]()

        @unroll
        for axis in range(3):
            acc_0[axis] = stack_allocation[nelts, DType.float64]()
            memset_zero(acc_0[axis], nelts)

        @parameter
        fn other_particles[_nelts: Int](i_tail: Int):
            let i1 = i0 + i_tail + 1
            var delta = StaticTuple[3, SIMD[DType.float64, _nelts]]()

            @unroll
            for axis in range(3):
                delta[axis] = position[axis][i0] - position[axis].simd_load[_nelts](i1)

            let distance_cube = norm_cube(delta[0], delta[1], delta[2])

            @unroll
            for axis in range(3):
                delta[axis] /= distance_cube
                let acc_ptr = acceleration[axis]
                acc_0[axis].simd_store[_nelts](
                    acc_0[axis].simd_load[_nelts]()
                    - (mass.simd_load[_nelts](i1) * delta[axis]),
                )

                acc_ptr.simd_store[_nelts](
                    i1,
                    acc_ptr.simd_load[_nelts](i1) + mass[i0] * delta[axis],
                )

        vectorize[nelts, other_particles](size - i0 - 1)

        @unroll
        for axis in range(3):
            acceleration[axis][i0] += acc_0[axis].simd_load[nelts]().reduce_add()


fn accelerate_parallelize_vectorize[nelts: Int](inout particles: Particles):
    let size = particles.size
    let position = particles.position
    let acceleration = particles.acceleration
    let acceleration1 = particles.acceleration1
    let mass = particles.mass

    @unroll
    for axis in range(3):
        memcpy(
            acceleration1[axis],
            acceleration[axis],
            size,
        )
        memset_zero(acceleration[axis], size)

    @parameter
    fn outer_body(i0: Int):
        var acc_0 = StaticTuple[3, DTypePointer[DType.float64]]()

        @unroll
        for axis in range(3):
            acc_0[axis] = stack_allocation[nelts, DType.float64]()
            memset_zero(acc_0[axis], nelts)

        @parameter
        fn inner_body[_nelts: Int](i1: Int):
            var delta = StaticTuple[3, SIMD[DType.float64, _nelts]]()

            @unroll
            for axis in range(3):
                delta[axis] = position[axis][i0] - position[axis].simd_load[_nelts](i1)

            let distance_cube = norm_cube(delta[0], delta[1], delta[2])

            @unroll
            for axis in range(3):
                delta[axis] /= distance_cube
                # zero the multiplier where i0 and i1 are same body
                var multiplier = mass.simd_load[_nelts](i1) * delta[axis]
                if i1 <= i0 < i1 + _nelts:
                    multiplier[i0 - i1] = 0
                acc_0[axis].simd_store[_nelts](
                    acc_0[axis].simd_load[_nelts]() - multiplier,
                )

        vectorize[nelts, inner_body](size)

        @unroll
        for axis in range(3):
            acceleration[axis][i0] += acc_0[axis].simd_load[nelts]().reduce_add()

    parallelize[outer_body](size, num_performance_cores())


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
        var acc_0 = StaticTuple[3, DTypePointer[DType.float64]]()

        @unroll
        for axis in range(3):
            acc_0[axis] = stack_allocation[nelts, DType.float64]()
            memset_zero(acc_0[axis], nelts)

        @parameter
        fn other_particles[_nelts: Int](i1: Int):
            var delta = StaticTuple[3, SIMD[DType.float64, _nelts]]()

            @unroll
            for axis in range(3):
                delta[axis] = position[axis][i0] - position[axis].simd_load[_nelts](i1)

            let distance_cube = norm_cube(delta[0], delta[1], delta[2])

            @unroll
            for axis in range(3):
                delta[axis] /= distance_cube
                let acc_ptr = acceleration[axis]
                acc_0[axis].simd_store[_nelts](
                    acc_0[axis].simd_load[_nelts]()
                    - (mass.simd_load[_nelts](i1) * delta[axis]),
                )

                acc_ptr.simd_store[_nelts](
                    i1,
                    acc_ptr.simd_load[_nelts](i1) + mass[i0] * delta[axis],
                )

        tile[
            other_particles,
            VariadicList[Int](nelts, 1),
        ](i0 + 1, size)

        @unroll
        for axis in range(3):
            acceleration[axis][i0] += acc_0[axis].simd_load[nelts]().reduce_add()
