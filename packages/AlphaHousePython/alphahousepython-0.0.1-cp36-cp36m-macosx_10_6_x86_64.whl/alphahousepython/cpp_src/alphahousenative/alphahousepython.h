#include <vector>
#include <sstream>
#include <algorithm>
#include <boost/dynamic_bitset.hpp>
#include <boost/algorithm/string/split.hpp>
#include <boost/algorithm/string/classification.hpp>
#include <boost/algorithm/string/classification.hpp>
#include <map>
#include <fstream>
#include <iostream>
#include <vector>
#include <iostream>
using std::map;
using std::ostream;
using std::shared_ptr;
using std::string;
using std::tuple;
using std::vector;
namespace alphahousepython
{
const bool MEMORYSAVE = true;
const std::string NOPARENT = "0";
const int MISSINGCODE = 9;
const int ERRORCODE = 9;

class IntersectCompare
{
  public:
    int matching;
    int total;
    int nonMissing;
    int nonMatching;

    IntersectCompare(int matchingIn, int totalIn, int nonMissingIn, int nonMatchingIn);
    ~IntersectCompare();
};

class DifferentLengthException : public std::exception
{
    virtual const char *what() const throw()
    {
        return "Objects have different lengths";
    }
};

class UnrelatedOffspringException : public std::exception
{
    const char *what() const throw() override
    {
        return "Offspring unrelated to animal";
    }
};

class OutOfRangeException : public std::exception
{
    const char *what() const throw() override
    {
        return "index given is out of range";
    }
};

class NoGenotypeException : public std::exception
{
    const char *what() const throw() override
    {
        return "No Genotype given";
    }
};

class NoHaplotypeException : public std::exception
{
    const char *what() const throw() override
    {
        return "No Haplotype given!";
    }
};

class Genotype;

class Haplotype
{
  protected:
  public:
    std::vector<int> array;
    boost::dynamic_bitset<> phase;
    boost::dynamic_bitset<> missing;
    unsigned int start;
    unsigned int weight;

    explicit Haplotype(std::vector<int> arrayIn, int start = 0, int weight = 0);

    Haplotype(boost::dynamic_bitset<> phaseIn, boost::dynamic_bitset<> missingIn, int start = 0, int weight = 0);

    Haplotype(unsigned long size, unsigned int value = MISSINGCODE, int start = 0, int weight = 0);

    ~Haplotype();

    int getLength();

    int countMissing();

    int countNotMissing();

    void setPhase(int, int);

    int getPhase(int);
    int getPhaseWithGlobalIndex(int);

    void setFromGenotypeIfMissing(Genotype *);

    float percentageMissing();

    bool checkEqual(Haplotype *otherhap);

    int getEnd();

    bool containsIndex(int);

    Haplotype *getSubsetHaplotype(int, int);
    Haplotype *getSubsetHaplotypeGlobal(int, int);

    IntersectCompare *compareHapsOnIntersect(Haplotype *otherHap);

    void setFromOtherIfMissing(Haplotype *);

    std::string toString();

    std::vector<int> toIntArray();

    int countNotEqualExcludeMissing(Haplotype *);
};

class Genotype
{
  public:
    std::vector<int> array;
    boost::dynamic_bitset<> homo;
    boost::dynamic_bitset<> additional;
    int start;

    Genotype(std::vector<int> arrayIn, int startIn = 0);

    Genotype(boost::dynamic_bitset<>, boost::dynamic_bitset<>, int startIn = 0);

    Genotype(Haplotype *h1, Haplotype *h2, int startIn = 0);

    //    SET TO VALUE CONSTRUCTOR
    Genotype(unsigned long size, unsigned int value = MISSINGCODE);

    ~Genotype();

    int getLength();

    int countMissing();

    int countNotMissing();

    void setGenotype(int, int);

    int getGenotype(int);

    float percentageMissing();

    bool checkEqual(Genotype *otherhap);

    int getEnd();

    bool containsIndex(int);

    Genotype *getSubsetGenotype(int, int);

    IntersectCompare *compareHapsOnIntersect(Genotype *otherHap);

    bool isHaplotypeCompatible(Haplotype *, int);

    int countMismatches(Genotype *);

    bool isMissing(int);

    int numHet();

    void setFromOtherIfMissing(Genotype *);

    void setFromHaplotypesIfMissing(Haplotype *, Haplotype *);

    Haplotype *complement(Haplotype *);

    std::string toString();

    std::vector<int> toIntArray();

    int countNotEqual(Genotype *other);

