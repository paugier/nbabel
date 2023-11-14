from memory.unsafe import DTypePointer


struct MyArray[dtype: DType]:
    var size: Int
    var pointer: DTypePointer[dtype]

    fn __init__(inout self, size: Int, value: SIMD[dtype, 1]):
        self.size = size
        self.pointer = DTypePointer[dtype]().alloc(size)
        for idx in range(size):
            self.pointer.store(idx, value)

    fn __copyinit__(inout self, borrowed existing: Self):
        print("__copyinit__")
        self.size = existing.size
        self.pointer = DTypePointer[dtype].alloc(self.size)
        for idx in range(self.size):
            self.pointer.store(idx, existing.pointer.load(idx))

    fn __moveinit__(inout self, owned existing: Self):
        print("__moveinit__")
        self.size = existing.size
        self.pointer = existing.pointer

    fn __getitem__(self, idx: Int) raises -> SIMD[dtype, 1]:
        if (idx < 0) or (idx >= self.size):
            raise Error("IndexError")
        return self.pointer.load(idx)

    fn __del__(owned self):
        self.pointer.free()
        print("MyArray deleted")


def main():
    arr = MyArray[DType.float64](4, 1.0)

    print(arr[0], arr[1])

    arr1 = arr
    print(arr1[0], arr1[1])

    arr1[0]

    arr2 = arr ^

    print(arr2[0])
