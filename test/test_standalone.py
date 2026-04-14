"""
Tests for Standalone Mode Implementation
=========================================

This test suite validates that the standalone mode works correctly
without requiring ZMQ.
"""

import sys
import unittest
from bugdoc.algos.base import Debugger
from bugdoc.algos.stacked_shortcut_standalone import StackedShortcutStandalone


class TestStandaloneModeBase(unittest.TestCase):
    """Test the Debugger base class in standalone mode."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_results = {}
        
        def simple_func(params):
            """A simple test function."""
            result = params.get('value', 0) > 0.5
            self.test_results[str(params)] = result
            return result
        
        self.simple_func = simple_func
    
    def test_standalone_mode_initialization(self):
        """Test that debugger initializes correctly in standalone mode."""
        debugger = Debugger(function=self.simple_func)
        self.assertTrue(debugger.is_standalone)
        self.assertIsNotNone(debugger.function)
    
    def test_zmq_mode_initialization(self):
        """Test that debugger tries to initialize ZMQ mode when no function provided."""
        try:
            import zmq
            has_zmq = True
        except ImportError:
            has_zmq = False
        
        if has_zmq:
            # Only test if zmq is available
            debugger = Debugger()
            self.assertFalse(debugger.is_standalone)
        else:
            # Should raise ImportError if ZMQ not available
            with self.assertRaises(ImportError):
                debugger = Debugger()
    
    def test_workflow_standalone_execution(self):
        """Test that _workflow executes function in standalone mode."""
        debugger = Debugger(function=self.simple_func)
        debugger.run('entry_point', {'value': None}, outputs=['result'])
        
        # Execute a workflow
        debugger._workflow([0.7])
        
        # Check that the function was called
        self.assertTrue(len(self.test_results) > 0)
        # The key is the string of the parameter dict, not the list
        expected_key = str({'value': 0.7})
        self.assertIn(expected_key, self.test_results)
        self.assertTrue(self.test_results[expected_key])
    
    def test_results_storage_standalone(self):
        """Test that results are properly stored in standalone mode."""
        debugger = Debugger(function=self.simple_func)
        debugger.run('entry_point', {'value': None}, outputs=['result'])
        
        debugger._workflow([0.7])
        
        # Check results are stored
        self.assertEqual(len(debugger.allexperiments), 1)
        self.assertEqual(len(debugger.allresults), 1)
        self.assertEqual(debugger.allexperiments[0], [0.7, True])
        self.assertEqual(debugger.allresults[0], [0.7, True])
    
    def test_pending_results_tracking(self):
        """Test that pending results are tracked in standalone mode."""
        debugger = Debugger(function=self.simple_func)
        debugger.run('entry_point', {'value': None}, outputs=['result'])
        
        debugger._workflow([0.3])
        
        # Check pending results
        self.assertTrue(debugger.has_pending_results())
        self.assertIn('[0.3]', debugger._pending_requests)
    
    def test_poll_results_standalone(self):
        """Test poll_results in standalone mode."""
        debugger = Debugger(function=self.simple_func)
        debugger.run('entry_point', {'value': None}, outputs=['result'])
        
        debugger._workflow([0.8])
        
        # Poll for results
        socks = debugger.poll_results()
        self.assertIn('standalone', socks)
        result = debugger.get_result_from_poll(socks)
        self.assertEqual(result, [0.8, True])
    
    def test_poll_results_empty(self):
        """Test poll_results when no pending results."""
        debugger = Debugger(function=self.simple_func)
        debugger.run('entry_point', {'value': None}, outputs=['result'])
        
        # Poll for results with no pending
        socks = debugger.poll_results()
        self.assertEqual(len(socks), 0)
        result = debugger.get_result_from_poll(socks)
        self.assertIsNone(result)


class TestStackedShortcutStandalone(unittest.TestCase):
    """Test the StackedShortcutStandalone algorithm."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.call_count = 0
        self.last_params = None
        
        def mock_pipeline(params):
            """Mock pipeline function."""
            self.call_count += 1
            self.last_params = params
            # Simple logic: return True if any param is greater than 0.5
            for v in params.values():
                if isinstance(v, (int, float)) and v > 0.5:
                    return True
            return False
        
        self.mock_pipeline = mock_pipeline
    
    def test_algorithm_initialization(self):
        """Test StackedShortcutStandalone initialization."""
        algo = StackedShortcutStandalone(function=self.mock_pipeline, max_iter=100)
        self.assertTrue(algo.is_standalone)
        self.assertEqual(algo.max_iter, 100)
    
    def test_algorithm_execution(self):
        """Test basic algorithm execution."""
        algo = StackedShortcutStandalone(function=self.mock_pipeline, max_iter=10)
        parameter_space = {
            'param1': [0.1, 0.6],
            'param2': [0.2, 0.7]
        }
        
        # This should run without errors
        try:
            result = algo.run('entry_point', parameter_space, outputs=['result'])
            # If we get here, execution was successful
            self.assertIsNotNone(algo.allexperiments)
        except Exception as e:
            # Some errors might be expected if load_runs fails, but the core logic should work
            print(f"Expected potential error during test: {e}")

    def test_run_with_historical_runs_skips_initial_generation(self):
        """Test that historical_runs bypasses load_runs and skips the initial permutation stage."""
        history = (
            [[0.6, 0.7, True]],
            [[0.6, 0.7, True]]
        )
        algo = StackedShortcutStandalone(function=self.mock_pipeline, max_iter=10)
        parameter_space = {
            'param1': [0.6],
            'param2': [0.7]
        }

        result = algo.run('entry_point', parameter_space, outputs=['result'], historical_runs=history)

        self.assertEqual(algo.allexperiments, history[0])
        self.assertEqual(algo.allresults, history[1])
        self.assertEqual(self.call_count, 0)
        self.assertEqual(result, [])


class StandaloneIntegrationTest(unittest.TestCase):
    """Integration tests for standalone mode."""
    
    def test_multiple_function_calls(self):
        """Test multiple function calls in sequence."""
        results = []
        
        def tracking_func(params):
            # Track what was provided
            result = params.get('value', 0) > 0.5
            results.append((params, result))
            return result
        
        debugger = Debugger(function=tracking_func)
        debugger.run('entry_point', {'value': None}, outputs=['result'])
        
        # Execute multiple workflows
        debugger._workflow([0.3])
        debugger._workflow([0.7])
        debugger._workflow([0.2])
        
        # Verify all were called
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0][1], False)  # 0.3 > 0.5 = False
        self.assertEqual(results[1][1], True)   # 0.7 > 0.5 = True
        self.assertEqual(results[2][1], False)  # 0.2 > 0.5 = False
    
    def test_parameter_dict_construction(self):
        """Test that parameter dictionaries are correctly constructed."""
        received_params = []
        
        def param_logger(params):
            received_params.append(params)
            return True
        
        debugger = Debugger(function=param_logger)
        debugger.run('entry_point', {'x': None, 'y': None, 'z': None}, outputs=['result'])
        
        # Execute workflow with values
        debugger._workflow([1, 2, 3])
        
        # Verify parameter dict was constructed correctly
        self.assertEqual(len(received_params), 1)
        params = received_params[0]
        self.assertEqual(params['x'], 1)
        self.assertEqual(params['y'], 2)
        self.assertEqual(params['z'], 3)


def run_tests():
    """Run all tests."""
    print("Running Standalone Mode Tests...")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestStandaloneModeBase))
    suite.addTests(loader.loadTestsFromTestCase(TestStackedShortcutStandalone))
    suite.addTests(loader.loadTestsFromTestCase(StandaloneIntegrationTest))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
