
#include <omp.h>
#include "alphahousepython.h"
using namespace alphahousepython;

void alignPhaseAndGenotypes(Individual &ind)
{
    ind.indivHomoFillIn();
    ind.makeIndividualPhaseCompliment();
    ind.makeIndividualGenotypeFromPhase();
}

// void ferdosi(Individual &ind, int nLoci)
// {

//     if (ind.offsprings.size() < 4)
//         return;

//     vector<vector<int>> subIndHaplotypes;
//     vector<vector<int>> haplotypes;
//     int hap = 0;

//     //TODO need to create subIndHaplotypes
//     for (auto &child : ind.offsprings)
//     {
//         if (*(child->sire) == ind)
//             hap = 0;
//         else if (*(child->dam) == ind)
//             hap = 1;

//         haplotypes.push_back(child->haplotypes[hap]->toIntArray());
//     }

//     typedef map<int, std::tuple<int, int>> consensusType;
//     consensusType consensus;

//      if (subIndHaplotypes.size() < 0) return;

//     for (int i=0; i<subIndHaplotypes; i++) {
//         consensus[i] = subIndHaplotypes
//     }

//     // TODO finish ferdosi
// }

tuple<int, int, int> *findConcensusHaplotypeChunks(Individual &ind, vector<vector<int>> haplotypes, int index, int nLoci)
{

    int start = index - int((nLoci - 1) / 2);
    int end = index + int((nLoci / 2) + 1);

    if (haplotypes.size() == 0)
        return nullptr;
    if (start < 0 || end > haplotypes[0].size())
        return nullptr;

    typedef map<int, std::tuple<int, int>> refType;

    refType reference;

    int numHaps = 0;
    tuple<int, int> maxValues;

    for (auto &hap : haplotypes)
    {

        vector<int>::const_iterator first = hap.begin() + start;
        vector<int>::const_iterator last = hap.begin() + end;

        vector<int> subset = subsetVector(hap, start, end);

        // if ((hap.begin() + start) == 1) subset = 1 - subset
        // TODO Needs finished
    }
}

Haplotype *Individual::getConsensus(vector<Haplotype *> &haplotypes, unsigned long nLoci, Haplotype *overwriteHap, int threshold, int tolerance)
{

    Haplotype *consensus = new Haplotype(nLoci);

    #pragma omp parallel for
    for (int i = 0; i < nLoci; i++)
    {
        int count = 0;
        int ones = 0;

        for (const auto &hap : haplotypes)
        {
            if (hap->containsIndex(i))
            {
                if (hap->getPhase(i - hap->start) != MISSINGCODE) {
                    count++;
                    ones += hap->getPhase(i - hap->start);
                }
            }
        }
        int zeros = count - ones;
        if (ones >= threshold && zeros <= tolerance)
            consensus->setPhase(i,1);
        if (zeros >= threshold && ones <= tolerance)
             consensus->setPhase(i,0);

        if (overwriteHap)
        {
            int tempPhase = overwriteHap->getPhase(i);
            if (tempPhase != MISSINGCODE)
            {
                consensus->setPhase(i, tempPhase);
            }
        }
    }
    return consensus;
}

void Individual::fillInhaplotypeBasedOnHaplotypeLibrary(const HaplotypeLibrary *hapLib, int hapIndex)
{

    shared_ptr<Haplotype> curHap = this->haplotypes[hapIndex];
    const int HAPLOTYPE_AGREEMENT_THRESHOLD = 1;
    const int HAPLOTYPE_ERROR_THRESHOLD = 0;
    const int LOCI_AGREEMENT_THRESHOLD = 1;
    const int LOCI_ERROR_THRESHOLD = 10;

    vector<std::array<char, 2>> arr(curHap->getLength(),{0});

    #pragma omp parallel for
    for (int i = 0; i< hapLib->haplotypes.size(); i++)
    {
        auto h = hapLib->haplotypes[i];
        auto ret = curHap->compareHapsOnIntersect(h);

        int hapStart = h->start;
        int hapEnd = hapStart + h->getLength();

        if (ret->matching > HAPLOTYPE_AGREEMENT_THRESHOLD && ret->nonMatching <= HAPLOTYPE_ERROR_THRESHOLD)
        {

            for (int i = hapStart; i < hapEnd; i++)
            {
                int v = h->getPhase(i - hapStart);

                if (v != MISSINGCODE)
                {
                    arr[i][v] += h->weight;
                }
            }
        }
    }


    #pragma omp parallel for
    for (int i = 0; i < arr.size(); i++)
    {

        if (arr[i][0] > arr[i][1] && arr[i][0] >= LOCI_AGREEMENT_THRESHOLD && arr[i][1] <= LOCI_ERROR_THRESHOLD)
        {

            if (curHap->getPhase(i) == MISSINGCODE)
            {
                curHap->setPhase(i, 0);
            }
        }

        else if (arr[i][1] > arr[i][0] && arr[i][1] >= LOCI_AGREEMENT_THRESHOLD and arr[i][0] <= LOCI_ERROR_THRESHOLD)
        {

            if (curHap->getPhase(i) == MISSINGCODE)
            {
                curHap->setPhase(i, 1);
            }
        }
    }
}

// TODO followinh code could potentially be faster - but currentlyg slower
// void Individual::fillInhaplotypeBasedOnHaplotypeLibrary(const HaplotypeLibrary *hapLib, int hapIndex)
// {

//     shared_ptr<Haplotype> curHap = this->haplotypes[hapIndex];
//     const int HAPLOTYPE_AGREEMENT_THRESHOLD = 1;
//     const int HAPLOTYPE_ERROR_THRESHOLD = 0;
//     const int LOCI_AGREEMENT_THRESHOLD = 1;
//     const int LOCI_ERROR_THRESHOLD = 10;

//     Haplotype *tempHap = new Haplotype(curHap->getLength());

//     for (int hapIter = 0; hapIter < hapLib->haplotypes.size(); hapIter++)
//     {

//         Haplotype *h = hapLib->haplotypes[hapIter];
//         auto ret = curHap->compareHapsOnIntersect(h);

//         int hapStart = h->start;
//         int hapEnd = hapStart + h->getLength();

//         if (ret->matching > HAPLOTYPE_AGREEMENT_THRESHOLD && ret->nonMatching <= HAPLOTYPE_ERROR_THRESHOLD)
//         {

//             int end = std::min(hapEnd, tempHap->getLength()); 
            
//             for (int i = hapStart; i < hapEnd; i++)
//             {
//                 int phaseVal = h->getPhase(i - hapStart);
//                 if (phaseVal != MISSINGCODE)
//                     if (tempHap->getPhase(i) == MISSINGCODE)
//                         tempHap->setPhase(i, phaseVal);
//                     else if (tempHap->getPhase(i) != phaseVal)
//                         tempHap->setPhase(i, ERRORCODE);
//             }
//         }
//     }

//     curHap->setFromOtherIfMissing(tempHap);
//     delete(tempHap);
// }