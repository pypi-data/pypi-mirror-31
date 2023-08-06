
#include <iostream>
#include "alphahousepython.h"

using namespace alphahousepython;

Genotype::Genotype(std::vector<int> arrayIn, int startIn)
{
    start = startIn;

    if (MEMORYSAVE)
    {
        int size = arrayIn.size();
        homo = boost::dynamic_bitset<>(size);
        additional = boost::dynamic_bitset<>(size);
        for (int i = 0; i < size; i++)
        {
            setGenotype(i, arrayIn[i]);
        }
    }
    else
        array = arrayIn;
}

Genotype::~Genotype() {
    array.clear();
    homo.clear();
    additional.clear();
}

Genotype::Genotype(boost::dynamic_bitset<> homoIn, boost::dynamic_bitset<> addIn, int startIn)
{
    start = startIn;

    if (MEMORYSAVE)
    {
        homo = homoIn;
        additional = addIn;
    }

    else
    {
        array = std::vector<int>(homoIn.size());

        for (int i = 0; i < homoIn.size(); i++)
        {
            bool hom = homoIn[i];
            bool add = addIn[i];

            if (hom && add)
                array[i] = 2;
            else if (hom)
                array[i] = 0;
            else if (add)
                array[i] = 9;
            else
                array[i] = 1;
        }
    }
}

Genotype::Genotype(Haplotype *h1, Haplotype *h2, int startIn)
{
    start = startIn;
    int h1Length = h1->getLength();

    if (h1Length != h2->getLength())
    {
        throw new DifferentLengthException();
    }

    if (MEMORYSAVE)
    {
        homo = (((~h1->phase & ~h1->missing) & (~h2->phase & ~h2->missing)) | ((h1->phase & ~h1->missing) & (h2->phase & ~h2->missing)));
        additional = (((h1->phase & ~h1->missing) & (h2->phase & ~h2->missing)) | (h1->missing | h2->missing));
    }
    else
    {
        array = std::vector<int>(h1Length);

        for (int i = 0; i < h1Length; i++)
        {
            int h1v = h1->array[i];
            int h2v = h2->array[i];
            if (h1v == 1 && h2v == 1)
                array[i] = 2;
            else if (h1v == 0 && h2v == 0)
                array[i] = 0;
            else if (h1v == MISSINGCODE || h2v == MISSINGCODE)
                array[i] = MISSINGCODE;
            else
                array[i] = 1;
        }
    }
}

std::string Genotype::toString()
{

    if (MEMORYSAVE)
    {
        array = toIntArray();
    }
    std::vector<int>::const_iterator it;
    std::stringstream s;
    for (it = array.begin(); it != array.end(); ++it)
    {
        if (it != array.begin())
            s << " ";

        s << *it;
    }
    if (MEMORYSAVE)
    {
        // clears memory of vector
        std::vector<int>().swap(array);
    }
    return s.str().c_str();
}

bool Genotype::isHaplotypeCompatible(Haplotype *hap, int threshold = 0)
{
    int x = 0;

    if (MEMORYSAVE)
    {
        x = (((homo & ~additional) & (hap->phase & ~hap->missing)) | ((homo & additional) & (~hap->phase & ~hap->missing))).count();
    }
    else
    {
        for (int i = 0; i < getLength(); i++)
        {
            if (array[i] == 0)
            {
                if (hap->array[i] != 0 || hap->array[i] == MISSINGCODE)
                {
                    x++;
                }
            }
            else if (array[i] == 2)
            {
                if (hap->array[i] != 1 || hap->array[i] == MISSINGCODE)
                {
                    x++;
                }
            }
        }
    }
    return x <= threshold;
}

int Genotype::getLength()
{
    if (MEMORYSAVE)
        return homo.size();
    else
        return array.size();
}

void Genotype::setGenotype(int pos, int value)
{
    if (pos > getLength() - 1)
        throw new OutOfRangeException();

    if (MEMORYSAVE)
    {
        switch (value)
        {
        case (0):
            homo[pos] = true;
            additional[pos] = false;
            break;
        case (1):
            homo[pos] = false;
            additional[pos] = false;
            break;
        case (2):
            homo[pos] = true;
            additional[pos] = true;
            break;
        default:
            homo[pos] = false;
            additional[pos] = true;
        }
    }

    else
        array[pos] = value;
}

int Genotype::getGenotype(int pos)
{
    if (pos > getLength() - 1) {
        throw new OutOfRangeException();
    }

    if (MEMORYSAVE)
    {
        bool hom = homo[pos];
        bool add = additional[pos];

        if (hom && add)
            return 2;
        else if (hom)
            return 0;
        else if (add)
            return MISSINGCODE;
        else
            return 1;
    }
    else
        return array[pos];
}

std::vector<int> Genotype::toIntArray()
{
    if (MEMORYSAVE)
    {

        std::vector<int> ret(getLength(), MISSINGCODE);
        for (int i = 0; i < getLength(); i++)
        {
            bool hom = homo[i];
            bool add = additional[i];

            if (hom && add)
                ret[i] = 2;
            else if (hom)
                ret[i] = 0;
            else if (add)
                ret[i] = MISSINGCODE;
            else
                ret[i] = 1;
        }
        return ret;
    }
    else
        return array;
}

int Genotype::countMissing()
{
    if (MEMORYSAVE)
        return (~homo & additional).count();
    else
        return std::count(array.begin(), array.end(), 9);
}

int Genotype::numHet()
{
    if (MEMORYSAVE)
        return (~homo & ~additional).count();
    else
        return std::count(array.begin(), array.end(), 1);
}

int Genotype::countNotMissing()
{
    return getLength() - countMissing();
}

