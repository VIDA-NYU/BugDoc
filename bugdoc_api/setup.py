import os
from setuptools import setup, find_packages

os.chdir(os.path.abspath(os.path.dirname(__file__)))

packages = find_packages()

install_requires = [
    'future',
    'numpy',
    'pyzmq',
    'certifi>=2023.0',
    'Pillow>=9.0',
    'Django>=4.2.17',
]

setup(
    name='bugdoc',
    version='0.2.0',
    packages=packages,
    install_requires=install_requires,
    python_requires='>=3.8',
    description="BugDoc library",
    author="Raoni Lourenco",
    author_email='raoni@nyu.edu',
    maintainer='Raoni Lourenco',
    maintainer_email='raoni@nyu.edu',
    url='https://github.com/VIDA-NYU/BugDoc',
    keywords=[
        'Scientific Workflows',
        'Provenance',
        'Heuristic Algorithms',
        'Debugging',
        'Combinatorial Design',
        'Parameter Exploration'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)

