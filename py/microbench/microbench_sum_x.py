"""
run with IPython::

  ipython microbench_sum_x.py

"""

from vector import Vector

from microbench_pypy4 import Point3D, number_particles


def sum_all_x(vec):
    result = 0.0
    for position in vec:
        result += position.x
    return result


def sum_few_x(vec):
    result = 0.0
    for i in range(10, len(vec)):
        result += vec[i].x
    return result


def sum_few_norm2(vec):
    result = 0.0
    for i in range(10, len(vec)):
        result += vec[i].norm2()
    return result


def norm2(elem):
    return elem.x ** 2 + elem.y ** 2 + elem.z ** 2


def sum_few_norm2_func(vec):
    result = 0.0
    for i in range(10, len(vec)):
        result += norm2(vec[i])
    return result


def get_x(vec, index):
    return vec[index].x


def get_xs(vec):
    for point in vec:
        point.x


def loop_all_objects(vec):
    for point in vec:
        point


if __name__ == "__main__":
    from IPython import get_ipython

    ipython = get_ipython()

    def bench(call):
        print(call + "\n  ", end="")
        ipython.magic("timeit " + call)

    points = Vector[Point3D].zeros(number_particles)

    x = 0.0
    for position in points:
        position.x = x
        x += 1.0

    bench("sum_few_x(points)")
    bench("sum_all_x(points)")
    bench("sum_few_norm2(points)")
    bench("sum_few_norm2_func(points)")
    # bench("get_x(points, 2)")
    # bench("get_xs(points)")
    # bench("loop_all_objects(points)")

    # list_empty_object = [object() for _ in range(number_particles)]
    # bench("loop_all_objects(list_empty_object)")
