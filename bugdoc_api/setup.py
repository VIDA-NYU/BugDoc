import os

from setuptools import find_packages, setup

os.chdir(os.path.abspath(os.path.dirname(__file__)))

packages = find_packages()

install_requires = [
    "future",
    "numpy",
    "pyzmq",
    "certifi>=2023.0",
    "Pillow>=9.0",
    "Django>=4.2.30",
]

setup(
    name="bugdoc",
    version="0.2.0",
    packages=packages,
    install_requires=install_requires,
    python_requires=">=3.8.1",
    description="BugDoc library",
    author="Raoni Lourenco",
    author_email="raoni@nyu.edu",
    maintainer="Raoni Lourenco",
    maintainer_email="raoni@nyu.edu",
    url="https://github.com/VIDA-NYU/BugDoc",
    keywords=[
        "Scientific Workflows",
        "Provenance",
        "Heuristic Algorithms",
        "Debugging",
        "Combinatorial Design",
        "Parameter Exploration",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    extras_require={
        "docs": [
            "sphinx>=6.0",
            "sphinx_rtd_theme>=1.0",
            "sphinx-gallery>=0.13",
            "nbsphinx>=0.9",
            "nbsphinx-link>=1.3",
            "ipykernel>=6.0"
            ],
        "dev": [
            "black[jupyter]>=23.0",
            "flake8>=6.0",
            "ruff>=0.1",
            "mypy>=1.0",
            "isort>=5.12",
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "pytest-xdist>=3.0",
            "pytest-timeout>=2.1",
            "coverage[toml]>=7.0",
            "bandit[toml]>=1.7",
            "pre-commit>=3.0"
            ]
    }
)
