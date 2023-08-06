# If the pyx file is a C++ file, we should specify that here.
set_source_files_properties(
gen.pyx hap.pyx PyIntersectCompare.pyx ped.pyx haplib.pyx
  PROPERTIES CYTHON_IS_CXX TRUE )

set(cythonPath ${CMAKE_CURRENT_LIST_DIR})
set(alphaHouseNativePath ${CMAKE_CURRENT_LIST_DIR}/alphahousenative/)
# Multi-file cython modules do not appear to be working at the moment.
include_directories(alphaHouseNativePath)

cython_add_module( gen gen.pyx ${alphaHouseNativePath}Genotype.cpp ${alphaHouseNativePath}Haplotype.cpp ${alphaHouseNativePath}IntersectCompare.cpp)

cython_add_module( hap hap.pyx ${alphaHouseNativePath}Haplotype.cpp ${alphaHouseNativePath}Genotype.cpp ${alphaHouseNativePath}IntersectCompare.cpp)

cython_add_module( ped ped.pyx ${alphaHouseNativePath}Pedigree.cpp ${alphaHouseNativePath}Genotype.cpp ${alphaHouseNativePath}Haplotype.cpp ${alphaHouseNativePath}Imputation.cpp ${alphaHouseNativePath}IntersectCompare.cpp )

cython_add_module( PyIntersectCompare PyIntersectCompare.pyx ${alphaHouseNativePath}IntersectCompare.cpp )
cython_add_module( haplib haplib.pyx ${alphaHouseNativePath}HaplotypeLibrary.cpp ${alphaHouseNativePath}Haplotype.cpp ${alphaHouseNativePath}IntersectCompare.cpp)
cython_add_module( Exceptions Exceptions.py)