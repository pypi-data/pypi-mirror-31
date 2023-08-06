from alphahousepythonheader cimport Pedigree, Genotype,Individual,IntersectCompare

cdef class PyIntersectCompare:

    cdef public:
        cdef int matching
        cdef int nonMatching
        cdef int nonMissing
        cdef int total
        cdef setFromPtr(self,IntersectCompare * thisptr)