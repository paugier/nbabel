# Simple efficient 1d vector for Python: a proposal for a new extension

This document proposes and describes a new Python extension fully compatible
with PyPy JIT to write computationally intensive code in pure Python style.

Both Python JITs (like PyPy and Numba) and ahead-of-time Python compilers (like
Pythran) could support this API. The global principle is to be able to disable
some dynamical features of Python for some objects to ease important
optimizations. Experiments with the N-Body problem
(https://github.com/paugier/nbabel/blob/master/py) suggest that this could lead
with PyPy to approximately a x4 speedup for pure Python style codes so that
such Python codes could be nearly as efficient as optimized Julia/C++/Fortran
codes.

We need a data structure that does not exist yet in pure Python: a container
for objects of the same types. Since we start with 1D sequence, let's call this
structure a `Vector` (as in Julia).

- The elements have to be stored continuously in memory. Therefore, iterating
on the elements contained in the container could be much faster than with
lists. Moreover, JIT and AOT compilers could know the type of the elements
without type checks.

- The mathematical operators would act on elements (like Numpy arrays and in
contrast to `list`, `tuple` and `array.array`). For standard numerical types,
such operations would be fast (or even very fast, using SIMD).

- For user-defined classes, a fundamental property for contiguous storage is
that all instances of the class have the same size in memory.

  Therefore, one needs to be able to disable dynamic features of Python for
  these classes. We need to be able to declare a class to be immutable and that
  one can't dynamically add attributes to the instances. For objects containing
  only fixed size objects, the size of the instances is fixed and computable.

  We also need to be able to declare the types of the attributes, but there is
  already a simple syntax for that in Python >= 3.6.

  For some cases, being able to declare that the instances of the class are
  immutable should also help for other optimizations.

- The `Vector` containers could support different modes of executions, "debug",
"dev" and "perf", that can be activated locally (with an API) and globally
(with an environment variable). For the performance mode, some type checks and
bound checks would be disabled.

## API

Let's say that we import the extension as:

```python
import vecpy as vp
```

A `Vector` can only store objects homogeneous in type (and only for types for
which all instances have the same size). To be simple, here, we propose that
the types of the objects are explicitly declared.

### Vectors of numbers

We can declare a type `Vector` of floats as:

```python
VectorF = vp.Vector[float]
```

Since all Python floats have the same size (they are "float64"), they can be
stored continuously in memory. In contrast, in Python 3, the size of an `int`
is not fixed (an `int` object can store very large integers) so
`vp.Vector[int]` should raise an error. To define an array of integer, one can
use for example `vp.Vector["int32"]`.

We can then declare vectors of different size like this:

```python
vec_100f = VectorF.empty(100)
vec_4f = VectorF.ones(4)
vec_2f = VectorF([2, 3])
```

We see that the size of the instances of `VectorF` is not fixed.

These vectors can of course be used as sequences, similarly to Numpy arrays:

```python
number = vec_2f[0]  # a float

tmp = 10 * vec_4f - 5  # another vector of floats
# no difficulty to speedup this loop
s = 0.0
for number in tmp:
    s += number
```

### Fixed-size vectors and vectors of fixed-size vector

We should be able to declare a fixed-size vector class:

```python
Vector4F = vp.Vector[float].subclass(size=4)
# can also be written as
Vector4F = vp.Vector.subclass(float, size=4)
```

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
    # in case we want to add methods
    ...

# or just (simpler)
Points = Vector[Point]

points = Points.empty(size=1000)

points[0] = [1, 2, 3]
# or
point = Point.zero()
point[0] = 1
points[0] = point  # copy
```

A Python interpreter with a JIT adapted for numerical tasks (like PyPy) could
run codes using such vectors very efficiently (fast iteration, much less type
checks, etc.). In particular, the latter simple code would basically be enough
to define the objects used in
https://github.com/paugier/nbabel/blob/master/py/bench_pypy4.py with no blocker
to accelerate the execution.

### Vector of instances of user-defined class

Under the hood, during the creation of a new concrete `Vector` class, we have
to obtain the size of one instance. For user-defined classes, this could be
done with a special class method `__size_of_instance__` (question: how one can
implement this?). We could use a decorator `vp.fixed_size_instances`.

Note: the special attribute `__slots__` can already be used in Python to
declare that it's going to be impossible to set a new attribute to an instance.
The decorator `vp.fixed_size_instances` could automatically set `__slots__`
from type annotations, see this example:

```python
@vp.fixed_size_instances
class MyNumericalClass:
    x: float
    y: float
    z: float

    ...
```

For such simple cases, a decorator could also set class methods like `zero`,
`one` and `empty`, and instance methods `fill`, `__add__`, etc.

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

## Comparison and compatibility with Numpy

`vecpy` would be much simpler than Numpy and targets specifically alternative
PyPy implementations with a JIT. The goal is only to provide an efficient
container for computationally intensive tasks in pure Python codes.

Numpy arrays can't contain Python objects continuously in memory. Moreover,
Numpy uses the CPython C API so that it's very difficult (or impossible) for
alternative Python interpreters to strongly accelerate Numpy codes.

It should be easy and very efficient (without copy) to convert vectors of
simple numerical types into contiguous Numpy arrays (and inversely).

## Comparison with `array.array`

`array.array` (https://docs.python.org/3/library/array.html) can only contain
few simple numerical types. Moreover,

```python
In [1]: from array import array
In [2]: a = array("f", [1., 1.])
In [3]: 2*a
Out[3]: array('f', [1.0, 1.0, 1.0, 1.0])
```

which is not what we usually want for such containers, especially for people
used to Numpy.

## Notes on a possible implementation

Unfortunately, I don't think this extension can be implemented in Python. I
guess one could use RPython but the resulting extensions would only be usable
with PyPy. Using the standard CPython C-API would be terrible in terms of
performance for PyPy and other alternative implementations. I guess it would
make sense to use Cython with a backend using HPy. However, HPy is still in the
early stages of development and this Cython backend targetting the HPy API is
just mentionned in some HPy documents. It could be interesting to try to
implement the core of such extension in C using the HPy API.

- Could it be possible with HPy to tell the PyPy JIT how to accelerate code
using `Vector`? Or would we need to also modify PyPy JIT?

- Could we use `memcpy` in `__modify_from__` to copy all the data of an object?
