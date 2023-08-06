

#include <utility>
#include <memory>
#include "alphahousepython.h"

using namespace alphahousepython;

Individual::Individual(std::string id, std::string sireId, std::string damId, bool founder, int recId, enum gender gender, std::shared_ptr<Genotype> genotype, std::vector<std::shared_ptr<Haplotype>> haplotypes,
                       unsigned long initToSnps)
{
    this->id = std::move(id);
    this->sireId = std::move(sireId);
    this->damId = std::move(damId);
    this->founder = founder;
    this->recId = recId;
    this->gender = gender;
    this->genotype = nullptr;
    if (genotype)
    {
        this->genotype = genotype;
    }
    if (!haplotypes.empty())
    {

        this->haplotypes = std::vector<std::shared_ptr<Haplotype>>(haplotypes.size());
        for (int i = 0; i < haplotypes.size(); i++)
        {
            this->haplotypes[i] =haplotypes[i];
        }
    }

    if (initToSnps != 0)
    {
        std::vector<int> missing = std::vector<int>(initToSnps, MISSINGCODE);

        if (!haplotypes[0])
        {
            // Add 2 elements to haplotypes
            this->haplotypes[0] = std::shared_ptr<Haplotype>(new Haplotype(missing));
            this->haplotypes[1] = std::shared_ptr<Haplotype>(new Haplotype(missing));
        }
        // TODO what if init to snps is different length? need to add support to extend hap and genotypes
        if (!genotype)
        {
            this->genotype = std::shared_ptr<Genotype>(new Genotype(missing));
        }
    }
}

Individual::~Individual() {
    offsprings.clear();
    haplotypes.clear();

}

Individual *Individual::getParentBasedOnIndex(int index)
{

    if (index == 0)
    {
        return sire;
    }
    else if (index == 1)
    {
        return dam;
    }
    else return nullptr;
}

void Individual::makeIndividualPhaseCompliment()
{
    auto comp2 = genotype->complement(haplotypes[0].get());
    auto comp1 = genotype->complement(haplotypes[1].get());
    haplotypes[0]->setFromOtherIfMissing(comp1);
    haplotypes[1]->setFromOtherIfMissing(comp2);

    delete (comp1);
    delete (comp2);
}

void Individual::makeIndividualGenotypeFromPhase()
{

    if (haplotypes.size() > 0) {
        if (!genotype) {
            genotype = std::shared_ptr<Genotype>(new Genotype(haplotypes[0]->getLength()));
        }
        genotype->setFromHaplotypesIfMissing(haplotypes[0].get(), haplotypes[1].get());
    }
    else {
        throw new NoHaplotypeException();
    }
}

void Individual::initPhase(int length) {
    std::vector<int> ret;
     if (length != 0)
    {
        ret = std::vector<int>(length, MISSINGCODE);
        }
    else {
        ret = std::vector<int>(genotype->getLength(), MISSINGCODE);
    }

    if (haplotypes.size() == 0)
    {
        // create 2 haplotypes
        haplotypes.push_back(shared_ptr<Haplotype>(new Haplotype(ret)));
        haplotypes.push_back(shared_ptr<Haplotype>(new Haplotype(ret)));
    }
}

void Individual::indivParentHomozygoticFillIn()
{
    if (!this->founder)
    {

        for (int i = 0; i < 2; i++)
        {
            auto parent = this->getParentBasedOnIndex(i);

            auto tempG = new Genotype(parent->haplotypes[0].get(), parent->haplotypes[1].get());

            haplotypes[i]->setFromGenotypeIfMissing(tempG);

           delete (tempG);
        }

        makeIndividualGenotypeFromPhase();
    }
}

