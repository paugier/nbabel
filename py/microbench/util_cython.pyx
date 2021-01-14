# cython: language_level=3
cimport cython

from libc.stdlib cimport malloc, free
from libc.string cimport memcpy

from math import sqrt


ctypedef struct point_:
    float x, y, z


@cython.freelist(8)
cdef class Point:
    cdef point_ *_ptr

    def __cinit__(self, x, y, z):

        self._ptr = <point_ *>malloc(sizeof(point_))
        if self._ptr is NULL:
            raise MemoryError
        if x is not None:
            self._ptr.x = x
            self._ptr.y = y
            self._ptr.y = y

    def __dealloc__(self):
        # De-allocate if not null and flag is set
        if self._ptr is not NULL:
            free(self._ptr)
            self._ptr = NULL

    def __repr__(self):
        return f"Point{self.x, self.y, self.z}"

    @property
    def x(self):
        return self._ptr.x

    @property
    def y(self):
        return self._ptr.y

    @property
    def z(self):
        return self._ptr.z

    def norm(self):
        return sqrt(self.norm2())

    def norm_cube(self):
        norm2 = self.norm2()
        return norm2 * sqrt(norm2)

    def norm2(self):
        return self.x ** 2 + self.y ** 2 + self.z ** 2

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other):
        return Point(other * self.x, other * self.y, other * self.z)

    __rmul__ = __mul__


cdef class Points:
    cdef int size
    cdef point_ *_ptr

    def __cinit__(self, int size):
        self.size = size
        self._ptr = <point_ *>malloc(size * sizeof(point_))
        if self._ptr is NULL:
            raise MemoryError

    @staticmethod
    def new_ones(size):
        cdef point_ *ptr_elem = <point_ *>malloc(sizeof(point_))
        ptr_elem.x = 1.
        ptr_elem.y = 1.
        ptr_elem.z = 1.

        cdef Points ret = Points.__new__(Points, size)

        cdef int i
        cdef point_ * ptr = ret._ptr
        for i in range(size):
            memcpy(ptr, ptr_elem, sizeof(point_))

        return ret

    def __iter__(self):
        cdef point_ *ptr_elem = self._ptr
        cdef Point point
        cdef int i
        for i in range(self.size):
            point = Point.__new__(Point, None, None, None)
            memcpy(point._ptr, ptr_elem, sizeof(point_))
            yield point
            ptr_elem += 1

    def __getitem__(self, int index):
        cdef point_ *ptr_elem = self._ptr + index
        cdef Point point = Point.__new__(Point, None, None, None)
        memcpy(point._ptr, ptr_elem, sizeof(point_))
        return point

    def __setitem__(self, int index, Point value):
        if not isinstance(value, Point):
            raise TypeError
        cdef point_ *ptr_elem = self._ptr + index
        memcpy(self._ptr + index, value._ptr, sizeof(point_))

    def __len__(self):
        return self.size

    # def __repr__(self):
    #     return self._data.__repr__()