from tensor import Tensor
from memory.unsafe import Pointer, DTypePointer
from memory.memory import memcpy


@register_passable("trivial")
struct InternalContainer:
    var data: Int
    var ref_count: Int

    fn __init__(value: Int) -> Self:
        return Self {data: value, ref_count: 1}

    fn __init__() -> Self:
        return Self {data: 0, ref_count: 1}

    fn __str__(self) -> String:
        return (
            "InternalContainer(data="
            + String(self.data)
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


struct MyPyIntRef:
    var ptr_container: Pointer[InternalContainer]

    fn __init__(inout self, size: Int):
        self.ptr_container = Pointer[InternalContainer].alloc(1)
        self.ptr_container.store(0, InternalContainer(4))
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
        let container = self.ptr_container.load(0)
        return "Ref(" + String(container.__str__())


def main():
    a = MyPyIntRef(4)

    print("in main, a:", a.__str__())

    b = a

    print("in main, a:", a.__str__())
    print("in main, b:", b.__str__())

    c = b

    print("in main, c:", c.__str__())


