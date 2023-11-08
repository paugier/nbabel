
from math import abs

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

        number = sign * (Float64(abs(n_before)) + Float64(n_after) / 10 ** len(after))
    else:
        number = Float64(atol(str_n))

    return number