#!/usr/bin/env python  
  
from distutils.core import setup, Extension  
import site

runtime_dirs = [i + "/pydat" for i in site.getsitepackages()]
# the c++ extension module
extension_mod = Extension("pydat.pydat", 
                        sources=['pydat/src/pydat.cpp', 'pydat/src/double_array_trie.cpp', 'pydat/src/utils.cpp'],
                        include_dirs=['pydat/src', 'pydat/include'],
                        library_dirs=['pydat/include/lib'],
                        runtime_library_dirs=runtime_dirs,
                        libraries=['boost_python'],
                        extra_compile_args=['-std=c++11'])

setup(name='pydat',
      version='0.2.9',
      keywords = ("Double Array Trie", "DAT"),  
      description = "DoubleArrayTrie(DAT) support prefix search & exact search & multiple pattern match for python implemented by c++",  
      long_description = "",  
      license = "MIT Licence",
      url = "https://github.com/yanwii/DoubleArrayTrie",  
      author = "yanwii",  
      author_email = "yanwii@outlook.com",
      package_dir={'':'pydat'},
      packages=['pydat'],
      include_package_data=True,
      package_data={"pydat":["libboost_python.so.1.66.0"]},
      ext_modules=[extension_mod]
)