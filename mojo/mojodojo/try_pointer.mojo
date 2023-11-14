from memory.unsafe import Pointer
from memory.memory import memset_zero


@register_passable  # ("trivial")
struct Container:
    var value: Int
    var ref_count: Int

    fn incref(inout self):
        self.ref_count += 1

    fn decref(inout self):
        self.ref_count -= 1

    fn __del__(owned self):
        print("__del__ Container")
        if self.ref_count == 0:
            self.free_memory()

    fn __copyinit__(existing: Self) -> Self:
        print("__copyinit__")
        return Self {value: existing.value, ref_count: existing.ref_count}

    fn free_memory(inout self):
        print("Freeing memory")

    fn __str__(self) -> String:
        return "Container(value=" + String(self.value) + ")"


def main():
    let p = Pointer[Container].alloc(1)
    memset_zero[Container](p, 1)

    # p[0].ref_count = 1
    # p[0].incref()

    # var v = p.load(0)
    # v.incref()
    # v.value = 5
    # p.store(0, v)

    # print(p[0].ref_count)
    # print(p[0].value)
    print(p[0].__str__())

    # v = p.load(0)
    # v.ref_count -= 1
    # if v.ref_count == 0:
    #     p.free()
    #     print("Array deleted and data freed")
    # else:
    #     p.store(0, v)