void Individual::randomlyPhasedMidPoint() 
{

    if (!genotype)
        throw new NoGenotypeException();
    if (haplotypes.size() == 0) {
        throw new NoHaplotypeException();
    }
    int mid = genotype->getLength() /2;
    int index = -1;

    int goal = (genotype->getLength() - mid) - 1;
    for (int i=0; i<goal; i++) {

        if (genotype->getGenotype(mid+i) == 1) {
            index = mid + i;
            break;
        }
        else if (genotype->getGenotype(mid-i) == 1){
            index = mid - i;
            break;
        }   
    }
    if (index != -1) 
    {
        haplotypes[0]->setPhase(index,0);
        haplotypes[1]->setPhase(index,1);
    }

}


void Individual::indivHomoFillIn()
{

    if (!genotype) throw new NoGenotypeException();
    std::vector<int> ret(genotype->getLength(), MISSINGCODE);
    if (haplotypes.size() == 0) {
        // create 2 haplotypes
        haplotypes.push_back(shared_ptr<Haplotype>(new Haplotype(ret)));
        haplotypes.push_back(shared_ptr<Haplotype>(new Haplotype(ret)));
    }
    for (int i = 0; i < genotype->getLength(); i++)
    {
        int value = genotype->getGenotype(i);
        if (value == 2)
        {
            for (auto hap : haplotypes)
            {
                hap->setPhase(i, 1);
            }
        }
        else if (value == 0)
        {
            for (auto hap : haplotypes)
            {
                hap->setPhase(i, 0);
            }
        }
    }
}


std::string Individual::toString() {

    std::string out;


    out = id + " " + sireId + " "  + " " + damId + '\n';

    return out;
}

void Individual::addOffspring(Individual *ind)
{
    offsprings.push_back(ind);

    if (ind->sireId == id)
    {
        ind->sire = this;
        gender = Male;
    }
    else if (ind->damId == id)
    {
        ind->dam = this;
        gender = Female;
    }
    else
    {
        throw new UnrelatedOffspringException();
    }
}

bool Individual::operator==(const Individual &other)
{

    if (id != other.id)
        return false;
    if (recId != other.recId)
        return false;
    if (sireId != other.damId)
        return false;

    return true;
}

void Individual::removeOffspring(Individual *ind)
{
    //    std::remove(offsprings.begin(), offsprings.end(), &ind);

    for (int i = 0; i < offsprings.size(); i++)
    {

        if (ind == offsprings[i])
        {
            offsprings.erase(offsprings.begin() + i);
        }
    }
    if (ind->sireId == id)
    {
        ind->sire = nullptr;
    }
    else if (ind->damId == id)
    {
        ind->dam = nullptr;
        gender = Female;
    }
    else
    {
        throw new UnrelatedOffspringException();
    }
}

std::shared_ptr<MendellianInconsistencies> Individual::getInconsistencies()
{

    std::shared_ptr<MendellianInconsistencies> inconsistencies;
    if (!genotype)
    {
        return inconsistencies;
    }

    if (sire && dam)
        inconsistencies = std::shared_ptr<MendellianInconsistencies>(new MendellianInconsistencies(genotype.get(), sire->genotype.get(), dam->genotype.get()));

    return inconsistencies;
}

Pedigree::Pedigree()
{
    pedigree = {};
    founders = {};
    generations = {};
}


Pedigree::~Pedigree()
{
    founders.clear();    
    pedigree.clear();
    generations.clear();
    sortedVec.clear();

}
Pedigree::Pedigree(std::string filePath)
{
    std::ifstream infile(filePath);
    if (infile.fail()) {
        std::cerr << "ERROR: file:" << filePath << " not found!";
    }
    std::string line;
    int count = 0;
    std::vector<std::vector<std::string>> arr{};
    while (std::getline(infile, line))
    {
        std::vector<std::string> tokens;
        boost::algorithm::split(tokens, line, boost::algorithm::is_any_of(" "), boost::token_compress_on);
        arr.push_back(tokens);
    }
    infile.close();
    *this = Pedigree(arr);
}

