# Simple command-line interface for BugDoc

This script is an executable software that combines several algorithms from `BugDoc`. It consists of a simple
command-line tool and requires a process that can receive pipeline configurations to be executed, such as the *worker*
script described [here](https://bugdoc.readthedocs.io/en/latest/auto_examples/index.html#example).

## Installation

    $ pip install -e .

## Commands

```
usage: bugdoc-cli [-h] -f FILE [--budget BUDGET] [--send SEND]
                  [--receive RECEIVE] [--workers WORKERS]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  path to a configuration file describing the pipeline
  --budget BUDGET       maximum number of pipeline instances
  --send SEND           Socket port used to send messages to worker
  --receive RECEIVE     Socket port used to receive messages from worker
  --workers WORKERS     number of parallel workers to execute pipelines
```

## Configuration file

BugDoc requires a ```JSON``` file with the following fields:
- An entry point to the pipeline: ```entry_point```.
- The python module containing the function to run the pipeline: ```python_module```.
- The function to run a pipeline instance: ```run```.
- A list of parameters, each one consisting of a name and a list of values: ```parameters```.
    - The name of the parameter: ```name```.
    - The values that each parameter can take: ```values```.

For example, ```my_pipeline_conf.json```:
```
{
  "entry_point": "my_pipeline",
  "python_module": "my_api_example",
  "run": "execute_pipeline",
  "parameters": [
    {
      "name": "p1",
      "values": [
        "p1v1",
        "p1v2",
        "p1v3"
        ]
    },
    {
      "name": "p2",
      "values": [1, 2, 3]
    },
    {
      "name": "p3",
      "values": [1.0, 2.0, 3.0]
    },
  ]
  }
```