from alphahousepythonheader cimport IntersectCompare
cimport PyIntersectCompare

cdef class PyIntersectCompare:
    def __cinit__(self):
        # cdef IntersectCompare * thisptr
        self.matching = 0
        self.nonMatching = 0
        self.nonMissing = 0
        self.total = 0

    cdef setFromPtr(self,IntersectCompare * thisptr):
        self.matching = thisptr.matching
        self.nonMatching = thisptr.nonMatching
        self.nonMissing = thisptr.nonMissing
        self.total = thisptr.total