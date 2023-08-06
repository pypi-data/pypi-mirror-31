

from libcpp.vector cimport vector
from libcpp.memory cimport shared_ptr
from alphahousepythonheader cimport Haplotype, HaplotypeLibrary, Genotype
from hap cimport PyHaplotype
from libcpp.memory cimport shared_ptr
from Exceptions import NoPointerException
import itertools
import math
cdef class PyHapLib:

    def __cinit__(self,haplotypes):

        
        cdef vector[Haplotype *] v
        cdef PyHaplotype hap
        cdef Haplotype * haplotypePtr
        for hap in haplotypes:
            haplotypePtr = hap.thisPtr.get()
            v.push_back(haplotypePtr)
        self.thisPtr = <shared_ptr[HaplotypeLibrary] > shared_ptr[HaplotypeLibrary](new HaplotypeLibrary(v))



    def __dealloc__(self):
        pass


    def incrementWeight(self,index):

        if (not self.thisPtr):
            raise NoPointerException
        
        self.thisPtr.get().haplotypes[index].weight = self.thisPtr.get().haplotypes[index].weight+1


class HaplotypeIterator(object):

    def __init__(self, coreLengths, offsets, haplotype):
        self.coreLengths = coreLengths
        self.maxSnp = len(haplotype)
        self.haplotype = haplotype
        self.offsets = offsets

    def __iter__(self):
        for coreLength in self.coreLengths:
            for offset in self.offsets:
                end = 0
                index = 0
                while end < self.maxSnp:
                    end, subHap = self.getHap(coreLength, offset, index)
                    yield ((coreLength, offset, index), subHap)
                    index = index + 1

    def getHap(self, coreLength, offset, index):

        coreLength = min(coreLength, self.maxSnp)
        offset = math.floor(offset*coreLength)
        start = max(index*coreLength - offset, 0)
        end = min((index + 1)*coreLength - offset, self.maxSnp)
        return (end, self.haplotype.getSubsetHaplotype(start=start, end=end))


class HaplotypeLibraryFrom(object):

    def __init__(self, individuals=[], coreLengths=[100]):
        self.coreLengths = coreLengths
        self.offsets = [0, .5]
        self.haplotypes = dict()

        for ind in individuals:
            self.add(ind.haplotypes[0])
            self.add(ind.haplotypes[1])

    def add(self, hap):
        hapIter = HaplotypeIterator(self.coreLengths, self.offsets, hap)
        for pair in hapIter:
            index, subHap = pair
            if index not in self.haplotypes:
                self.haplotypes[index] = []
            if subHap.countMissing() == 0:
                try:
                    ii = self.haplotypes[index].index(subHap)
                    self.haplotypes[index][ii].incrementWeight()
                    # print("weight increased", self.haplotypes[index][ii].weight)
                except ValueError:
                    # print("Hap added")
                    self.haplotypes[index].append(subHap)

    def __iter__(self):
        for key, value in self.haplotypes.items():
            for v in value:
                yield v

    def toList(self):
        haps = self.haplotypes.values()

        return list(itertools.chain(*haps))
