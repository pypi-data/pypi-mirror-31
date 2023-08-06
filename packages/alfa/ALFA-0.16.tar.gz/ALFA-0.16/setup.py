#!/usr/bin/env python

from distutils.core import setup

setup(name = 'ALFA',
      py_modules = ['ALFA'],
      version = '0.16',
      description = 'A simple software to get a quick overview of features composing NGS dataset(s).',
      author = 'Mathieu Bahin',
      author_email = 'mathieu.bahin@biologie.ens.fr',
      maintainer = 'Mathieu Bahin',
      maintainer_email = 'mathieu.bahin@biologie.ens.fr',
      url = 'https://github.com/biocompibens/ALFA',
      long_description = 'README',
      license = 'MIT',
      scripts = ['ALFA.py'],
      install_requires = [
        'pysam==0.13',
        'pybedtools==0.7.10'
        'progressbar==2.3']
)
