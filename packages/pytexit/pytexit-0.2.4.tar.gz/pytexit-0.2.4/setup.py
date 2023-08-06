from __future__ import absolute_import
from setuptools import setup, find_packages
import os
import codecs
from os.path import join, dirname

long_description = 'Convert a Python expression in a LaTeX formula'
if os.path.exists('README.rst'):
    long_description = codecs.open('README.rst', encoding="utf-8").read()

# Read version number from file
with open(join(dirname(__file__),'pytexit', '__version__.txt')) as version_file:
    __version__ = version_file.read().strip()
    
setup(name='pytexit',
      version=__version__,
      description='Convert a Python expression in a LaTeX formula',
      long_description=long_description,
      url='https://github.com/erwanp/pytexit',
      author='Erwan Pannier',
      author_email='erwan.pannier@gmail.com',
      license='CeCILL-2.1',
      packages=find_packages(),
      platforms="any",
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: CEA CNRS Inria Logiciel Libre License, version 2.1 (CeCILL-2.1)',
        'Topic :: Scientific/Engineering',
        'Topic :: Text Processing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        "Operating System :: OS Independent"],
      install_requires=[
                 'six',  # python 2-3 compatibility],
                 ],
      scripts=[
          'scripts/py2tex'],
      include_package_data=True,
      zip_safe=False)
