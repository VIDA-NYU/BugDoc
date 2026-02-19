# Standalone Mode for BugDoc Algorithms

## Overview

The standalone mode allows you to use BugDoc's debugging algorithms without requiring ZMQ (ZeroMQ) or an external worker process. Instead, you pass a Python function directly to the algorithm, and the algorithm executes it in-process for each test case.

## Key Benefits

- **No External Dependencies**: No need to run a separate worker process
- **No ZMQ Requirement**: Eliminates the ZMQ dependency for standalone usage
- **Simpler Setup**: Direct function execution makes testing and integration easier
- **Direct Integration**: Can be embedded directly in Python applications

## How It Works

### Traditional ZMQ Mode

```
Algorithm → [sends message via ZMQ] → External Worker Process → Result
                                      [receives result via ZMQ]
```

### Standalone Mode

```
Algorithm → [directly calls function] → Result
```

## Usage

### Basic Usage

```python
from bugdoc.algos.stacked_shortcut_standalone import StackedShortcutStandalone

# Define your pipeline function
def my_pipeline(params):
    """
    Your pipeline function.
    
    Parameters
    ----------
    params: dict
        Dictionary with parameter names as keys and their values.
        
    Returns
    -------
    bool
        True if successful, False if failed.
    """
    # Extract parameters
    param1 = params['param1']
    param2 = params['param2']
    
    # Run your pipeline logic
    result = your_function(param1, param2)
    
    return result


# Create the debugger in standalone mode
debugger = StackedShortcutStandalone(
    max_iter=1000,
    function=my_pipeline  # Pass your function here
)

# Run the debugger
parameter_space = {
    'param1': [value1, value2, value3],
    'param2': [valueA, valueB, valueC]
}

result = debugger.run('entry_point', parameter_space)
```

### Comparison: ZMQ Mode vs Standalone Mode

#### ZMQ Mode (Traditional)

```python
from bugdoc.algos.stacked_shortcut import StackedShortcut

# ZMQ mode requires an external worker process
# Start the worker in another terminal:
# python bugdoc_cli_worker.py --file conf.json

debugger = StackedShortcut()  # No function parameter
result = debugger.run('pipeline_config.json', parameter_space)
```

#### Standalone Mode (New)

```python
from bugdoc.algos.stacked_shortcut_standalone import StackedShortcutStandalone

# No external worker needed
def pipeline_function(params):
    # Your implementation
    return result

debugger = StackedShortcutStandalone(function=pipeline_function)
result = debugger.run('entry_point', parameter_space)
```

## Available Algorithms in Standalone Mode

Currently, the following algorithm is available in standalone mode:

- `StackedShortcutStandalone`: Standalone version of the StackedShortcut algorithm

More algorithms will be converted to support standalone mode in future updates.

## Creating a Standalone Algorithm

To create a standalone version of an algorithm:

1. Extend the `Debugger` base class with the `function` parameter support
2. Override the `run()` method to handle parameter space exploration
3. Use `self._workflow()` to execute the function (it automatically handles both modes)
4. Use `self.poll_results()` and `self.get_result_from_poll()` for result collection

Example:

```python
from bugdoc.algos.base import Debugger

class MyAlgorithmStandalone(Debugger):
    
    def run(self, entry_point, input_dict, outputs=['results']):
        super().run(entry_point, input_dict, outputs=outputs)
        
        # Your algorithm logic here
        for exp in experiments:
            self._workflow(exp)  # Works in both modes!
            
            # Collect results using mode-agnostic methods
            socks = self.poll_results()
            result = self.get_result_from_poll(socks)
```

## Implementation Notes

### Mode Detection

The `Debugger` base class automatically detects which mode to use:
- If `function` parameter is provided: **Standalone mode**
- If `function` parameter is None: **ZMQ mode** (requires ZMQ to be installed)

### Result Storage

Both modes store results in the same format for compatibility:
- `self.allexperiments`: List of experiment parameters and results
- `self.allresults`: List of experiment results

### Polling

Use the provided helper methods instead of directly accessing ZMQ:
- `poll_results(timeout)`: Mode-agnostic polling
- `get_result_from_poll(socks)`: Mode-agnostic result extraction
- `has_pending_results()`: Check for pending results (standalone mode)

## Performance Considerations

- **Standalone mode** has lower overhead since there's no IPC (inter-process communication)
- **ZMQ mode** may be better for distributed scenarios or long-running worker processes
- **Standalone mode** executes functions sequentially, while ZMQ mode can have worker parallelization

## Troubleshooting

### ImportError: ZMQ is required for non-standalone mode

**Solution**: Either:
1. Install ZMQ: `pip install zmq`
2. Use standalone mode by passing a `function` parameter

### Results not being collected

Make sure you:
1. Pass a valid callable function to the algorithm
2. Use `self._workflow()` instead of `self._workflow_zmq()` or `self._workflow_standalone()`
3. Use mode-agnostic polling methods (`poll_results()` and `get_result_from_poll()`)

## Migration Guide

If you want to convert existing code from ZMQ mode to standalone mode:

1. Create a function that encapsulates your pipeline logic
2. Replace algorithm import: `StackedShortcut` → `StackedShortcutStandalone`
3. Add the `function` parameter: `debugger = StackedShortcutStandalone(function=my_func)`
4. Everything else remains the same!

## Future Work

- Convert all remaining algorithms to support standalone mode
- Add async/await support for standalone mode
- Add support for multiprocessing in standalone mode
- Performance optimizations for large parameter spaces
