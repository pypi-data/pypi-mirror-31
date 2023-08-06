set_source_files_properties(
_faker.py
  PROPERTIES CYTHON_IS_CXX TRUE )
cython_add_module( _faker _faker.py)
cython_add_module( Constants Constants.py)