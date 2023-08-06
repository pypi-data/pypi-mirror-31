
from libcpp.vector cimport vector
from libcpp cimport bool
from libcpp.string cimport string
import numpy as np

cimport ped
from alphahousepython cimport Haplotype, IntersectCompare, Gender, Pedigree, HaplotypeLibrary, NOPARENTPYTHON, Haplotype_pointer
from gen cimport PyGenotype
from hap cimport PyHaplotype
from haplib cimport PyHapLib
from libcpp.memory cimport shared_ptr

cdef class PyIndividual:
    def __cinit__(self):
        self.haplotypes = []
        pass
    
    def __dealloc__(self):
        pass


    def __str__(self):
        if (self.thisPtr.get()):
            return str(self.thisPtr.get().toString(), 'utf-8')
        else:
            return 0


    cdef setPointer(self, shared_ptr[Individual] ptr):
        self.thisPtr = ptr
        
    def getGenotype(self):
        if (not self.genotype):
            self.genotype = PyGenotype()
            self.genotype.setPointer(self.thisPtr.get().genotype)
        return self.genotype

    def getGenotypeSize(self):
        if (self.thisPtr.get().genotype):
            return self.thisPtr.get().genotype.get().getLength()
        else:
            return 0

    def indivParentHomozygoticFillIn(self):
        self.thisPtr.get().indivParentHomozygoticFillIn()

    def indivHomoFillIn(self):
        self.thisPtr.get().indivHomoFillIn()

    def makeIndividualGenotypeFromPhase(self):
        self.thisPtr.get().makeIndividualGenotypeFromPhase()

    def makeIndividualPhaseCompliment(self):
        self.thisPtr.get().makeIndividualPhaseCompliment()
        
    cdef setGenotype(self, PyGenotype genotype):
        gen = genotype

        self.thisPtr.get().genotype = shared_ptr[Genotype](genotype.thisPtr.get())

    def getHaplotype(self, int pos):
        if (len(self.haplotypes) == 0):
            for i in range(0, self.thisPtr.get().haplotypes.size()):
                t = PyHaplotype()
                t.setPointer(self.thisPtr.get().haplotypes[i])
                self.haplotypes.append(t)
        return self.haplotypes[pos]
        # return PyHaplotype(thisPtr.get().haplotypes[pos])
        
    def updatePointers(self):
        cdef PyHaplotype tempHap

        if (not self.genotype):
            self.genotype = PyGenotype()

        if (self.thisPtr.get().genotype):
            self.genotype.setPointer(self.thisPtr.get().genotype)

        if (len(self.haplotypes) == 0):
            for i in range(0, self.thisPtr.get().haplotypes.size()):
                tempHap = PyHaplotype()
                self.haplotypes.append(tempHap)
        for i in range(0, self.thisPtr.get().haplotypes.size()):
            tempHap = self.haplotypes[i]
            tempHap.setPointer(self.thisPtr.get().haplotypes[i])
            self.haplotypes[i] = tempHap
        # TODO could do sire dam too
        self.id = str(self.thisPtr.get().id,'utf-8')
        self.sireId = str(self.thisPtr.get().sireId, 'utf-8')
        self.damId = str(self.thisPtr.get().damId, 'utf-8')
    def isFounder(self):
        return self.thisPtr.get().founder

    def randomlyPhasedMidPoint(self):

        if (not self.thisPtr.get()):  raise NotImplementedError

        self.thisPtr.get().randomlyPhasedMidPoint()
        

    def getId(self):
        return str(self.thisPtr.get().id, 'utf-8')

    def getSireId(self):
        return str(self.thisPtr.get().sireId, 'utf-8')
    
    def getDamId(self):
        return str(self.thisPtr.get().damId, 'utf-8')
    def setHaplotype(self, int pos, PyHaplotype haplotype):

        if (len(self.haplotypes) > pos):
            self.haplotypes[pos] = haplotype
            self.thisPtr.get().haplotypes[pos] = shared_ptr[Haplotype](
                haplotype.thisPtr.get())

    def __dealloc__(self):
        pass

    def fillInhaplotypeBasedOnHaplotypeLibraryIndiv(self, PyHapLib hapLib, int index):

        self.thisPtr.get().fillInhaplotypeBasedOnHaplotypeLibrary(
            hapLib.thisPtr.get(), index)

