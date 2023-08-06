# distutils: language = c++
# distutils: sources = ['alphahousenative/Haplotype.cpp', 'alphahousenative/IntersectCompare.cpp', 'alphahousenative/Genotype.cpp']

# Cython interface file for wrapping the object
#
#

from libcpp.vector cimport vector
from libcpp.map cimport map
from libcpp cimport bool
from libcpp.string cimport string
from libcpp.memory cimport shared_ptr 
from cpython.buffer cimport PyObject_GetBuffer, PyBUF_FULL 
ctypedef Individual* Individual_pointer
ctypedef Haplotype* Haplotype_pointer
NOPARENTPYTHON = "0"
cdef extern from "alphahousepython.h" namespace "alphahousepython":

    cdef int MISSINGCODE
    cdef int ERRORCODE
    cdef string NOPARENT

    cdef cppclass Haplotype:
        Haplotype(vector[int], int start,int weight) except +
        #Haplotype(int,int,int) except +
        int start
        int weight
        vector[int] array
        int getLength()
        void setPhase(int,int) except +
        int getPhase(int)  except +
        int getPhaseWithGlobalIndex(int) except +
        bool containsIndex(int)
        int countMissing()
        int countNotMissing()
        bool checkEqual(Haplotype * )
        IntersectCompare * compareHapsOnIntersect(Haplotype*)
        Haplotype * getSubsetHaplotype(int, int)
        Haplotype * getSubsetHaplotypeGlobal(int, int)
        string toString()
        vector[int] toIntArray()
        void setFromOtherIfMissing(Haplotype *)
        void setFromGenotypeIfMissing(Genotype *)
        int countNotEqualExcludeMissing(Haplotype *)

    cdef cppclass IntersectCompare:
        IntersectCompare(int, int, int, int) 
        int matching
        int total
        int nonMissing
        int nonMatching
    
    cdef cppclass Genotype:
        Genotype(vector[int], int start) except +
        int start
        vector[int] array
        int getLength()
        void setGenotype(int,int)  except +
        int getGenotype(int)  except +
        int countMissing() except +
        bool containsIndex(int) except +
        int countNotMissing() except +
        int getEnd() except +
        int countMismatches(Genotype *) except +
        bool checkEqual(Genotype * ) except +
        Genotype * getSubsetGenotype(int, int) except +
        string toString() except +
        vector[int] toIntArray() except +
        Haplotype * complement() except +
        int numHet() except +
        int isMissing(int) except +
        float percentageMissing() except +
        void setFromOtherIfMissing(Genotype *) except +
        int countNotEqual(Genotype *) except +
        int countNotEqualExcludeMissing(Genotype *) except +
        Haplotype * complement(Haplotype *) except +
        bool isHaplotypeCompatible(Haplotype *, int)  except +
    


    cdef cppclass HaplotypeLibrary:
        vector[int] coreLengths
        vector[float] offsets
        vector[Haplotype *] haplotypes

        HaplotypeLibrary(vector[Haplotype *] & haplotypes)
        void addHap(shared_ptr[Haplotype] hap)
    
    cdef enum Gender:
        Male = 1
        Female = 2
        Unknown = 0

    cdef cppclass Individual:
        string id
        int recId
        string sireId
        string damId
        vector[Individual*] offsprings
        Individual* sire
        Individual* dam
        bool founder
        int generation
        int inconsistenciesCount;
        shared_ptr[Genotype] genotype
        vector[shared_ptr[Haplotype]] haplotypes
        Gender gender

        Individual(string, string, string,bool, int, Gender, shared_ptr[Genotype], vector[shared_ptr[Haplotype],unsigned long])
        void addOffspring(Individual *)
        void removeOffspring(Individual *)
        void randomlyPhasedMidPoint() except +
        string toString()
        #MendellianInconsistencies * getInconsistencies()
        void indivHomoFillIn() except +
        void makeIndividualPhaseCompliment() except +
        void indivParentHomozygoticFillIn() except +
        void makeIndividualGenotypeFromPhase()  except +
        void fillInhaplotypeBasedOnHaplotypeLibrary(HaplotypeLibrary*, int index)  except +
        Haplotype* getConsensus(vector[Haplotype*], unsigned long, Haplotype*, int,int)  except +

    # TODO dummy indiv 




    cdef cppclass Pedigree:

        map[string, shared_ptr[Individual]] pedigree;
        vector[shared_ptr[Individual]] founders;
        vector[vector[Individual_pointer]] generations;
        vector[Individual*] sortedVec;


        Pedigree(string)

        Individual& operator[](string)

        #Pedigree(vector[vector[string]])

        void sortPedigree();

        void checkOffspring(Individual *, map[string,bool],vector[vector[shared_ptr[Individual]]],int currentGeneration)

        void addGenotypeInfoFromFile(string, bool);
        void addPhaseInfoFromFile(string);
        unsigned long getLength()
        void findMendelianInconsistencies(float threshold =0.05,string filepath="" )
        






