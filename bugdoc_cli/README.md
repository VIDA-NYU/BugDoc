# Simple command-line interface for BugDoc

This script is an executable software that combines several algorithms from `BugDoc`. It consists of a simple
command-line tool and requires a process that can receive pipeline configurations to be executed, such as the *worker*
script described [here](https://bugdoc.readthedocs.io/en/latest/auto_examples/index.html#example).

## Installation

    $ pip install -e .

## Commands

```
usage: bugdoc-cli [-h] [--file FILE] [--budget BUDGET] [--params PARAMS]
                  [--output OUTPUT]

optional arguments:
  -h, --help       show this help message and exit
  --file FILE      path to pipeline entry point
  --budget BUDGET  maximum number of pipeline instances
  --params PARAMS  path to json with parameters and values to be investigated
  --output OUTPUT  path to file where results will written to
```