Pedigree::Pedigree(const std::vector<std::vector<std::string>>& array)
{

    std::vector<std::shared_ptr<Individual>> temp{};
    int count = 1;

    pedigree[NOPARENT] = std::shared_ptr<Individual>(new DummyIndividual());
    this->founders.push_back(pedigree[NOPARENT]);
    for (int i = 0; i < array.size(); i++)
    {
        bool founder = false;

        std::string id = array[i][0];
        std::string p1 = array[i][1];
        std::string p2 = array[i][2];
        if (p1 == NOPARENT && p2 == NOPARENT)
            founder = true;

        this->pedigree[id] = std::shared_ptr<Individual>(new Individual(id, p1, p2, founder, count));
        count++;
        if (founder)
        {
            this->founders.push_back(this->pedigree[id]);
        }
        // if bolth parents are in pedigree, then add the individual to both now 
        else if ((this->pedigree.count(p1) > 0) && (this->pedigree.count(p2) > 0))
        {
            this->pedigree[p1]->addOffspring(this->pedigree[id].get());
            this->pedigree[p2]->addOffspring(this->pedigree[id].get());
        }
        else
        {
            temp.push_back(this->pedigree[id]);
        }
    }

    for (std::shared_ptr<Individual> ind : temp)
    {
        if (pedigree.count(ind->sireId) > 0)
            pedigree[ind->sireId]->addOffspring(ind.get());

        else if (ind->sireId != NOPARENT)
        {
            pedigree[ind->sireId] = std::shared_ptr<Individual>(new Individual(ind->sireId, NOPARENT, NOPARENT, true, count));
            founders.push_back(pedigree[ind->sireId]);
            pedigree[ind->sireId]->addOffspring(ind.get());
            count++;
        }

        if (pedigree.count(ind->damId) > 0)
            pedigree[ind->damId]->addOffspring(ind.get());

        else if (ind->damId != NOPARENT)
        {
            pedigree[ind->damId] = std::shared_ptr<Individual>(new Individual(ind->damId, NOPARENT, NOPARENT, true, count));
            founders.push_back(pedigree[ind->damId]);
            pedigree[ind->damId]->addOffspring(ind.get());
            count++;
        }
    }
}

Individual &Pedigree::operator[](const std::string &index)
{
    return *(this->pedigree[index]);
}

Individual &Pedigree::operator[](int index)
{
    return *(this->sortedVec[index]);
}

void Pedigree::checkOffspring(Individual *animal, std::map<std::string, bool> *seen, std::vector<std::vector<Individual *>>& generations, int currentGeneration)
{
    (*seen)[animal->id] = true;

    int genSize = (generations.size() - 1);
    if (currentGeneration > genSize)
    {
        generations.push_back(std::vector<Individual *>{});
    }

    animal->generation = currentGeneration;

    std::vector<std::vector<Individual*>> &gen = generations;

    gen[currentGeneration].push_back(animal);

    for (const auto& off : animal->offsprings)
    {
        if (seen->count(off->sireId) > 0 && seen->count(off->damId) > 0)
        {
            int m = std::max(off->sire->generation, off->dam->generation);
            checkOffspring(off, seen, generations, m + 1);
        }
    }
}

void Pedigree::addGenotypeInfoFromFile(std::string filePath, bool initAll)
{
    std::ifstream infile(filePath);
    if (infile.fail()) {
        std::cerr << "ERROR: file:" << filePath << " not found!";
    }
    std::string line;
    std::vector<int> data;
    int c = 0;
    while (std::getline(infile, line))
    {
        std::vector<std::string> tokens;

        boost::algorithm::split(tokens, line, boost::algorithm::is_any_of(" "), boost::token_compress_on);

        std::transform(tokens.begin() + 1, tokens.end(), std::back_inserter(data),
                       [](const std::string &str) { return std::stoi(str); });

        if (c== 0) c = data.size();
        if (pedigree.count(tokens[0]) > 0)
        {
            pedigree[tokens[0]]->genotype = std::shared_ptr<Genotype>(new Genotype(data));
        }
        data.clear();
    }
    infile.close();

    // assume data is the same length
    if (initAll) {
        for (auto const &x : pedigree)
        {
            const auto ind = x.second;
            data.assign(c, 9);
            if (!ind->genotype)
            {                
                ind->genotype = std::shared_ptr<Genotype>(new Genotype(data));
            }
            ind->initPhase();
        }
    }
}

