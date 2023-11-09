
from tensor import Tensor, TensorSpec
from utils.index import Index
from memory.buffer import Buffer
from memory.unsafe import DTypePointer

from helpers import read_file, list, split, string_to_float


struct DataContainer:
    var data: DTypePointer[DType.float64]
    var n0: Int
    var n1: Int
    var size: Int

    fn __init__(inout self, n0: Int, n1: Int):
        self.n0 = n0
        self.n1 = n1
        let size = n0 * n1
        self.size = size
        self.data = DTypePointer[DType.float64].alloc(size)

    fn __del__(owned self):
        return self.data.free()

    fn __getitem__(self, i0: Int, i1: Int) -> Float64:
        return self.data.load(i0 * self.n1 + i1)

    fn __setitem__(self, i0: Int, i1: Int, value: Float64):
        return self.data.store(i0 * self.n1 + i1, value)


def main():

    path = "../data/input1k"

    lines = split(read_file(path), "\n")

    nb_particles = 0
    for index in range(lines.__len__()):
        line = lines[index]
        if not len(line):
            continue
        nb_particles += 1

    container = DataContainer(nb_particles, 7)



    # let spec = TensorSpec(DType.float64, nb_particles, 7)
    # var tensor = Tensor[DType.float64](spec)

    index_part = -1

    for index in range(1):
        line = lines[index]
        if not len(line):
            continue

        index_part += 1

        words = split(line)
        words1 = list[String]()
        for idx in range(1, words.__len__()):
            word = words[idx]
            if len(word):
                words1.append(word)

        # words = words1

        for idx in range(words1.__len__()):
            print(words1[idx], "stop")
            print(string_to_float(words1[idx]))
            container[index_part, idx] = string_to_float(words1[idx])

            # tensor[Index(index_part, idx)] = string_to_float(words[idx])

    print("\n")

    idx_part = 0
    for idx_value in range(7):
        print(container[idx_part, idx_value])


    # print(tensor[1])

    # buf = Buffer[7, DType.float64](tensor.data)
