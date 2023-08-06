from alphahousepython cimport Pedigree, Genotype,Individual
from gen cimport PyGenotype
from hap cimport PyHaplotype
from libcpp.vector cimport vector
from libcpp.memory cimport shared_ptr

cdef class PyIndividual:
    
    cdef shared_ptr[Individual] thisPtr
    cdef public:
        cdef PyGenotype genotype
        cdef list offsprings
        cdef PyIndividual sire
        cdef PyIndividual dam
        cdef str id
        cdef str sireId
        cdef str damId
        cdef list haplotypes
     
    # cdef __cinit__(self, Individual *  ptr)
    cdef setGenotype(self,PyGenotype genotype)
    cdef setPointer(self, shared_ptr[Individual])


cdef class PyPedigree:
    cdef public dict individuals
    cdef  shared_ptr[Pedigree] thisPtr
    cdef public list founders



