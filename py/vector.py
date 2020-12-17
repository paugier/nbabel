class MetaVector(type):
    def __getitem__(self, dtype):
        return type(
            f"Vector{dtype.__name__.capitalize()}",
            (Vector,),
            {"dtype": dtype},
        )


class Vector(metaclass=MetaVector):
    @classmethod
    def from_list(cls, data):
        return cls(len(data), data=data)

    @classmethod
    def empty(cls, size):
        return cls(size)

    def zeros_like(self):
        points = self.empty(len(self))
        i = 0
        while i < len(self):
            points[i] = self.dtype.zero()
            i += 1
        return points

    def __init__(self, size, data=None):
        if data is None:
            self._data = [None] * size
        else:
            self._data = list(data).copy()

        self.__iter__ = self._data.__iter__

    def __getitem__(self, index):
        return self._data[index]

    def __setitem__(self, index, value):
        self._data[index] = value

    def __len__(self):
        return len(self._data)



if __name__ == "__main__":

    class Point2d:

        @classmethod
        def zero(cls):
            return cls(0., 0.)

        def __init__(self, x, y):
            self.x = x
            self.y = y


    a = Vector[Point2d].empty(4)