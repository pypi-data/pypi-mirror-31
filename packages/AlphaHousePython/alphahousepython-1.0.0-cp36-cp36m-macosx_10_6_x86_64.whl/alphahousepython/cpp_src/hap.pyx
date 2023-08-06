
# Cython interface file for wrapping the object
#
#

from libcpp.vector cimport vector
from libcpp cimport bool
from libcpp.string cimport string
from libcpp.memory cimport shared_ptr
import numpy as np

cimport hap
from alphahousepython cimport Haplotype, IntersectCompare
from gen cimport PyGenotype
from PyIntersectCompare cimport PyIntersectCompare
from ped cimport PyIndividual
from Exceptions import NoPointerException
# cimport numpy as np

DTYPE = np.int8


# creating a cython wrapper class
cdef class PyHaplotype:

    
    # cdef Haplotype * thisPtr      # hold a C++ instance which we're wrapping
    def __cinit__(self, array=None, start=0, weight = 0):
        
        if array is not None:
            
            if not isinstance(array, np.ndarray):
                array = np.array(array, dtype=np.int)
            self.thisPtr = <shared_ptr[Haplotype] > shared_ptr[Haplotype](new Haplotype(array, start, weight))
            self.start = self.thisPtr.get().start;
            self.length = self.thisPtr.get().getLength();
        else:
            pass;


    cdef setPointer(self,shared_ptr[Haplotype] ptr):
        self.thisPtr = ptr
        self.start = ptr.get().start
        self.weight = ptr.get().weight
        self.length = ptr.get().getLength()
    def __dealloc__(self):
        pass
        # if (self.thisPtr):
        #     del self.thisPtr

    def printPointer(self):
       x = "{0:x}".format( < unsigned long > self.thisPtr.get())
       print(x)
       return x

    def getLength(self):
        if (self.thisPtr):
            return self.thisPtr.get().getLength()
        else:
            raise NoPointerException()
    def setPhase(self,int pos, int value):
        if (self.thisPtr):
            self.thisPtr.get().setPhase(pos, value)
        else:
            raise NoPointerException()

    def getWeight(self):
        return self.weight
        

    def setWeight(self, int value ):
        self.weight = value
    
    def getStart(self):
        return self.start

    def setStart(self,int value):
        self.start = value

    def getPhaseGlobal(self,int gloIndex):
        if (self.thisPtr):
            return self.thisPtr.get().getPhaseWithGlobalIndex(gloIndex)
        else:
            raise NoPointerException()

    def getPhase(self,pos):
        if (self.thisPtr):
            return self.thisPtr.get().getPhase(pos)
        else:
            raise NoPointerException()

    def incrementWeight(self):

        if (not self.thisPtr):
            raise NoPointerException

        self.thisPtr.get().weight = self.thisPtr.get(
        ).weight+1

    def countMissing(self):
        if (self.thisPtr):
            return self.thisPtr.get().countMissing()
        else:
            raise NoPointerException()
    def countNotMissing(self):
        if (self.thisPtr):
            return self.thisPtr.get().countNotMissing()
        else:
            raise NoPointerException()
    def __eq__(self, otherHaplotype):
        return self.checkEqual(otherHaplotype)

    def checkEqual(self, PyHaplotype otherHaplotype):
        if (self.thisPtr):
            return self.thisPtr.get().checkEqual(otherHaplotype.thisPtr.get())
        else:
            raise NoPointerException()

    def intersectCompare(self, PyHaplotype otherHaplotype):
        cdef IntersectCompare * isptr

        isptr = self.thisPtr.get().compareHapsOnIntersect(otherHaplotype.thisPtr.get());


        return (isptr.matching, isptr.total, isptr.nonMissing, isptr.nonMatching)
    
    def __str__(self):
        if (self.thisPtr):
            return str(self.thisPtr.get().toString(), 'utf-8')
        else:
            return "NULL"
    def __len__(self): 
        return self.length

    def __iter__(self):
        if (self.thisPtr):
            for i in range(0, len(self)):
                yield self.thisPtr.get().getPhase(i)
    
    def __setitem__(self,int key,int value):
        if (self.thisPtr):
            self.thisPtr.get().setPhase(key, value)
        else:
            raise NoPointerException()
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
                if (self.thisPtr):
                    return self.thisPtr.get().getPhase(item)
                else:
                    raise NoPointerException()
        
    
    def percentageMissing(self):
        return self.countMissing() / len(self)
    def toIntArray(self):
        # ret = np.empty(len(self), np.int8)
        if (self.thisPtr):
            ret = self.thisPtr.get().toIntArray()
            return np.array(ret,dtype=np.int8)
        else:
            raise NoPointerException()
    def getSubsetHaplotype(self, int start, int end):
        

        cdef PyHaplotype new
        cdef Haplotype * tempptr

        if (self.thisPtr):
            tempptr = self.thisPtr.get().getSubsetHaplotype(start, end)

            t = PyHaplotype()
            t.setPointer(shared_ptr[Haplotype](tempptr))
            return t
        else:
            raise NoPointerException()

    def getSubsetHaplotypeGlobal(self, int globalStart, int globalEnd):

        cdef PyHaplotype new
        cdef Haplotype * tempptr
        if (self.thisPtr):
            tempptr = self.thisPtr.get().getSubsetHaplotypeGlobal(globalStart, globalEnd)
        else:
            raise NoPointerException()
        t = PyHaplotype()
        t.setPointer(shared_ptr[Haplotype](tempptr))
        return t

    def contains(self, int index) :
        if (self.thisPtr):
            return self.thisPtr.get().containsIndex(index)
        else:
            raise NoPointerException()

    def setFromOtherIfMissing(self, PyHaplotype other):
        if (self.thisPtr):
            self.thisPtr.get().setFromOtherIfMissing(other.thisPtr.get())
        else:
            raise NoPointerException()
    def setFromGenotypeIfMissing(self, PyGenotype other):
        if (self.thisPtr):
            self.thisPtr.get().setFromGenotypeIfMissing(other.thisPtr.get())
        else: raise NoPointerException()
    def countNotEqualExcludeMissing(self, PyHaplotype other):
        if (self.thisPtr):
            return self.thisPtr.get().countNotEqualExcludeMissing(other.thisPtr.get())
        else:
            raise NoPointerException()
def compareHapsOnIntersectArray(PyHaplotype one, PyHaplotype two):
        temp = PyIntersectCompare()
        if (one.thisPtr and two.thisPtr):
            temp.setFromPtr(one.thisPtr.get().compareHapsOnIntersect(two.thisPtr.get()))
        else: raise NoPointerException()
        return temp


