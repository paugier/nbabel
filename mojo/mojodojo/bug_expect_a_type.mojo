
from memory.unsafe import Pointer, DTypePointer
from memory.memory import memset_zero

@register_passable
struct SimpleContainer[dtype: DType]:

    var data: DTypePointer[dtype]
    var size: Int

    fn __init__(size: Int) -> Self:
        let data = DTypePointer[dtype].alloc(size)
        memset_zero[dtype](data, size)
        return Self {data: data, size: size}

    fn __setitem__(inout self, idx: Int, value: SIMD[dtype, 1]):
        self.data.store(idx, value)

    fn __del__(owned self):
        self.data.free()


def main():

    a = SimpleContainer[DType.int64](4)

    print(a.size)