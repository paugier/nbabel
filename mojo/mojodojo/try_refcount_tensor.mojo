from memory.unsafe import Pointer, DTypePointer
from memory.memory import memset_zero

from tensor import Tensor


struct RefTensor[dtype: DType]:
    var ptr_tensor: Pointer[Tensor[dtype]]
    var ptr_ref_count: Pointer[Int]

    fn __init__(inout self, size: Int):

        self.ptr_tensor = Pointer[Tensor[dtype]].alloc(1)

        tensor = self.ptr_tensor[0]