int Genotype::countNotEqual(Genotype *other)
{

    if (MEMORYSAVE)
    {
        return ((homo ^ other->homo) | (additional ^ other->additional)).count();
    }
    else
    {

        if (getLength() != other->getLength())
        {
            throw new DifferentLengthException();
        }
        int count = 0;
        for (int i = 0; i < getLength(); i++)
        {
            if (array[i] != other->array[i])
                count++;
        }

        return count;
    }
}
int Genotype::countNotEqualExcludeMissing(Genotype *other)
{

    if (MEMORYSAVE)
        return (((homo ^ other->homo) | (additional ^ other->additional)) & ((homo | ~additional) & (other->homo | ~other->additional))).count();
    else
    {

        if (getLength() != other->getLength())
        {
            throw new DifferentLengthException;
        }
        int count = 0;
        for (int i = 0; i < getLength(); i++)
        {

            int g1 = array[i];
            int g2 = other->array[i];
            if (g1 != g2 && (g1 != MISSINGCODE && g2 != MISSINGCODE))
                count++;
        }

        return count;
    }
}

float Genotype::percentageMissing()
{
    return countMissing() / getLength();
}

bool Genotype::checkEqual(Genotype *other)
{
    if (start != other->start)
    {
        return false;
    }

    if (getLength() != other->getLength())
    {
        return false;
    }

    if (MEMORYSAVE)
    {
        if (homo != other->homo || additional != other->additional)
            return false;
    }

    else
    {
        for (int i = 0; i < getLength(); i++)
        {

            if (array[i] != other->array[i])
                return false;
        }
    }

    return true;
}

int Genotype::getEnd()
{
    return (getLength() + start) - 1;
}

Genotype *Genotype::getSubsetGenotype(int startIn, int end)
{

    if (MEMORYSAVE)
    {
        boost::dynamic_bitset<> mask(homo.size());
        mask.set();
        mask = mask << startIn;

        boost::dynamic_bitset<> homoSub(homo.size());
        homoSub = (homo & mask) >> startIn;

        homoSub.resize((end - startIn));

        boost::dynamic_bitset<> addSub(additional.size());
        addSub = (additional & mask) >> startIn;

        addSub.resize((end - startIn));

        return new Genotype(homoSub, addSub, startIn + start);
    }
    else
    {
        std::vector<int>::const_iterator first = array.begin() + startIn;
        std::vector<int>::const_iterator last = array.begin() + end;
        std::vector<int> tempVec(first, last);
        return new Genotype(tempVec, startIn + start);
    }
}

bool Genotype::containsIndex(int index)
{
    return (index >= start && index < getEnd());
}

int Genotype::countMismatches(Genotype *other)
{

    if (other->getLength() != getLength())
        throw new DifferentLengthException();

    if (MEMORYSAVE)
    {
        return ((homo & other->homo) & (additional ^ other->additional)).count();
    }

    else
    {
        int count = 0;
        for (int i = 0; i < getLength(); i++)
        {
            if (array[i] == 0 && other->array[i] == 2)
                count++;

            if (array[i] == 2 && other->array[i] == 0)
                count++;
        }
        return count;
    }
}

void Genotype::setFromOtherIfMissing(Genotype *other)
{

    if (other->getLength() != getLength())
        throw new DifferentLengthException();

    if (MEMORYSAVE)
    {
        boost::dynamic_bitset<> origHom = homo;
        homo = (((homo | ~additional) & homo) | ((~homo & additional) & other->homo));
        additional = (((origHom | ~additional) & additional) | ((~origHom & additional) & other->additional));
    }

    else
    {
        for (int i = 0; i < getLength(); i++)
        {
            if (array[i] == MISSINGCODE)
            {
                array[i] = other->array[i];
            }
        }
    }
}

void Genotype::setFromHaplotypesIfMissing(alphahousepython::Haplotype * h1, alphahousepython::Haplotype * h2) {
    auto temp = new Genotype(h1, h2);

    setFromOtherIfMissing(temp);

    delete(temp);

}

Haplotype *Genotype::complement(Haplotype *hap)
{
    if (MEMORYSAVE)
    {
        boost::dynamic_bitset<> tempPhase = ((hap->phase & hap->missing) | (((hap->phase & ~hap->missing) & homo) | (~(hap->phase | hap->missing) & ~(homo ^ additional))));
        boost::dynamic_bitset<> tempMissing = (hap->missing | (additional & ~homo) | ((~hap->phase & additional) & hap->phase & (homo ^ additional)));
        return new Haplotype(tempPhase, tempMissing);
    }

    else
    {

        std::vector<int> temp(getLength());

        for (int i = 0; i < getLength(); i++)
        {
            if (array[i] == 0)
            {
                temp[i] = 0;
            }
            else if (array[i] == 2)
            {
                temp[i] = 1;
            }
            else if (array[i] == 1)
            {
                if (hap->array[i] == 1)
                {
                    temp[i] = 0;
                }
                else if (hap->array[i] == 0)
                {
                    temp[i] = 1;
                }
                else
                {
                    temp[i] = 9;
                }
            }
            else
            {
                temp[i] = MISSINGCODE;
            }
        }

        return new Haplotype(temp);
    }
}

bool Genotype::isMissing(int pos)
{
    if (array[pos] == MISSINGCODE)
        return true;

    return false;
}

Genotype::Genotype(unsigned long size, unsigned int value) {
    // Empty Genotype 
    if (MEMORYSAVE) {
        homo = boost::dynamic_bitset<>(size);
        additional = boost::dynamic_bitset<>(size);
        for (int i = 0; i < size; i++)
        {
            setGenotype(i, value);
        }

    }
    else {
        array = std::vector<int>(size,value);
    }


}


