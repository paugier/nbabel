# Simple efficient 1d vector for Python: a proposal for a new extension

## Motivation

I did some experiments on writting numerically intensive codes in pure Python
object-oriented programming (OOP) and benchmarking them using PyPy (see [this
project](https://github.com/paugier/nbabel) and more specifically [these
microbenchmarks](https://github.com/paugier/nbabel/tree/master/py/microbench)).
I conclude from these experiments and my experience on scientific computing (in
particular in Python with [FluidDyn project](https://fluiddyn.readthedocs.io)
and [Transonic](https://transonic.readthedocs.io)) that:

1. PyPy is very promissing but it is really limited by some missing features of
Python. Even with the fastest implementation in pure Python (which is not easy
to write because we need to implement from scratch very basic data structures),
the performances are not so good compared to what can be done with other
languages. It's interesting to compare with Julia because the 2 technologies
are somehow similar (JIT compilation of 2 dynamic languages). To be fair, the
Julia code is in some aspects nicer and runs (something like 4 to 6 times)
faster. Julia's fastest implementation is based on `struct` defined by:

```julia
struct Point4D
    x::Float64
    y::Float64
    z::Float64
    w::Float64
end
Point4D(x,y,z) = Point4D(x, y, z, 0)
norm2(vec::Point4D) = vec.x^2 + vec.y^2 + vec.z^2 + vec.w^2
norm(vec::Point4D) = sqrt(norm2(vec))
import Base: +, -, *, zero
-(vec1::Point4D,vec2::Point4D) = Point4D(vec1.x - vec2.x, vec1.y - vec2.y, vec1.z - vec2.z, vec1.w - vec2.w)
...

points = Vector{Point}(undef, number_particles)
```

We'd like to be able to write something like that in object-oriented Python.
Note that by default a `struct` type is **immutable** and that `points` (a
vector of `Point`) corresponds in memory to a contiguous array of `4 *
number_particles` floats. (Note that it is like in Numpy for which
`np.ones(2)[0]` is a `np.float64` scalar which is immutable.)

2. It seems that the problem is not really about the Python language but about
the lack of a Python extension specialized for this task (Python OOP for
computing).

In my humble opinion, Numpy API is not adapted for this task. Numpy has been
designed for CPython, an interpreter without JIT compilation. (i) The strategy
to be (relatively) efficient is to avoid interactions with the Python
interpreter in computationally intensive parts. (ii) Thus, Numpy is not built
to define array types of particular dtype (to use these types for Python object
oriented codes and type annotations). (iii) Finally (but [this could be
changed](https://github.com/hpyproject/hpy/issues/137)), the core of Numpy uses
the CPython C API so it cannot be accelerated by alternative Python
implementations (in particular PyPy).

I think there are algorithms for which Python OOP style is very adapted and in
some sense better than Numpy style. Since the 2 programming styles are
complementary, I think we need a Python API compatible with OOP to express a
data organisation compatible with numerically intensive computing.

## Goal and proposed API

This document proposes and describes a new Python extension to write
computationally intensive code in OOP style. Of course, it has to be fully
compatible with efficient Python interpreters, like PyPy. Both Python JITs
(like PyPy, Numba or GraalPython) and ahead-of-time Python compilers (like
Pythran or Cython) could support this API.

The 3 main principles behind this project are:

1. One needs a Python API compatible with Python OOP for (i) pool of native
variables similar to C `struct` and (ii) native contiguous arrays of native
variables and "`struct`".

2. One needs to be able to disable some dynamical features of Python for some
objects to ease important optimizations.

3. One needs to support different modes of executions, "debug", "dev" and
"perf", that can be activated locally (with an API, as with the
`no_bound_check` decorator used further) and globally (with an environment
variable). In the performance mode, some type checks and bound checks would be
disabled.

Experiments with the N-Body problem
(https://github.com/paugier/nbabel/blob/master/py) suggest that this could lead
with PyPy to approximately a x5 speedup for pure Python style codes so that
such Python codes could be nearly as efficient as optimized Julia/C++/Fortran
codes.

Let's say that we import the extension as:

```python
import vecpy as vp
```

---

Disclaimer: this proposition is just a crazy idea from a scientist using
Python. I write this document to get some feedback about the project and its
technical feasibility.

---

## Data structures and types

We need 3 data structures and types that do not exist in pure Python:
`NativeBag`, `Vector` and `HomogeneousList`.

### 1. A metaclass to define C `struct`-like classes

One needs to be able to disable dynamic features of Python for user-defined
classes.

1. Standard Python classes and instances are too dynamics for very good
performance. For numerically intensive codes, one needs **immutable classes**
and **less dynamic instances**: we don't want to be able to add attributes to
the instances or dynamically change its class. Moreover, in many cases, we need
**immutable instances**.

2. The types of the attributes have to be fixed and defined in the class. The
types of the attributes could be limited to types corresponding to native types
(and maybe vectors of native types).

3. The native data have to be stored contiguously (as for C `struct`). The
corresponding Python objects point towards the raw data.

I think we need what I call here a `NativeBag` (I don't use the word `struct`
for clarity). There could be a constructor to build them from a `dict` or a
standard `class`.

```python
# from a dict
Point2D = vp.native_bag(dict(x=float, y=float))

# or with class syntax
@vp.native_bag
class Point3D:
    x: float
    y: float
    z: float

    def square(self):
        return self.x**2 + self.y**2 + self.z**2

    ...

p = Point2D(1, 1)
x = p.x

assert isinstance(x, float)

# behavior appropriate for good performance:

# no dynamic attribute creation
with pytest.raises(AttributeError):
    p.w = 1

# no dynamic modification of the class
with pytest.raises(TypeError):
    p.__class__ = tuple
```

For such simple cases, the decorator could also set class methods like `zero`,
`one` and `empty`, and instance methods `fill`, `__add__`, etc.

---

#### Mutability

Immutability is a very important property for high performance in Julia.
By default, `NativeBag` should be immutable:

```python
ImmutablePoint = vp.native_bag(dict(x=float, y=float))
p = ImmutablePoint(42, 42)
with pytest.raises(TypeError):
    p.x = 0.
```

I don't know if mutable `NativeBag` would really be useful:

```python
MutablePoint = vp.native_bag(dict(x=float, y=float), mutable=True)
p = MutablePoint(42, 42)
p.x = 0.
```

---

### 2. A container for homogeneous objects

In pure Python, there is no container specialized to contain a fixed number of
homogeneous objects (objects of the same types and of the same size).
(Actually, there is the module `array`, but it's very limited as explained
below.) Since we first need 1D sequence, let's call this type a `Vector` (as
in Julia).

The native elements have to be stored contiguously in memory. Alignment of the
native data is of course very important for performance. Moreover, JIT and AOT
compilers could know the type of the elements without type check.

The mathematical operators would act on elements (like Numpy arrays and in
contrast to `list`, `tuple` and `array.array`). For standard numerical types,
such operations would be fast (or even very fast, using SIMD).

We should be able to work with types, i.e. to define precise vector types and
to subclass them in Python. To be simple, here, we propose that the type of the
elements (the `dtype`) is explicitly declared.

#### Vectors of numbers

We can declare a type `Vector` of floats as:

```python
VectorF = vp.Vector[float]
```

Since all Python floats have the same size (they are "float64"), the
corresponding native numbers can be stored continuously in memory.

---

**Note Python 3 `int`:** In contrast, in Python 3, the size of an `int` is not
fixed (an `int` object can store very large integers) so `vp.Vector[int]`
should raise an error. To define an array of fixed-size integers, one can use
for example `vp.Vector["int32"]`.

---

We can then declare vectors of different size like this:

```python
vec_100f = VectorF.empty(100)
vec_4f = VectorF.ones(4)
vec_2f = VectorF([2, 3])
```

These vectors can of course be used as sequences, similarly to Numpy arrays:

```python
number = vec_2f[0]  # a float

tmp = 10 * vec_4f - 5  # another vector of floats
# no difficulty to speedup this loop (here, a JIT can bypass the Python objects)
s = 0.0
for number in tmp:
    s += number
```

#### Vectors of `NativeBag` instances

A `Vector` can only store objects homogeneous in type and size. For
user-defined classes, a fundamental property for contiguous storage is that all
instances of the class have the same size in memory. For `NativeBag`, the size
of the instances (the Python object and its associated native data) is fixed
and computable, so one should be able to use:

```python
@vp.native_bag
class Point4D:
    x: float
    y: float
    z: float
    w: float

    def square(self):
        # a JIT could completely remove the overhead,
        # vectorize this and use a SIMD instruction
        return self.x**2 + self.y**2 + self.z**2 + self.w**2

Points = vp.Vector[Point4D]
positions = Points.empty(1000)
velocities = Points.empty(1000)
```

Note that the object `positions` contains 1 native array of 4000 floats.

A Python interpreter with a JIT adapted for numerical tasks (like PyPy) could
run codes using such vectors/objects much more efficiently than codes using
standard Python list (fast iteration, much less type checks, etc.). In
particular, the simple code just above would basically be enough to define the
objects used in https://github.com/paugier/nbabel/blob/master/py/bench_pypy4.py
with no blocker to accelerate the execution. One can think about how the
following code could be accelerated with a good JIT. I added the type
annotations but note that they are actually useless for PyPy.

```python
@vp.no_bound_check
def compute_accelerations(
        accelerations: Vector[Point],
        masses: Vector[float],
        positions:Vector[Point],
):
    assert len(accelerations) == len(masses) == len(positions)
    nb_particules = len(masses)
    for i0, position0 in enumerate(positions):
        for i1 in range(i0 + 1, nb_particules):
            delta = position0 - positions[i1]
            distance_cube = delta.norm_cube()
            accelerations[i0] -= masses[i1] / distance_cube * delta
            accelerations[i1] += masses[i0] / distance_cube * delta
```

---

**Note on views:** As in Numpy, we should prefer views to copies for slicing:

```python
a = vp.Vector[float].zeros(4)
b = a[:2]
b += 1
print(a)
```

should return `[1, 1, 0, 0]`. Moreover, Vectors should have a `copy` method.

---

### 3. `HomogeneousList`

`list`s behave like arrays of references. For some cases, it could be useful to
have homogeneous lists. It would allow some optimizations compared to what can
be done with standard heterogenous lists.

```python
Points = vp.HomogeneousList[Point]
points = Points.empty(1000)
```

## Comparison and compatibility with Numpy

`vecpy` would be much simpler than Numpy (very small API) and targets
specifically alternative Python implementations with a JIT. The goal is only to
provide an API adated for computationally intensive tasks in pure Python codes.

Numpy arrays can't contain Python objects continuously in memory. It's possible
to define new structured data types in Numpy
(<https://numpy.org/doc/stable/reference/arrays.dtypes.html>), but one can't
use them in OOP (for example to associated methods to these dtypes). Moreover,
these dtypes are mutable:

```python
dt = np.dtype([("x", float), ("y", float)])
a = np.ones(2, dtype=dt)
elem = a[0]
# the elements are mutable (this modifies the array)
elem["x"] = 2.
```

Moreover, Numpy uses the CPython C API so that it's very difficult (or
impossible?) for alternative Python interpreters to accelerate Numpy codes.

It should be easy and efficient (without copy) to convert vectors of simple
numerical types into contiguous Numpy arrays (and inversely).

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

- Could it be possible with HPy to tell the PyPy JIT (in the extension) how to
accelerate code using `Vector`? Or would we need to also modify PyPy JIT?

- Is it possible to initialize a C array of (homogeneous) Python objects?
(needed for `Vector`)

- Could we use `memcpy` in `__modify_from__` to copy all the data of an object?

---

Using cffi could be another option...

---
