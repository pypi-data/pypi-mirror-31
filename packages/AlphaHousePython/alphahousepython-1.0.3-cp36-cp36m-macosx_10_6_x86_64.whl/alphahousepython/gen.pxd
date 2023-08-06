from alphahousepython cimport Genotype
from libcpp.memory cimport shared_ptr 

cdef class PyGenotype:
    cdef shared_ptr[Genotype] thisPtr
    cdef public int start
    cdef public int length
    cdef setPointer(self,shared_ptr[Genotype] ptr)