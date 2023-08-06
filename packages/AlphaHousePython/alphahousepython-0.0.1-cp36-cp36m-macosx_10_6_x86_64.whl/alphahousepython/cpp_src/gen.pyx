
# Cython interface file for wrapping the object
#
#

from libcpp.vector cimport vector
from libcpp cimport bool
from libcpp.string cimport string
from alphahousepython cimport Haplotype, Genotype, IntersectCompare, MISSINGCODE
from hap cimport PyHaplotype
from libcpp.memory cimport shared_ptr, make_shared
# from alphahousepython cimport PyHaplotype, PyGenotype
import numpy as np
cimport gen
cimport numpy as np

DTYPE = np.int8

    

# creating a cython wrapper class
cdef class PyGenotype:
    # cdef Genotype * thisPtr      # hold a C++ instance which we're wrapping

    def __cinit__(self, array=None, start=0, haplotypes = None, length= 0):
        self.start = start
        if array is not None:
            self.thisPtr = <shared_ptr[Genotype] > shared_ptr[Genotype](new Genotype(array, start))
        elif haplotypes is not None:
            self.__initFromHaps(haplotypes[0], haplotypes[1])
        elif length!= 0:
            array = np.full(length, fill_value=9, dtype=np.int8)
            self.thisPtr = <shared_ptr[Genotype] > shared_ptr[Genotype](new Genotype(array, start))
        if (self.thisPtr):
            self.length = self.thisPtr.get().getLength()

    def __initFromHaps(self, PyHaplotype h1, PyHaplotype h2):

        array = np.full(len(h1), fill_value=9, dtype=np.int8)
        for i, (one, two) in enumerate(zip(h1.toIntArray(), h2.toIntArray())):
            if ((one == 1) and (two == 1)):
                    array[i] = 2
            elif ((one == 0) and (two == 0)):
                array[i] = 0
            elif (one == MISSINGCODE or two == MISSINGCODE):
                # if either is missing - set to missing
                array[i] = MISSINGCODE
            else:
                # if one is 1, and the other is 0
                array[i] = 1
        self.thisPtr = <shared_ptr[Genotype] > shared_ptr[Genotype](new Genotype(array, 0))

    cdef setPointer(self, shared_ptr[Genotype] ptr):
        self.thisPtr = ptr
        self.length = self.thisPtr.get().getLength()
    
    def printPointer(self):
       x = "{0:x}".format( < unsigned long > self.thisPtr.get())
       print(x)
       return x



    def __dealloc__(self):
        # del self.thisPtr
        pass

    def getLength(self):
        return self.length;

    def setGenotype(self,int pos, int value):
        self.thisPtr.get().setGenotype(pos, value)

    def getGenotype(self,pos):
        return self.thisPtr.get().getGenotype(pos)
    
    def getEnd(self):
        return self.thisPtr.get().getEnd()
        
    def countMissing(self):
        return self.thisPtr.get().countMissing()

    def countNotMissing(self):
        return self.thisPtr.get().countNotMissing()

    def countMismatches(self, PyGenotype other):
        return self.thisPtr.get().countMismatches(other.thisPtr.get())
    def __eq__(self, PyGenotype otherGenotype):
        return self.checkEqual(otherGenotype)

    def checkEqual(self, PyGenotype otherGenotype):
        
        return self.thisPtr.get().checkEqual(otherGenotype.thisPtr.get())
    def __iter__(self):
        for i in range(0, len(self)):
            yield self.thisPtr.get().getGenotype(i)

    def __str__(self):
        return str(self.thisPtr.get().toString(), 'utf-8')

    def __setitem__(self, int key, int value):
        self.thisPtr.get().setGenotype(key, value)

    def __getitem__(self, item):
        if isinstance(item, slice):
            return [self[ii] for ii in range(*item.indices(len(self)))]
            # TODO think
            # return self.getSubsetHaplotype(start=item.start,end=item.stop)
        elif isinstance(item, list):
            return [self[ii] for ii in item]
        elif isinstance(item, int):
            if item < 0 or item >= len(self):
                raise IndexError("The index (%d) is out of range." % item)
            else:
                return self.thisPtr.get().getGenotype(item)


    def percentageMissing(self):
        return self.thisPtr.get().percentageMissing()
    

    def __len__(self):
        return self.thisPtr.get().getLength()
        
    def getSubsetGenotype(self, int start, int end):
        

        cdef PyGenotype t
        cdef Genotype * tempptr

        tempptr = self.thisPtr.get().getSubsetGenotype(start, end)

        t = PyGenotype()
        t.setPointer(shared_ptr[Genotype](tempptr))
        return t

    def isMissing(self, int pos):
        
        return self.thisPtr.get().isMissing(pos)

    def toIntArray(self):
        ret = self.thisPtr.get().toIntArray()
        return np.array(ret, dtype=np.int8)

    def setFromHaplotypesIfMissing(self, h1, h2):
       

        other = PyGenotype(haplotypes=[h1, h2])
        self.setFromOtherIfMissing(other)

    def complement(self, PyHaplotype  hap):
        cdef PyHaplotype new
        cdef Haplotype * tempptr
        tempptr = self.thisPtr.get().complement(hap.thisPtr.get())
        new = PyHaplotype()
        new.setPointer(shared_ptr[Haplotype](tempptr))

        return new

    def setFromOtherIfMissing(self, PyGenotype other):
        self.thisPtr.get().setFromOtherIfMissing(other.thisPtr.get())
    
    def numHet(self):
        return self.thisPtr.get().numHet()

    def countNotEqualExcludeMissing(self, PyGenotype other):
        return self.thisPtr.get().countNotEqualExcludeMissing(other.thisPtr.get())
    
    def countNotEqual(self, PyGenotype other): 
        return self.thisPtr.get().countNotEqual(other.thisPtr.get())

    def isHaplotypeCompatible(self, PyHaplotype other,int threshold = 0):
        return self.thisPtr.get().isHaplotypeCompatible(other.thisPtr.get(), threshold)