    int countNotEqualExcludeMissing(Genotype *other);
};

class MendellianInconsistencies
{
  public:
    boost::dynamic_bitset<> maternalInconsistent;
    boost::dynamic_bitset<> paternalInconsistent;
    boost::dynamic_bitset<> individualInconsistent;

    boost::dynamic_bitset<> paternalConsistent;
    boost::dynamic_bitset<> maternalConsistent;
    boost::dynamic_bitset<> individualConsistent;

    MendellianInconsistencies(Genotype *, Genotype *, Genotype *);
};

class HaplotypeLibrary
{
  public:
    std::vector<int> coreLengths;
    std::vector<float> offsets;
    std::vector<Haplotype *> haplotypes;

    HaplotypeLibrary(vector<Haplotype *> &haplotypes);
    void addHap(Haplotype *hap);
    std::vector<Haplotype *> getMatching(Haplotype &hap);
};

enum gender
{
    Male = 1,
    Female = 2,
    Unknown = 0
};

class Individual
{
  public:
    std::string id;
    int recId{};
    std::string sireId;
    std::string damId; // TODO could maybe make these pointers
    std::vector<Individual *> offsprings;
    Individual *sire;
    Individual *dam;
    bool founder;
    int generation{};
    int inconsistenciesCount = 0;
    std::shared_ptr<Genotype> genotype;
    std::vector<std::shared_ptr<Haplotype>> haplotypes{};
    enum gender gender;

    Individual() = default;
    ~Individual();

    //    TODO write copy constructor
    Individual(std::string id, std::string sireId, std::string damId, bool founder, int recId,
               enum gender gender = Unknown, std::shared_ptr<Genotype> genotype = nullptr,
               std::vector<std::shared_ptr<Haplotype>> haplotypes = {}, unsigned long initToSnps = 0);

    void addOffspring(Individual *ind);
    void removeOffspring(Individual *ind);
    bool operator==(const Individual &);
    std::shared_ptr<MendellianInconsistencies> getInconsistencies();
    //    Helper functions
    void initPhase(int length = 0);
    void indivHomoFillIn();
    void indivParentHomozygoticFillIn();
    void makeIndividualPhaseCompliment();
    void makeIndividualGenotypeFromPhase();
    void randomlyPhasedMidPoint();
    string toString();
    Individual *getParentBasedOnIndex(int);
    void fillInhaplotypeBasedOnHaplotypeLibrary(const HaplotypeLibrary *hapLib, int hapIndex);
    Haplotype *getConsensus(vector<Haplotype *> &haplotypes, unsigned long nLoci, Haplotype *override = nullptr, int threshold = 2, int tolerance = 2);
};

class DummyIndividual : public Individual
{
  public:
    DummyIndividual()
    {
        id = NOPARENT;
        sireId = NOPARENT;
        damId = NOPARENT;
        recId = 0;
        founder = true;
    };
};

// Following is a way of printing out vectors
template <typename T>
ostream &operator<<(ostream &out, const vector<T> &v)
{
    out << "{";
    size_t last = v.size() - 1;
    for (size_t i = 0; i < v.size(); ++i)
    {
        out << v[i];
        if (i != last)
            out << ", ";
    }
    out << "}";
    return out;
}

// returns a new vector of a subset type
template <typename T>
vector<T> subsetVector(const vector<T> &in, const int &start, const int &end)
{
    auto first = in.begin() + start;
    auto last = in.begin() + end;
    vector<T> subset = vector<T>(first, last);
    return subset;
}

class Pedigree
{
  public:
    std::map<std::string, std::shared_ptr<Individual>> pedigree;
    std::vector<std::shared_ptr<Individual>> founders;
    std::vector<std::vector<Individual *>> generations;
    std::vector<Individual *> sortedVec;

    Pedigree();
    ~Pedigree();

    //        TODO write copy constructor
    explicit Pedigree(const std::string filePath);

    explicit Pedigree(const std::vector<std::vector<std::string>> &array);

    void sortPedigree();

    void checkOffspring(Individual *animal, std::map<std::string, bool> *seen, std::vector<std::vector<Individual *>> &generations, int currentGeneration);

    void addGenotypeInfoFromFile(std::string, bool initAll = false);
    void addPhaseInfoFromFile(std::string);

    std::vector<Individual *>::iterator begin();
    std::vector<Individual *>::iterator end();

    unsigned long getLength();

    Individual &operator[](const std::string &index);

    Individual &operator[](int index);

    void findMendelianInconsistencies(float threshold = 0.05, std::string filePath = "");
    void writeOutPhase(std::string filePath);
};

tuple<int, int, int> findConcensusHaplotypeChunks(Individual &ind, vector<vector<int>> haplotypes, int index, int nLoci);
}