std::vector<Individual*>::iterator Pedigree::end()
{

    if (sortedVec.size() == 0)
        sortPedigree();
    return sortedVec.end();
}

std::vector<Individual*>::iterator Pedigree::begin()
{
    if (sortedVec.size() == 0)
        sortPedigree();
    return sortedVec.begin();
}
void Pedigree::addPhaseInfoFromFile(std::string filePath)
{
    std::ifstream infile(filePath);
    if (infile.fail()) {
        std::cerr << "ERROR: file:" << filePath << " not found!";
    }
    std::string line;
    int count = 0;
    std::vector<int> data;
    while (std::getline(infile, line))
    {
        std::vector<std::string> tokens;

        boost::algorithm::split(tokens, line, boost::algorithm::is_any_of(" "), boost::token_compress_on);

        std::transform(tokens.begin() + 1, tokens.end(), std::back_inserter(data),
                       [](const std::string &str) { return std::stoi(str); });

        if (pedigree.count(tokens[0]) > 0)
        {
            pedigree[tokens[0]]->haplotypes.push_back(std::shared_ptr<Haplotype>(new Haplotype(data)));
        }

        data.clear();
    }
    infile.close();
}

void Pedigree::writeOutPhase(std::string filePath)
{
    std::ofstream outFile(filePath);

    for (auto const &x : pedigree)
    {
        const auto ind = x.second;
        auto hap1Array = ind->haplotypes[0]->toIntArray();
        auto hap2Array = ind->haplotypes[1]->toIntArray();

        outFile << ind->id;
        for (int i = 0; i < hap1Array.size(); i++)
        {
            outFile << " " << hap1Array[i];
        }
        outFile << "\n";

        outFile << ind->id;
        for (int i = 0; i < hap2Array.size(); i++)
        {
            outFile << " " << hap2Array[i];
        }
        outFile << "\n";
    }

    outFile.close();
}

unsigned long Pedigree::getLength()
{
    return pedigree.size();
}

void Pedigree::sortPedigree()
{

    std::map<std::string, bool> seen{};

    int currentGeneration = 0;
    seen[NOPARENT] = true;
    if (generations.empty())
    {
        for (auto f : founders)
        {
            checkOffspring(f.get(), &seen, generations, currentGeneration);
        }
    }

    for (const auto& g : generations)
    {
        for (const auto &animal : g)
        {
            sortedVec.push_back(animal);
        }
    }
}

