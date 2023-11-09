from math import abs

from tensor import Tensor, TensorSpec

# from utils.index import Index
from memory.buffer import Buffer
from memory.unsafe import DTypePointer


from _list import list


alias PointerFloat64 = DTypePointer[DType.float64]


fn contain_char(string: String, char: String = ".") raises -> (Bool, Int):
    if len(char) != 1:
        raise Error("len(char) != 1")

    for idx in range(string.__len__()):
        if string[idx] == char:
            return True, idx

    return False, 0


fn string_to_float(str_n: String) raises -> Float64:
    let contains: Bool
    let idx: Int

    contains, idx = contain_char(str_n)

    let number: Float64

    if contains:
        var sign = 1
        if str_n[0] == "-":
            sign = -1

        let before = str_n[:idx]
        let after = str_n[idx + 1 :]

        let n_before = atol(before)
        let n_after = atol(after)

        var f_alter = Float64(n_after)
        if len(after) < 19:
            f_alter = f_alter / 10 ** len(after)
        else:
            f_alter = f_alter / 10**18 / 10 ** (len(after) - 18)

        number = sign * (Float64(abs(n_before)) + f_alter)
    else:
        number = Float64(atol(str_n))

    return number


fn split(input_string: String, sep: String = " ") raises -> list[String]:
    var output = list[String]()
    var start = 0
    var split_count = 0

    for end in range(len(input_string) - len(sep) + 1):
        if input_string[end : end + len(sep)] == sep:
            output.append(input_string[start:end])
            start = end + len(sep)
            split_count += 1

    output.append(input_string[start:])
    return output


def read_file(path: String) -> String:
    let text: String
    with open(path, "r") as file:
        text = file.read()
    return text


def _test_string_to_float(str_n: String, should_be: Float64):
    let result = string_to_float(str_n)

    if result != should_be:
        print("Error for ", str_n, result)
        raise Error("string_to_float error")


struct DataContainer:
    var n0: Int
    var n1: Int
    var size: Int
    var data: PointerFloat64

    fn __init__(inout self, n0: Int, n1: Int):
        self.n0 = n0
        self.n1 = n1
        let size = n0 * n1
        self.size = size
        self.data = PointerFloat64.alloc(size)

    fn __copyinit__(inout self, existing: Self):
        self.n0 = existing.n0
        self.n1 = existing.n1
        self.size = existing.size
        self.data = PointerFloat64.alloc(self.size)
        for i in range(self.size):
            self.data.store(i, existing.data.load(i))

    fn __del__(owned self):
        return self.data.free()

    fn __getitem__(self, i0: Int, i1: Int) -> Float64:
        return self.data.load(i0 * self.n1 + i1)

    fn __setitem__(self, i0: Int, i1: Int, value: Float64):
        return self.data.store(i0 * self.n1 + i1, value)


def read_data(path: String) -> DataContainer:
    lines = split(read_file(path), "\n")

    nb_particles = 0
    for index in range(lines.__len__()):
        line = lines[index]
        if not len(line):
            continue
        nb_particles += 1

    container = DataContainer(nb_particles, 7)

    index_part = -1

    for index in range(lines.__len__()):
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

        for idx in range(words1.__len__()):
            container[index_part, idx] = string_to_float(words1[idx])

    return container


def main():
    _test_string_to_float("-0.503269367480841723", -0.503269367480841723)
    _test_string_to_float("0.503269367480841723", 0.503269367480841723)
    _test_string_to_float("-1.503269367480841723", -1.503269367480841723)
    _test_string_to_float("1.503269367480841723", 1.503269367480841723)
    _test_string_to_float("0", 0.0)
    _test_string_to_float("-0", 0.0)
    _test_string_to_float("-1", -1.0)
    _test_string_to_float("1", 1.0)
    _test_string_to_float("0.1654360739738478747", 0.1654360739738478747)
