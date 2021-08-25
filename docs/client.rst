Client Example
==============
This example presents an executable software that combines several algorithms from `BugDoc`. It consists of a simple
command-line tool and requires a process that can receive pipeline configurations to be executed, such as the *worker*
script described `here <https://bugdoc.readthedocs.io/en/latest/auto_examples/index.html#example>`_.

Simple command-line interface
-----------------------------
This command-line tool can be found and installed from
the main `BugDoc` `repository <https://github.com/VIDA-NYU/BugDoc/tree/master/bugdoc_cli>`_.

usage: bugdoc-cli [-h] -f FILE [--budget BUDGET] [--send SEND]
                  [--receive RECEIVE] [--workers WORKERS]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  path to a configuration file describing the pipeline
  --budget BUDGET       maximum number of pipeline instances
  --send SEND           Socket port used to send messages to worker
  --receive RECEIVE     Socket port used to receive messages from worker
  --workers WORKERS     number of parallel workers to execute pipelines

