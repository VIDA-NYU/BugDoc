import os
from setuptools import setup



# pip workaround
os.chdir(os.path.abspath(os.path.dirname(__file__)))

packages = []




req = ['bugdoc']


setup(name='bugdoc-cli',
      version='0.1',
      packages=packages,
      entry_points={
          'console_scripts': [
              'bugdoc-cli = main:run']
      },
      install_requires=req,
      description="BugDoc Command Line Interface",
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