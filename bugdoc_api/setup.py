import io
import os
from setuptools import setup

import sys


# pip workaround
os.chdir(os.path.abspath(os.path.dirname(__file__)))

packages = []
for rootdir, dirs, files in os.walk('bugdoc'):
    if '__init__.py' in files:
        packages.append(rootdir.replace('\\', '.').replace('/', '.'))




req = ['pytest-cov',
       'pylint',
       'future',
       'numpy',
       'zmq',
       'certifi>=2017.4.17',
       'Pillow',
       'image',
       'nose==1.3.7',
       'Django == 1.11.28']


setup(name='bugdoc',
      version='0.1',
      packages=packages,
      install_requires=req,
      description="BugDoc library",
      author="Raoni Lourenco",
      author_email='raoni@nyu.edu',
      maintainer='Raoni Lourenco',
      maintainer_email='raoni@nyu.edu',
      keywords=['Scientific Workflows',
                'Provenance', 
                'Heuristic Algorithms', 
                'Debugging', 
                'Combinatorial Design', 
                'Parameter Exploration'])