cdef class PyPedigree:

    def __cinit__(self, path):
        cdef string id
        self.individuals = {}
        self.founders = []
        _path = path.encode('utf-8')
        self.thisPtr = <shared_ptr[Pedigree] > shared_ptr[Pedigree](new Pedigree(_path))
        self.thisPtr.get().sortPedigree()
        for i in range(0, self.thisPtr.get().sortedVec.size()):
            temp = PyIndividual()
            id = self.thisPtr.get().sortedVec[i].id
            temp.setPointer(self.thisPtr.get().pedigree[id])
            self.individuals[temp.getId()] = temp
            if (temp.isFounder()):
                self.founders.append(temp)
        self._fixRelationshipPointers()

    def __dealloc__(self):
        pass

    def _fixRelationshipPointers(self):
        cdef PyIndividual temp
        for i in self.individuals:
            temp = self.individuals[i]

            temp.sire = self.individuals[temp.getSireId()]
            temp.dam = self.individuals[temp.getDamId()]
            temp.offsprings = []
            for x in range(0, temp.thisPtr.get().offsprings.size()):
                 temp.offsprings.append(self.individuals[str( temp.thisPtr.get().offsprings[x].id, 'utf-8')])


    def __iter__(self):
        """Iterates through individuals and yields individual items """
        iter = self.individuals.items().__iter__()

        for i in iter:
            yield i[1]

    def __getitem__(self, item):
        if isinstance(item, list):
            return [self[i] for i in item]
        elif isinstance(item, slice):
            return [self[ii] for ii in range(*item.indices(len(self)))]
        elif isinstance(item, str):
            return self.individuals[item]
        else:
            try:
                return self.individuals[str(item)]
            except ValueError:
                raise TypeError(
                    "Wrong type given for getter:" + str(type(item)))

    def addGenotypesFromFile(self, str file, bool initAll=False):
        self.thisPtr.get().addGenotypeInfoFromFile(file.encode('utf-8'), initAll)
        for i in self:
            i.updatePointers()

    def compareToTrueFile(self, file: str, ids=None):
        """Returns yield and accuracy of genotype information for pedigree compared to a specified true file"""
        # with open(file, 'r').readlines() as f:
        if ids is None:
            ids = [ind for ind in self.individuals.keys()]
        f = open(file, 'r')

        yieldCount = 0
        diffs = 0
        totalLength = 0

        count = 0
        for l in f.readlines():
            t = l.strip().split(" ")

            g = PyGenotype(np.array(t[1:], dtype=int))
            count += 1
            if (t[0] in ids and t[0] in self.individuals):
                comp = self.individuals[t[0]].getGenotype()
                yieldCount += comp.countNotMissing()
                totalLength += len(comp)

                diffs += comp.countNotEqualExcludeMissing(g)

        yieldRet = float(yieldCount) / totalLength
        accuracy = 1 - float(diffs) / yieldCount

        f.close()

        return (yieldRet, accuracy)

    def getFounders(self):
        return self.founders

    def compareToTrueFile(self, file: str, ids=None):
        """Returns yield and accuracy of genotype information for pedigree compared to a specified true file"""
        # with open(file, 'r').readlines() as f:
        if ids is None:
            ids = [ind for ind in self.individuals.keys()]
        f = open(file, 'r')

        yieldCount = 0
        diffs = 0
        totalLength = 0
        for l in f.readlines():
            t = l.strip().split(" ")

            g = PyGenotype(np.array(t[1:], dtype=int))

            if (t[0] in ids and t[0] in self.individuals):
                comp = self.individuals[t[0]].genotype
                yieldCount += comp.countNotMissing()
                totalLength += len(comp)

                diffs += comp.countNotEqualExcludeMissing(g)

        yieldRet = float(yieldCount) / totalLength
        accuracy = 1 - float(diffs) / yieldCount

        f.close()

        return (yieldRet, accuracy)

    def compareToTrueFilePhase(self, file: str, ids=None):
        """Returns yield and accuracy of genotype information for pedigree compared to a specified true file"""
        # with open(file, 'r').readlines() as f:
        if ids is None:
            ids = [ind for ind in self.individuals.keys()]
        f = open(file, 'r')

        yieldCount = 0
        diffs = 0
        totalLength = 0
        lines = dict()
        for l in f.readlines():
            t = l.strip().split(" ")

            g = PyHaplotype(t[1:])

            if (t[0] in ids and t[0] in self.individuals):
                if t[0] not in lines:
                    lines[t[0]] = g
                else:
                    g0 = lines.pop(t[0])  # This also removes it from the dict.
                    g1 = g

                    comp0 = self.individuals[t[0]].getHaplotype(0)
                    comp1 = self.individuals[t[0]].getHaplotype(1)
                    yieldCount += comp0.countNotMissing()
                    yieldCount += comp1.countNotMissing()
                    totalLength += len(comp0) + len(comp1)

                    diffsAlign = comp0.countNotEqualExcludeMissing(
                        g0) + comp1.countNotEqualExcludeMissing(g1)
                    diffsNot = comp0.countNotEqualExcludeMissing(
                        g1) + comp1.countNotEqualExcludeMissing(g0)
                    diffs += min(diffsAlign, diffsNot)

        yieldRet = float(yieldCount) / totalLength
        if yieldCount != 0:
            accuracy = 1 - float(diffs) / yieldCount
        else:
            accuracy = -1
        f.close()

        return (yieldRet, accuracy)
    

def getConsensusPython(PyIndividual ind, list haplotypes, int nLoci, PyHaplotype override=None, int threshold=2, int tolerance=2):

    cdef PyHaplotype temp
    cdef vector[Haplotype*] tempHaps
    cdef Haplotype * returnHaplotype
    cdef Haplotype * overridePointer
    cdef PyHaplotype h
    temp = PyHaplotype()
    for h in haplotypes:
        tempHaps.push_back(h.thisPtr.get())

    if (override is not None):
        overridePointer = override.thisPtr.get()
    else:
        overridePointer = NULL
    returnHaplotype = ind.thisPtr.get().getConsensus(tempHaps, nLoci, overridePointer, threshold, tolerance)
    temp.setPointer(shared_ptr[Haplotype](returnHaplotype))
    return temp