void Pedigree::findMendelianInconsistencies(float threshold, std::string filePath)
{

    if (sortedVec.size() == 0)
    {
        sortPedigree();
    }

    unsigned long long countChanges = 0;
    unsigned long long snpChanges = 0;

    std::map<std::string, std::vector<unsigned long long>> inconsistencies{};
    std::map<std::string, std::shared_ptr<MendellianInconsistencies>> mendObjects{};
    for (int i = 0; i < getLength(); i++)
    {

        auto ind = sortedVec[i];

        if (ind->founder)
            continue;

        mendObjects[ind->id] = ind->getInconsistencies();
        bool sireRemoved = false;
        bool damRemoved = false;
        unsigned long long sireIncon = mendObjects[ind->id]->paternalInconsistent.count();

        ind->sire->inconsistenciesCount += sireIncon;

        int damIncon = mendObjects[ind->id]->maternalInconsistent.count();
        ind->dam->inconsistenciesCount += damIncon;

        if ((float(sireIncon) / ind->genotype->getLength()) > threshold)
        {
            countChanges++;
            ind->sire->removeOffspring(ind);
            sireRemoved = true;
        }

        if ((float(damIncon) / ind->genotype->getLength()) > threshold)
        {
            countChanges++;
            ind->dam->removeOffspring(ind);
            damRemoved = true;
        }

        if (!sireRemoved)
        {

            for (int b = 0; b < (mendObjects[ind->id]->paternalInconsistent.size()); b++)
            {
                if (mendObjects[ind->id]->paternalInconsistent[b])
                    inconsistencies[ind->sire->id][b]++;
                if (mendObjects[ind->id]->paternalInconsistent[b])
                    inconsistencies[ind->sire->id][b]--;
            }
        }

        if (!damRemoved)
        {
            for (int b = 0; b < (mendObjects[ind->id]->paternalInconsistent.size()); b++)
            {
                if (mendObjects[ind->id]->maternalInconsistent[b])
                    inconsistencies[ind->dam->id][b]++;
                if (mendObjects[ind->id]->maternalConsistent[b])
                    inconsistencies[ind->dam->id][b]--;
            }
        }
    }

    for (int i = 0; i < getLength(); i++)
    {
        auto ind = sortedVec[i];
        if (ind->founder)
            continue;

        for (int b = 0; ind->genotype->getLength(); b++)
        {

            if (mendObjects[ind->id]->individualInconsistent[b])
            {
                snpChanges++;

                if (inconsistencies[ind->sire->id][b] > inconsistencies[ind->dam->id][b])
                {
                    ind->genotype->setGenotype(b, MISSINGCODE);
                    ind->sire->genotype->setGenotype(b, MISSINGCODE);
                }
                else if (inconsistencies[ind->sire->id][b] < inconsistencies[ind->dam->id][b])
                {
                    ind->genotype->setGenotype(b, MISSINGCODE);
                    ind->dam->genotype->setGenotype(b, MISSINGCODE);
                }
                else
                {
                    ind->genotype->setGenotype(b, MISSINGCODE);
                    ind->dam->genotype->setGenotype(b, MISSINGCODE);
                    ind->sire->genotype->setGenotype(b, MISSINGCODE);
                }
            }
        }
    }
}

MendellianInconsistencies::MendellianInconsistencies(Genotype *g, Genotype *pg, Genotype *mg)
{
    boost::dynamic_bitset<> indPres{};
    boost::dynamic_bitset<> matPres{};
    boost::dynamic_bitset<> patPres{};

    if (MEMORYSAVE)
    {
        auto het = (~(g->homo | g->additional)) & ((pg->homo & mg->homo) & (~pg->additional ^ mg->additional));
        maternalInconsistent = (het | ((g->homo & mg->homo) & (g->additional ^ mg->additional)));
        this->paternalInconsistent = (het | ((g->homo & pg->homo) & (g->additional ^ pg->additional)));

        patPres = pg->homo | ~pg->additional;
        matPres = mg->homo | ~mg->additional;
        indPres = g->homo | ~g->additional;
    }

    else
    {
        maternalInconsistent = boost::dynamic_bitset<>(g->getLength());
        paternalInconsistent = boost::dynamic_bitset<>(g->getLength());

        for (int i = 0; i < g->getLength(); i++)
        {
            indPres[i] = g->array[i] != MISSINGCODE ? true : false;
            patPres[i] = pg->array[i] != MISSINGCODE ? true : false;
            matPres[i] = mg->array[i] != MISSINGCODE ? true : false;

            if (g->array[i] == 1 && ((pg->array[i] == 0 && mg->array[i] == 2) || (pg->array[i] == 2 && mg->array[i] == 0)))
            {
                maternalInconsistent[i] = true;
                paternalInconsistent[i] = true;
                continue;
            }

            if ((g->array[i] == 0 && pg->array[i] == 2) || (g->array[i] == 2 && pg->array[i] == 0))
            {
                paternalInconsistent[i] = true;
            }

            if ((g->array[i] == 0 && mg->array[i] == 2) || (g->array[i] == 2 && mg->array[i] == 0))
            {
                maternalInconsistent[i] = true;
            }
        }
    }

    paternalConsistent = (indPres & patPres) & (~paternalInconsistent);
    maternalConsistent = (indPres & matPres) & (~maternalInconsistent);
    individualConsistent = (indPres & matPres & patPres) & ~individualInconsistent;
}
