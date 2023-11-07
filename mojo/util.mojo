
from _list import list


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
