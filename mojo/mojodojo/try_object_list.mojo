def my_def(a: object):
    # argument given by copy but one can modify the referenced list
    a[0] = 1


fn my_fn(borrowed a: object) raises:
    # argument borrowed but one can modify the referenced list
    a[0] = 2


def main():
    a = object([0])
    print(a)
    b = a  # <- the reference is copied but not the pointed list
    my_def(a)
    print(a)
    print(b)
    my_fn(a)
    print(a)
