# Simple efficient 1d vector for Python

The goal of the proposed extension is to be able to execute very efficiency
numerical pure Python codes. It should not be difficult to strongly accelerate
codes using this extension with JIT to reach nearly the same performance as
what can be done with Julia. Moreover, it should not be too difficult for
ahead-of-time Python compilers to support this API. The global principle is to
locally disable some dynamical features of Python which are issues for
performance.

First, we need a data structure that does not exit yet in Python: a container
for homogeneous objects. Since we start with 1D sequence, let's call that a
`Vector` (as in Julia).

- The mathematical operators would act on elements (like Numpy arrays and in
contrast to `list`, `tuple` and `array.array`). For standard numerical types,
such operations would be fast (or even very fast, with SIMD).

- For user-defined classes for which the size in memory of one instance is
constant, the interpreter could store the objects continuously so that
iterating on the elements contained in the container could be much faster than
with lists.

  For contiguous storage of instances of user-defined classes, one needs to be
  able to disable dynamic features of Python for these classes. We need to be
  able to declare a class to be immutable and that one can't dynamically add
  attributes to the instances. For objects containing only simple fixed size
  objects, the size of the instances will be fixed and can easily be computed.

  For some cases, it would also be interesting to declare that the instances of
  the class are immutable.

- Such containers could support different modes of executions, "debug", "dev"
and "perf", that can be activated locally (with an API) and globally (with an
environment variable). For the performance mode, some type checks and bound
checks would be disabled.

## API

Let's say that we import the extension as:

```
import vecpy as vp
```

A `Vector` can only store objects of homogeneous type, with fixed size
instances.

### Vectors of numbers

We can declare a type `Vector` of floats as:

```python
VectorF = vp.Vector[float]
```

Since all Python floats have the same size (they are "float64"), they can be
store continuously in memory. In contrast, in Python 3, the size of an `int` is
not fixed (an `int` object can stored very large integers) so `vp.Vector[int]`
should raise an error. To define an array of integer, one can use for example
`vp.Vector["int32"]`.

We can then declare vectors of different size like this:

```
vec_4f = VectorF.empty(4)
vec_2f = VectorF([2, 3])
vec_100f = VectorF.zeros(100)
```

We see that the size of the instances of `VectorF` is not fixed.

### Fixed-size vectors

```python
Vector4F = vp.Vector[float].subclass(size=4)
# can also be written as
Vector4F = vp.Vector.subclass(float, size=4)
```

### Vectors of fixed-size vector

All `Vector4F` instances have the same size in memory, so they can be stored in
another `Vector` and we can write:

```python
class Point(vp.Vector.subclass(float, size=3)):
    @property
    def x(self):
        return self[0]

    ...

    def square(self):
        return self.x**2 + self.y**2 + self.z**2

    ...

class Points(Vector[Point]):
    ...

# or just
Points = Vector[Point]

points = Points.empty(size=1000)

points[0] = [1, 2, 3]
# or
point = Point.zero()
point[0] = 1
points[0] = point  # copy
```

A Python interpreters with a JIT adapted for numerical tasks (like PyPy) could
run codes using such vectors very efficiently.

### Vector of instances of user-defined class

Under the hood, during the creation of a new concrete `Vector` class, we have
to obtain the size of an instance. For user-defined classes, this could be done
with a special class method `__size_of_instance__` (question: how one can
implement this?). We could use a decorator `vp.fixed_size_instances`.

Note: the special attribute `__slots__` can already be used in Python to
declare that one can't set a new attribute to an instance. The decorator
`vp.fixed_size_instances` could automatically set `__slots__` from type
annotations, see this example:

```python
@vp.fixed_size_instances
class MyNumericalClass:
    x: float
    y: float
    z: float

    ...
```

For such simple cases, a decorator could also set class methods like
`__zero__`, `__one__` and `__empty__`, and instance methods `__fill__`,
`__add__`, etc.

Of course, it should be forbidden to dynamically modify the class. We could use
a decorator `@vp.immutable_class`.

Setting the value of an element of a vector (`vec[i] = something`) implies a
copy, a type check and potentially a cast. We could use a special method
`__modify_from__` for these tasks so that ``vec[i] = something`` would be turned into

```python
vec[i].__modify_from__(something)
```

### Views

As in Numpy, we should prefer views to copies for slicing:

```
a = vp.Vector[float].zeros(4)
b = a[:2]
b += 1
print(a)
```

should return `[1, 1, 0, 0]`. Moreover, Vectors should have a `copy` method.

### Compatibility with Numpy

It should be easy and very efficient to transform vectors of simple numerical
types into contiguous Numpy arrays (and inversely).

## Notes on a possible implementation

Unfortunately, I don't think this can be implemented in Python. I guess one
could use RPython but the resulting extensions would only be usable with PyPy.
Using C with the standard CPython C-API would be terrible in terms of
performance for PyPy and other alternative implementations. I guess it would
make sense to use Cython with a backend using HPy. However, the HPy project is
very immature and this Cython backend targetting the HPy API is just mentionned
in some HPy documents. It could be interesting to try to implement the core of
such extension in HPy. I wonder if it could be possible with HPy to tell the
PyPy JIT how to accelerate code using `Vector`.
