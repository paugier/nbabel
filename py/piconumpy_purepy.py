class array:
    def __init__(self, data):
        if isinstance(data, list):
            self.data = data
            return
        self.data = list(float(number) for number in data)

    @property
    def size(self):
        return len(self.data)

    def __add__(self, other):
        if len(self.data) == 3 and len(other.data) == 3:
            return array(
                [
                    self.data[0] + other.data[0],
                    self.data[1] + other.data[1],
                    self.data[2] + other.data[2],
                ]
            )
        return array(
            number + other.data[index] for index, number in enumerate(self.data)
        )

    def __sub__(self, other):
        if len(self.data) == 3 and len(other.data) == 3:
            return array(
                [
                    self.data[0] - other.data[0],
                    self.data[1] - other.data[1],
                    self.data[2] - other.data[2],
                ]
            )
        return array(
            number - other.data[index] for index, number in enumerate(self.data)
        )

    def __pow__(self, exponent):
        if len(self.data) == 3:
            return array(
                [
                    self.data[0] ** exponent,
                    self.data[1] ** exponent,
                    self.data[2] ** exponent,
                ]
            )
        return array(number ** exponent for number in self.data)

    def __mul__(self, other):
        if len(self.data) == 3:
            return array(
                [
                    self.data[0] * other,
                    self.data[1] * other,
                    self.data[2] * other,
                ]
            )
        return array(other * number for number in self.data)

    __rmul__ = __mul__

    def __truediv__(self, other):
        if len(self.data) == 3:
            return array(
                [
                    self.data[0] / other,
                    self.data[1] / other,
                    self.data[2] / other,
                ]
            )
        return array(number / other for number in self.data)

    def tolist(self):
        return list(self.data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]

    def __setitem__(self, index, value):
        self.data[index] = value

    def __iadd__(self, other):
        if len(self.data) == 3 and len(other) == 3:
            self.data[0] += other[0]
            self.data[1] += other[1]
            self.data[2] += other[1]
            return self
        for index, value in enumerate(other):
            self.data[index] += value
        return self

    def __isub__(self, other):
        if len(self.data) == 3 and len(other) == 3:
            self.data[0] -= other[0]
            self.data[1] -= other[1]
            self.data[2] -= other[1]
            return self
        for index, value in enumerate(other):
            self.data[index] -= value
        return self

    def sum(self):
        if len(self.data) == 3:
            return self.data[0] + self.data[1] + self.data[2]
        return sum(self.data)


def empty(size):
    return array([0.0] * size)


def zeros(size):
    return array([0.0] * size)


class Vectors(array):
    def get_vector(self, index_part):
        start = 3 * index_part
        return array(self.data[start : start + 3])

    def fill(self, value):
        for i in range(self.size):
            self.data[i] = value

    def compute_squares(self):
        result = []
        for index_part in range(self.size // 3):
            vector = self.get_vector(index_part)
            result.append(vector[0] ** 2 + vector[1] ** 2 + vector[2] ** 2)
        return result
