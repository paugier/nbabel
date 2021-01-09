from microbench_sum_x import sum_all_x, sum_few_x, sum_few_norm2_func

from cffi import FFI

ffi = FFI()

ffi.cdef(
    """
    typedef struct {
        double x, y, z;
    } point_t;
"""
)

points = ffi.new("point_t[]", 1000)

if __name__ == "__main__":

    from IPython import get_ipython

    ipython = get_ipython()

    def bench(call):
        print(call + "\n  ", end="")
        ipython.magic("timeit " + call)

    bench("sum_few_x(points)")
    bench("sum_all_x(points)")
    bench("sum_few_norm2_func(points)")
