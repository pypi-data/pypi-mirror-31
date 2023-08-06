#include "alphahousepython.h"

using namespace alphahousepython;

HaplotypeLibrary::HaplotypeLibrary(vector<Haplotype *> &haplotypes)
{

    this->haplotypes = haplotypes;
}

void HaplotypeLibrary::addHap(Haplotype *hap)
{
    haplotypes.push_back(hap);
}

std::vector<Haplotype *> HaplotypeLibrary::getMatching(Haplotype &hap)
{
    std::vector<Haplotype *> ret{};
    const int HAPLOTYPE_ERROR_THRESHOLD = 0;
    const int HAPLOTYPE_AGREEMENT_THRESHOLD = 1;
    for (Haplotype *hapLibHap : this->haplotypes)
    {

        auto compare = hap.compareHapsOnIntersect(hapLibHap);

        if (compare->matching > HAPLOTYPE_AGREEMENT_THRESHOLD && compare->nonMatching <= HAPLOTYPE_ERROR_THRESHOLD)
        {
            ret.push_back(hapLibHap);
        }
    }
    return ret;
}
