
include_directories(cpp_src )
include_directories(cpp_src/alphahousenative )
include_directories(${PYTHON_NUMPY_INCLUDE_DIR} )
# Process the CMakeLists.txt in the 'src' and 'bin' directory.
add_subdirectory( cpp_src )
add_subdirectory( src )