
from python import Python


def setitem(obj: PythonObject, key: String, value: Int):
    # obj is copied but we can modified the Python object
    obj.__setitem__(key, value)


def setitem(obj: PythonObject, idx: Int, value: Int):
    # obj is copied but we can modified the Python object
    obj.__setitem__(idx, value)


def main():
    let python_builtins: PythonObject = Python.import_module("builtins")
    let dict: PythonObject = python_builtins.dict
    let d: PythonObject = dict()
    # error: expression must be mutable in assignment (with Mojo 0.0.5)
    # d["a"] = 0
    # works:
    d.__setitem__("a", 0)
    print(d["a"])

    d.__setitem__("a", 1)
    print(d["a"])

    setitem(d, "a", 2)
    print(d["a"])

    print("With Numpy:")

    np = Python().import_module("numpy")
    let a = np.zeros(2)

    print(a[0])

    setitem(a, 0, 1)
    print(a[0])
