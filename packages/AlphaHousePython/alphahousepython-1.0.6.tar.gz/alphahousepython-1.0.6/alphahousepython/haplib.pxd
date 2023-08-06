from alphahousepythonheader cimport HaplotypeLibrary
from libcpp.memory cimport shared_ptr

cdef class PyHapLib:
    cdef shared_ptr[HaplotypeLibrary] thisPtr


