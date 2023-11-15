def my_def(a: object):
    # argument given by copy but one can modify the referenced list
    a[0] = 1


fn my_fn(borrowed a: object) raises:
    # argument borrowed but one can modify the referenced list
    a[0] = 2


def main():
    a = object([0])

    print(a)
    my_def(a)
    print(a)
    my_fn(a)
    print(a)
