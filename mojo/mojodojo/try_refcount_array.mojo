from memory.unsafe import Pointer, DTypePointer
from memory.memory import memset_zero


@register_passable("trivial")
struct InternalContainer[dtype: DType]:
    var data: DTypePointer[dtype]
    var size: Int
    var ref_count: Int

    fn __init__() -> Self:
        return Self {data: DTypePointer[dtype].get_null(), ref_count: 1, size: 1}

    fn __str__(self) -> String:
        var data_as_str = String("[")
        for idx in range(self.size - 1):
            let elem = self.data.load(idx)
            data_as_str += String(elem) + ", "

        let elem = self.data.load(self.size - 1)
        data_as_str += String(elem)

        data_as_str += "]"

        return (
            "InternalContainer(data="
            + data_as_str
            + ", ref_count"
            + String(self.ref_count)
            + ")"
        )

    fn incref(inout self):
        self.ref_count += 1

    fn decref(inout self):
        self.ref_count += 1

    fn free_memory(inout self):
        print("Freeing memory")
        self.data.free()

    fn __setitem__(inout self, idx: Int, value: SIMD[dtype, 1]):
        self.data.store(idx, value)


struct Array[dtype: DType]:
    var ptr_container: Pointer[InternalContainer[dtype]]

    fn __init__(inout self, size: Int):
        self.ptr_container = Pointer[InternalContainer[dtype]].alloc(1)
        var container = self.ptr_container[0]
        container.ref_count = 1
        container.size = size
        container.data = DTypePointer[dtype].alloc(size)
        memset_zero[dtype](container.data, size)
        self.ptr_container.store(0, container)
        print("end init Array")

    fn __copyinit__(inout self, borrowed existing: Self):
        print("__copyinit__")
        var container = existing.ptr_container.load(0)
        container.incref()
        existing.ptr_container.store(0, container)
        self.ptr_container = existing.ptr_container

    fn __moveinit__(inout self, owned existing: Self):
        print("__moveinit__")
        self.ptr_container = existing.ptr_container

    fn __del__(owned self):
        var container = self.ptr_container.load(0)
        print("del", self.__str__(), "refcount", container.ref_count)
        container.ref_count -= 1
        if container.ref_count == 0:
            self.ptr_container.free()
            container.free_memory()
            print("Array deleted and data freed")
        else:
            self.ptr_container.store(0, container)

    fn __str__(self) -> String:
        return "Ref(" + String(self.ptr_container.load(0).__str__())

    fn __setitem__(inout self, idx: Int, value: SIMD[dtype, 1]):
        var container = self.ptr_container.load(0)
        container[idx] = value


def main():
    a = Array[DType.int64](4)

    print("in main, a:", a.__str__())

    b = a

    print("in main, a:", a.__str__())
    print("in main, b:", b.__str__())

    a[0] = 5

    print("in main, a:", a.__str__())
    print("in main, b:", b.__str__())

    c = b

    print("in main, c:", c.__str__())
