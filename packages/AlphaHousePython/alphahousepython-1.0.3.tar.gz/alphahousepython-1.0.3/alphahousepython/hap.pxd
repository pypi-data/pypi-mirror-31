from alphahousepython cimport Haplotype
from libcpp.memory cimport shared_ptr

cdef class PyHaplotype:
    cdef shared_ptr[Haplotype] thisPtr
    cdef int start
    cdef int weight
    cdef public: 
        cdef int length
    cdef setPointer(self,shared_ptr[Haplotype] ptr)