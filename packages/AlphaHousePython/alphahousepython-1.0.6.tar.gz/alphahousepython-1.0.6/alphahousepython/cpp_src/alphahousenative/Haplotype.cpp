// #include "Python.h"

#include <iostream>

#include "alphahousepython.h"

using namespace alphahousepython;

Haplotype::Haplotype(std::vector<int> arrayIn, int start, int weight)
{

    if (MEMORYSAVE)
    {
        int size = arrayIn.size();
        phase = boost::dynamic_bitset<>(size);
        missing = boost::dynamic_bitset<>(size);

        for (int i = 0; i < size; i++)
        {
            setPhase(i, arrayIn[i]);
        }
    }

    else
    {
        array = arrayIn;
    }

    this->start = start;
    this->weight = weight;
    // std::bitset< =
}

Haplotype::Haplotype(unsigned long size, unsigned int value, int start, int weight)
{

    if (MEMORYSAVE)
    {
        phase = boost::dynamic_bitset<>(size);
        missing = boost::dynamic_bitset<>(size);
        for (int i = 0; i < size; i++)
        {
            setPhase(i, value);
        }
    }
    else
    {
        array = std::vector<int>(size, value);
    }

    this->start = start;
    this->weight = weight;
}

Haplotype::Haplotype(boost::dynamic_bitset<> phaseIn, boost::dynamic_bitset<> missingIn, int start, int weight)
{

    this->start = start;
    this->weight = weight;
    if (MEMORYSAVE)
    {
        phase = phaseIn;
        missing = missingIn;
    }
    else
    {
        array = std::vector<int>(phaseIn.size());

        for (int i = 0; i < phaseIn.size(); i++)
        {
            bool hom = phaseIn[i];
            bool miss = missingIn[i];
            if (hom && miss)
                array[i] = ERRORCODE;
            else if (hom)
                array[i] = 1;
            else if (miss)
                array[i] = MISSINGCODE;
            else
                array[i] = 0;
        }
    }
}
Haplotype::~Haplotype()
{
    array.clear();
    phase.clear();
    missing.clear();
}

void Haplotype::setFromOtherIfMissing(Haplotype *other)
{

    if (MEMORYSAVE)
    {
        phase = ((~missing & phase) | (missing & other->phase));
        missing = (missing & other->missing);
    }
    else
    {

        if (other->getLength() != getLength())
            throw new DifferentLengthException();
        for (int i = 0; i < getLength(); i++)
        {
            if (array[i] == MISSINGCODE)
            {
                array[i] = other->array[i];
            }
        }
    }
}

void Haplotype::setFromGenotypeIfMissing(Genotype *other)
{

    if (MEMORYSAVE)
    {
        phase = ((~missing & phase) | (missing & (other->homo & other->additional)));
        missing = ~other->homo & missing;
    }

    else
    {
        if (other->getLength() != getLength())
            throw new DifferentLengthException();
        for (int i = 0; i < getLength(); i++)
        {
            if (array[i] == MISSINGCODE)
            {
                if (other->array[i] == 2)
                    array[i] = 1;
                else if (other->array[i] == 0)
                    array[i] = 0;
            }
        }
    }
}

std::vector<int> Haplotype::toIntArray()
{
    if (MEMORYSAVE)
    {
        std::vector<int> ret(getLength(), MISSINGCODE);
        for (int i = 0; i < getLength(); i++)
        {
            bool hom = phase[i];
            bool add = missing[i];

            if (hom && add)
                ret[i] = ERRORCODE;
            else if (hom)
                ret[i] = 1;
            else if (add)
                ret[i] = MISSINGCODE;
            else
                ret[i] = 0;
        }
        return ret;
    }

    else
        return array;
}

int Haplotype::getLength()
{

    if (MEMORYSAVE)
        return phase.size();
    else
        return array.size();
}

std::string Haplotype::toString()
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

void Haplotype::setPhase(int pos, int value)
{

    if (pos > getLength() - 1)
    {
        throw new OutOfRangeException();
    }

    if (MEMORYSAVE)
    {

        
        bool miss;
        bool ph;
        switch (value)
        {
        case 0:
            ph = false;
            miss = false;
            break;
        case 1:
            ph = true;
            miss = false;
            break;
        case MISSINGCODE:
            ph = false;
            miss = true;
            break;
        default:
            ph = true;
            miss = true;
            break;
        }
        phase[pos] = ph;
        missing[pos] = miss;
    }
    else
    {
        array[pos] = value;
    }
}

