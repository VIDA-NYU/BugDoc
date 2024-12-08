"""
Debugger script
===========================

This script defines the pipeline entry point, the parameter-space,
 and invokes one of BugDoc's algorithm to debug the pipeline.
"""


# %%
# Importing algorithm from BugDoc's API
# --------------------------------------
# We choose the Stacked Shortcut Algorithm to debug the pipeline.

from bugdoc.algos.stacked_shortcut import StackedShortcut

# %%
# Parameter space definition
# ---------------------------
# The parameter-values that BugDoc tries can be retrieved in two ways:
# From previous executions of the pipeline or specifying the all possible values each parameter can take.
# In the following, we provide the entry point of the pipeline and a dictionary with the parameter names as keys
# and a list of parameter-values as the corresponding value.


filename = 'dataflow_pipeline.json'
parameter_space = {
    'operator1_script': [
        '/data/scripts/operator1/script1.py',
        '/data/scripts/operator1/script2.py',
        '/data/scripts/operator1/script3.py',
        '/data/scripts/operator1/script4.py',
        '/data/scripts/operator1/script5.py',
        '/data/scripts/operator1/script6.py',
        '/data/scripts/operator1/script7.py',
        '/data/scripts/operator1/script8.py',
        '/data/scripts/operator1/script9.py',
    ],
    'read_path': [
        '/tmp/inputs_20200527.csv',
        '/tmp/inputs_20200528.csv',
        '/tmp/inputs_20200529.csv',
        '/tmp/inputs_20200530.csv',
        '/tmp/inputs_20200531.csv',
    ],
    'read_mode': ['once', 'repeat'],
    'write_mode': ['append', 'concat', 'replace'],
    'operator2_script': [
        '/data/scripts/operator2/aggregation.py',
        '/data/scripts/operator2/average.py',
        '/data/scripts/operator2/reduce.py',
    ],
    'threshold': [0.1, 0.5],
    'folds': [2, 5, 10]
}


# %%
# Pipeline Debugging
# ------------------------
# We initialize the Stacked Shortcut Algorithm object and run it passing the pipeline entry point and
# the parameter space. The Algorithm will generate new pipeline instances and exchange messages with the *Worker*
# script to execute and evaluate the instances. This process will be blocked if no *Worker* is running.

debugger = StackedShortcut()
result = debugger.run(filename, parameter_space)

# %%
# Revealing the root cause
# -------------------------
# When the algorithm finishes we can display the root cause of error.

root, _, _ = result
parameters = list(parameter_space.keys())
print('Root Cause: \n%s' % (
    ' OR '.join(
     [
        ' AND '.join(
         [parameters[pair[0]]+' = '+pair[1] for pair in r]
                    )
        for r in root])))
