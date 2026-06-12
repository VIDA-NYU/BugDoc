"""
Standalone Debugger Example
===========================

This example demonstrates how to use BugDoc's algorithms in standalone mode
without requiring ZMQ or an external worker process.

In standalone mode, you pass a Python function directly to the algorithm
that takes a parameter dictionary and returns a result.
"""

from bugdoc.algos.stacked_shortcut_standalone import StackedShortcutStandalone


# Example 1: Simple pipeline function
def my_pipeline(params):
    """
    A simple pipeline function that takes parameter values and returns a boolean result.
    
    Parameters
    ----------
    params: dict
        Dictionary with parameter names as keys and their values.
        
    Returns
    -------
    bool
        True if the pipeline execution was successful, False otherwise.
    """
    # Extract parameters
    mode = params.get('mode', 'default')
    value = params.get('value', 0)
    threshold = params.get('threshold', 0.5)
    
    # Run some logic
    result = value > threshold if mode == 'compare' else value > 0
    
    print(f"Pipeline executed with params: {params}, result: {result}")
    return result


# Example 2: Using with the StackedShortcut algorithm in standalone mode
def main():
    # Define the parameter space
    parameter_space = {
        'mode': ['compare', 'default', 'other'],
        'value': [0.1, 0.5, 0.9],
        'threshold': [0.3, 0.7]
    }
    
    # Create the debugger in standalone mode by passing the function
    debugger = StackedShortcutStandalone(max_iter=50, function=my_pipeline)
    
    # Run the debugger with the entry point (not used in standalone mode but required by API)
    result = debugger.run('pipeline_function', parameter_space)
    
    print(f"\nDebugger completed. Results:\n{result}")


if __name__ == '__main__':
    main()
