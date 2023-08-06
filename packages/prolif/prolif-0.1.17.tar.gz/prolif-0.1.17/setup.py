from setuptools import setup
from os import path
from codecs import open

here = path.abspath(path.dirname(__file__))

# get version from version.py
__version__ = None
exec(open('prolif/version.py').read())

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='prolif',
      version=__version__,
      description='Protein-Ligand Interaction Fingerprints',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/cbouy/ProLIF',
      author='Cédric Bouysset',
      author_email='bouysset.cedric@gmail.com',
      license='Apache License, Version 2.0',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Chemistry',
      ],
      keywords='science chemistry biology drug-design chemoinformatics virtual-screening',
      packages=['prolif'],
      entry_points = {
        'console_scripts': ['prolif=prolif.command_line:cli'],
        },
      install_requires=['numpy>=1.13.3'],
      dependency_links=['git+https://github.com/rdkit/rdkit'],
      test_suite="prolif.tests",
      include_package_data=True,
      zip_safe=False)
