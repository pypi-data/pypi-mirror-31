#include "alphahousepython.h"
#include <iostream>
using namespace alphahousepython;
#include <typeinfo>
#include <omp.h>
int main(int argc, char** argv)
{

    std::string test = "pedigree.txt";
    // std::unique_ptr<Pedigree> ped = std::unique_ptr<Pedigree>(new Pedigree(test));
    Pedigree* ped = new Pedigree(test);

    ped->addGenotypeInfoFromFile("genotypes.txt", true);

    printf("ped:%i", ped->getLength());
    ped->sortPedigree();


    for (auto const &x : ped->sortedVec)
    {

        // std::cout << x->id // string (key)
        //           << std::endl;

        x->indivHomoFillIn();
        x->indivParentHomozygoticFillIn();
    }


    std::vector<int> t(500, 0);
    
    #pragma omp parallel for
    for (int i=0; i< 500; i++ ) {
        t[i]++;
        #pragma omp critical
                {
                    std::cout << omp_get_thread_num() << "\n ";
                }
    }



   delete(ped);



     std::cout << "there" << '\n';
    // std::cout << "animOne:" <<  ped->pedigree["ccc"]->sireId << '\n';

}