from vector import Vector

from microbench_pypy4 import Point3D, number_particles
from microbench_pypy_list import Point3D as P3D_list


def sum_x(positions):
    result = 0.0
    for i in range(len(positions)):
        result += positions[i].x
    return result


if __name__ == "__main__":

    positions = Vector[Point3D].zeros(number_particles)

    x = 0.0
    for position in positions:
        position.x = x
        x += 1.0

    positions_list = Vector[P3D_list].zeros(number_particles)

    x = 0.0
    for position in positions_list:
        position.x = x
        x += 1.0

    assert sum_x(positions_list) == sum_x(positions)


    from IPython import get_ipython
    ipython = get_ipython()

    print("sum_x(positions)")
    ipython.magic("timeit sum_x(positions)")
    print("sum_x(positions_list)")
    ipython.magic("timeit sum_x(positions_list)")
