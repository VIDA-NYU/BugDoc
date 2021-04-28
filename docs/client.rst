Client Example
==============
This example presents an executable software that combines several algorithms from `BugDoc`. It consists of a simple
command-line tool and requires a process that can receive pipeline configurations to be executed, such as the *worker*
script described `here <https://bugdoc.readthedocs.io/en/latest/auto_examples/index.html#example>`_.

Simple command-line interface
-----------------------------
This command-line tool can be found and installed from
the main `BugDoc` `repository <https://github.com/VIDA-NYU/BugDoc/tree/master/bugdoc_cli>`_.

usage: bugdoc-cli [-h] [--file FILE] [--budget BUDGET] [--params PARAMS]
                  [--output OUTPUT]

optional arguments:
  -h, --help       show this help message and exit
  --file FILE      path to pipeline entry point
  --budget BUDGET  maximum number of pipeline instances
  --params PARAMS  path to json with parameters and values to be investigated
  --output OUTPUT  path to file where results will written to