int Haplotype::getPhase(int pos)
{

    if (pos > missing.size()) {
        throw new OutOfRangeException();
    }
    if (MEMORYSAVE)
    {
        bool miss = missing[pos];
        bool ph = phase[pos];
        if (miss && ph)
        {
            return ERRORCODE;
        }
        else if (miss)
        {
            return MISSINGCODE;
        }
        else if (ph)
        {
            return 1;
        }
        else
        {
            return 0;
        }
    }
    else
    {
        return array[pos];
    }
}


int Haplotype::getPhaseWithGlobalIndex(int globalIndex) {
    return getPhase(globalIndex - start);
}

int Haplotype::countMissing()
{
    if (MEMORYSAVE)
    {
        return (~phase & missing).count();
    }
    else
    {
        return std::count(array.begin(), array.end(), 9);
    }
}

int Haplotype::countNotMissing()
{
    return getLength() - countMissing();
}

int Haplotype::countNotEqualExcludeMissing(Haplotype *other)
{
    if (MEMORYSAVE)
    {
        return (((phase ^ other->phase) | (missing ^ other->missing)) & ((~missing) & (~other->missing))).count();
    }

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

float Haplotype::percentageMissing()
{
    return countMissing() / getLength();
}

bool Haplotype::checkEqual(Haplotype *other)
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
        if (phase != other->phase || missing != other->missing)
        {
            return false;
        }
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



Haplotype *Haplotype::getSubsetHaplotype(int startIn, int end)
{
    if (startIn > getLength()){
        throw new OutOfRangeException();
    }
    if (MEMORYSAVE)
    {
        boost::dynamic_bitset<> mask(phase.size());
        mask.set();
        mask = mask << startIn;
        boost::dynamic_bitset<> phaseSub(phase.size());
        phaseSub = (phase & mask) >> startIn;
        phaseSub.resize((end - startIn));

        boost::dynamic_bitset<> missingSub(missing.size());
        missingSub = (missing & mask) >> startIn;
        missingSub.resize((end - startIn));

        return new Haplotype(phaseSub, missingSub, startIn + start);
    }
    else
    {
        std::vector<int>::const_iterator first = array.begin() + startIn;
        std::vector<int>::const_iterator last = array.begin() + end;
        std::vector<int> tempVec(first, last);
        return new Haplotype(tempVec, startIn + start);
    }
}

Haplotype *Haplotype::getSubsetHaplotypeGlobal(int globStart, int globEnd) {
    return getSubsetHaplotype(globStart - start, globEnd - start);
}
bool Haplotype::containsIndex(int index)
{
    return (index >= start && index < (start + getLength()));
}
// TODO write iterator

IntersectCompare *Haplotype::compareHapsOnIntersect(Haplotype *otherHap)
{

    int startHere = std::max(start, otherHap->start);
    int end = std::min(getLength() + start, otherHap->getLength() + otherHap->start);

    int nonMissing = 0;
    int matching = 0;

    if (MEMORYSAVE)
    {
        Haplotype *h1 = this->getSubsetHaplotypeGlobal(startHere, end);
        Haplotype *h2 = otherHap->getSubsetHaplotypeGlobal(startHere, end);
        if (h1->getLength() == 0 || h2->getLength() == 0)
            return new IntersectCompare(0, 0, 0, 0);
        nonMissing = (~h1->missing & ~h2->missing).count(); // counts true bits in resulting array
        matching = ((~h1->missing & ~h2->missing) & ((h1->phase & h2->phase) ^ ((~h1->phase & ~h2->phase)))).count();
        delete(h1);
        delete(h2);
    }
    else
    {
        for (int i = startHere; i < end; i++)
        {
            int ind1 = i - start;
            int ind2 = i - otherHap->start;

            if (array[ind1] != MISSINGCODE && otherHap->array[ind2] != MISSINGCODE)
            {
                nonMissing++;

                if (otherHap->array[ind2] == array[ind1])
                {
                    matching++;
                }
            }
        }
    }

    int nonMatching = nonMissing - matching;
    return new IntersectCompare(matching, end - startHere, nonMissing, nonMatching);
}

