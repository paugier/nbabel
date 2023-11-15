
from memory.unsafe import Pointer


struct IntRef:
    var ptr_value: Pointer[Int]
    var ptr_ref_count: Pointer[Int]

    fn __init__(inout self, value: Int):
        self.ptr_value = Pointer[Int].alloc(1)
        self.ptr_value.store(0, value)
        self.ptr_ref_count = Pointer[Int].alloc(1)
        self.ptr_ref_count.store(0, 1)

    fn __copyinit__(inout self, borrowed existing: Self):
        print("__copyinit__")
        self.ptr_value = existing.ptr_value
        self.ptr_ref_count = existing.ptr_ref_count
        self._incref()

    fn __moveinit__(inout self, owned existing: Self):
        print("__moveinit__")
        self.ptr_value = existing.ptr_value
        self.ptr_ref_count = existing.ptr_ref_count

    fn _incref(inout self):
        let ref_count = self.ptr_ref_count.load(0)
        self.ptr_ref_count.store(0, ref_count + 1)

    fn _decref(inout self):
        let ref_count = self.ptr_ref_count.load(0)
        self.ptr_ref_count.store(0, ref_count -1)

    fn __del__(owned self):
        self._decref()
        let ref_count = self.ptr_ref_count.load(0)
        if ref_count == 0:
            print("Data freed")
            self.ptr_value.free()
            self.ptr_ref_count.free()

    fn __str__(self) -> String:
        let ref_count = self.ptr_ref_count.load(0)
        let value = self.ptr_value.load(0)
        return "Ref(value=" + String(value) + ', ref_count=' + String(ref_count) + ")"

    fn set_value(inout self, value: Int):
        self.ptr_value.store(0, value)


def main():

    a = IntRef(4)

    print("in main, a:", a.__str__())

    b = a

    print("in main, a:", a.__str__())
    print("in main, b:", b.__str__())

    a.set_value(2)

    print("in main, a:", a.__str__())
    print("in main, b:", b.__str__())

    c = b
    d = b
    print("in main, c:", c.__str__())
    print("in main, d:", d.__str__())
    e = b
