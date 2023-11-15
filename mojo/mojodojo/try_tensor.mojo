
from tensor import Tensor, TensorShape, TensorSpec


def main():
    t = Tensor[DType.int64](4)
    print(t)
    t1 = t
    t1[0] = 1
    print(t1)
    print(t)
