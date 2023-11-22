from memory.unsafe import Pointer


def print_pointer(ptr: Pointer):
    print(ptr.__as_index())


def main():
    a = 1
    p1 = Pointer.address_of(a)
    print_pointer(p1)

    a = 2
    p2 = Pointer.address_of(a)
    print_pointer(p2)

    # a = "a"  # error: cannot implicitly convert 'StringLiteral' value to 'Int' in assignment

    b = "mojo"
    p = Pointer.address_of(b)
    print_pointer(p)

    c = b
    p = Pointer.address_of(c)
    print_pointer(p)
