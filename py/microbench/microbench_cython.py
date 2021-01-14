from util_cython import Point, Points


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


if __name__ == "__main__":
    from IPython import get_ipython

    ipython = get_ipython()

    def bench(call):
        print(call + "\n  ", end="")
        ipython.magic("timeit " + call)

    points = Points.new_ones(1000)

    x = 0.0
    for i in range(len(points)):
        points[i] = Point(x, x, x)
        x += 1.0

    bench("sum_few_x(points)")
    bench("sum_all_x(points)")
    bench("sum_few_norm2(points)")
