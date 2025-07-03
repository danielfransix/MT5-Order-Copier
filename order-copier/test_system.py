#!/usr/bin/env python3
# MT5 Pending Order Copier System - Test Script
# This script tests system components and validates configuration

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import tempfile
import json

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config import load_config, validate_config
    from utils import (
        setup_logging, calculate_lot_size, validate_lot_size,
        format_price, is_valid_order_type, safe_float_compare,
        create_order_summary, format_error_message
    )
    from mt5_connector import MT5Connector
    from order_tracker import OrderTracker
    from order_manager import OrderManager
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all required modules are available")
    sys.exit(1)

class TestUtils(unittest.TestCase):
    """Test utility functions"""
    
    def test_calculate_lot_size(self):
        """Test lot size calculation"""
        # Basic calculation
        self.assertEqual(calculate_lot_size(1.0, 1.0, 0.01, 100.0), 1.0)
        self.assertEqual(calculate_lot_size(1.0, 0.5, 0.01, 100.0), 0.5)
        self.assertEqual(calculate_lot_size(2.0, 1.5, 0.01, 100.0), 3.0)
        
        # Min/max constraints
        self.assertEqual(calculate_lot_size(0.005, 1.0, 0.01, 100.0), 0.01)  # Below min
        self.assertEqual(calculate_lot_size(200.0, 1.0, 0.01, 100.0), 100.0)  # Above max
        
        # Edge cases
        self.assertEqual(calculate_lot_size(0.0, 1.0, 0.01, 100.0), 0.01)  # Zero source
        self.assertEqual(calculate_lot_size(1.0, 0.0, 0.01, 100.0), 0.01)  # Zero multiplier
    
    def test_validate_lot_size(self):
        """Test lot size validation"""
        self.assertTrue(validate_lot_size(1.0, 0.01, 100.0))
        self.assertTrue(validate_lot_size(0.01, 0.01, 100.0))  # Min boundary
        self.assertTrue(validate_lot_size(100.0, 0.01, 100.0))  # Max boundary
        
        self.assertFalse(validate_lot_size(0.005, 0.01, 100.0))  # Below min
        self.assertFalse(validate_lot_size(200.0, 0.01, 100.0))  # Above max
        self.assertFalse(validate_lot_size(-1.0, 0.01, 100.0))  # Negative
    
    def test_format_price(self):
        """Test price formatting"""
        self.assertEqual(format_price(1.23456, 2), 1.23)
        self.assertEqual(format_price(1.23456, 4), 1.2346)
        self.assertEqual(format_price(1.23456, 5), 1.23456)
        self.assertEqual(format_price(1.0, 2), 1.0)
    
    def test_is_valid_order_type(self):
        """Test order type validation"""
        allowed_types = ['BUY_LIMIT', 'SELL_LIMIT', 'BUY_STOP', 'SELL_STOP']
        
        self.assertTrue(is_valid_order_type('BUY_LIMIT', allowed_types))
        self.assertTrue(is_valid_order_type('SELL_STOP', allowed_types))
        self.assertFalse(is_valid_order_type('BUY_STOP_LIMIT', allowed_types))
        self.assertFalse(is_valid_order_type('INVALID_TYPE', allowed_types))
        
        # Empty allowed types should reject all
        self.assertFalse(is_valid_order_type('BUY_LIMIT', []))
        self.assertFalse(is_valid_order_type('ANY_TYPE', []))
    
    def test_safe_float_compare(self):
        """Test safe floating point comparison"""
        self.assertTrue(safe_float_compare(1.0, 1.0, 1e-5))
        self.assertTrue(safe_float_compare(1.00001, 1.00002, 1e-4))
        self.assertFalse(safe_float_compare(1.0, 1.1, 1e-5))
        self.assertTrue(safe_float_compare(0.0, 0.0, 1e-5))
    
    def test_create_order_summary(self):
        """Test order summary creation"""
        order = {
            'ticket': 123456,
            'symbol': 'EURUSD',
            'type_name': 'BUY_LIMIT',
            'volume_initial': 1.0,
            'price_open': 1.1234,
            'sl': 1.1200,
            'tp': 1.1300
        }
        
        summary = create_order_summary(order)
        self.assertIn('123456', summary)
        self.assertIn('EURUSD', summary)
        self.assertIn('BUY_LIMIT', summary)
        self.assertIn('1.0', summary)
    
    def test_format_error_message(self):
        """Test error message formatting"""
        try:
            raise ValueError("Test error")
        except Exception as e:
            msg = format_error_message(e)
            self.assertIn('Test error', msg)
            
            # Test with context
            msg_with_context = format_error_message(e, "Context")
            self.assertIn('Context:', msg_with_context)
            self.assertIn('Test error', msg_with_context)

class TestOrderTracker(unittest.TestCase):
    """Test order tracking functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, 'test_state.json')
        self.tracker = OrderTracker(state_file=self.state_file)
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.state_file):
            os.remove(self.state_file)
        os.rmdir(self.temp_dir)
    
    def test_update_source_orders(self):
        """Test source order updates"""
        orders = [
            {
                'ticket': 123, 'symbol': 'EURUSD', 'volume_initial': 1.0, 'type_name': 'BUY',
                'price_open': 1.1234, 'sl': 1.1200, 'tp': 1.1300, 'time_setup': 1640995200, 'time_expiration': 0
            },
            {
                'ticket': 456, 'symbol': 'GBPUSD', 'volume_initial': 0.5, 'type_name': 'SELL',
                'price_open': 1.3456, 'sl': 1.3500, 'tp': 1.3400, 'time_setup': 1640995300, 'time_expiration': 0
            }
        ]
        
        self.tracker.update_source_orders(orders)
        self.assertEqual(len(self.tracker.state['source_orders']), 2)
        self.assertIn('123', self.tracker.state['source_orders'])
        self.assertIn('456', self.tracker.state['source_orders'])
    
    def test_update_target_orders(self):
        """Test target order updates"""
        orders = [
            {
                'ticket': 789, 'magic': 123, 'symbol': 'EURUSD', 'type_name': 'BUY',
                'volume_initial': 1.0, 'price_open': 1.1234, 'sl': 1.1200, 'tp': 1.1300,
                'time_setup': 1640995200, 'time_expiration': 0
            },
            {
                'ticket': 101, 'magic': 456, 'symbol': 'GBPUSD', 'type_name': 'SELL',
                'volume_initial': 0.5, 'price_open': 1.3456, 'sl': 1.3500, 'tp': 1.3400,
                'time_setup': 1640995300, 'time_expiration': 0
            }
        ]
        
        self.tracker.update_target_orders('Terminal1', orders)
        self.assertIn('Terminal1', self.tracker.state['target_orders'])
        self.assertEqual(len(self.tracker.state['target_orders']['Terminal1']), 2)
    
    def test_detect_orphaned_orders(self):
        """Test orphaned order detection"""
        # Set up source orders
        source_orders = [{
            'ticket': 123, 'symbol': 'EURUSD', 'type_name': 'BUY',
            'volume_initial': 1.0, 'price_open': 1.1234, 'sl': 1.1200, 'tp': 1.1300,
            'time_setup': 1640995200, 'time_expiration': 0
        }]
        self.tracker.update_source_orders(source_orders)
        
        # Set up target orders with one orphan
        target_orders = [
            {  # Valid
                'ticket': 789, 'magic': 123, 'symbol': 'EURUSD', 'type_name': 'BUY',
                'volume_initial': 1.0, 'price_open': 1.1234, 'sl': 1.1200, 'tp': 1.1300,
                'time_setup': 1640995200, 'time_expiration': 0
            },
            {  # Orphan
                'ticket': 101, 'magic': 999, 'symbol': 'GBPUSD', 'type_name': 'SELL',
                'volume_initial': 0.5, 'price_open': 1.3456, 'sl': 1.3500, 'tp': 1.3400,
                'time_setup': 1640995300, 'time_expiration': 0
            }
        ]
        self.tracker.update_target_orders('Terminal1', target_orders)
        
        orphans = self.tracker.detect_orphaned_orders('Terminal1')
        self.assertEqual(len(orphans), 1)
        self.assertEqual(orphans[0]['ticket'], 101)
    
    def test_orphan_check_management(self):
        """Test orphan check counter management"""
        terminal = 'Terminal1'
        ticket = 123
        
        # Test increment
        count1 = self.tracker.increment_orphan_check(terminal, ticket)
        self.assertEqual(count1, 1)
        
        count2 = self.tracker.increment_orphan_check(terminal, ticket)
        self.assertEqual(count2, 2)
        
        # Test should kill logic
        self.assertFalse(self.tracker.should_kill_orphan(terminal, ticket, 3))
        
        count3 = self.tracker.increment_orphan_check(terminal, ticket)
        self.assertTrue(self.tracker.should_kill_orphan(terminal, ticket, 3))
        
        # Test reset
        self.tracker.reset_orphan_check(terminal, ticket)
        self.assertFalse(self.tracker.should_kill_orphan(terminal, ticket, 3))
    
    def test_state_persistence(self):
        """Test state save and load"""
        # Set up some state
        source_orders = [{
            'ticket': 123, 'symbol': 'EURUSD', 'type_name': 'BUY',
            'volume_initial': 1.0, 'price_open': 1.1234, 'sl': 1.1200, 'tp': 1.1300,
            'time_setup': 1640995200, 'time_expiration': 0
        }]
        target_orders = [{
            'ticket': 789, 'magic': 123, 'symbol': 'EURUSD', 'type_name': 'BUY',
            'volume_initial': 1.0, 'price_open': 1.1234, 'sl': 1.1200, 'tp': 1.1300,
            'time_setup': 1640995200, 'time_expiration': 0
        }]
        
        self.tracker.update_source_orders(source_orders)
        self.tracker.update_target_orders('Terminal1', target_orders)
        self.tracker.increment_orphan_check('Terminal1', 999)
        
        # Save state
        self.assertTrue(self.tracker.save_state())
        self.assertTrue(os.path.exists(self.state_file))
        
        # Create new tracker and load state
        new_tracker = OrderTracker(state_file=self.state_file)
        self.assertTrue(new_tracker.load_state())
        
        # Verify state was loaded
        self.assertEqual(len(new_tracker.state['source_orders']), 1)
        self.assertIn('Terminal1', new_tracker.state['target_orders'])
        self.assertIn('Terminal1', new_tracker.state['orphan_checks'])

class TestConfiguration(unittest.TestCase):
    """Test configuration loading and validation"""
    
    def test_sample_config_structure(self):
        """Test that sample config has required structure"""
        # Try to load sample config
        sample_config_path = 'config_sample.py'
        if os.path.exists(sample_config_path):
            config = load_config(sample_config_path)
            self.assertIsNotNone(config)
            
            # Check required sections
            self.assertIn('SOURCE_TERMINAL', config)
            self.assertIn('TARGET_TERMINALS', config)
            self.assertIn('ENABLE_SCHEDULING', config)
            self.assertIn('ENABLE_CONTINUOUS_MODE', config)
            self.assertIn('LOGGING_CONFIG', config)
            
            # Validate structure
            is_valid, errors = validate_config(config)
            if not is_valid:
                print("Sample config validation errors:")
                for error in errors:
                    print(f"  - {error}")
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Valid minimal config
        valid_config = {
            'SOURCE_TERMINAL': {
                'MT5_ACCOUNT': 123456,
                'MT5_PASSWORD': 'test',
                'MT5_SERVER': 'test-server',
                'MT5_TERMINAL_PATH': r'C:\test\path.exe',
                'timeout': 10000
            },
            'TARGET_TERMINALS': {
                'Test1': {
                    'MT5_ACCOUNT': 654321,
                    'MT5_PASSWORD': 'test',
                    'MT5_SERVER': 'test-server',
                    'MT5_TERMINAL_PATH': r'C:\test\path.exe',
                    'timeout': 10000,
                    'lot_multiplier': 1.0,
                    'min_lot_size': 0.01,
                    'max_lot_size': 100.0,
                    'allowed_order_types': ['BUY_LIMIT'],
                    'symbol_mapping': {},
                    'orphan_management': {
                        'kill_orphaned_orders': True,
                        'max_orphan_checks': 3
                    }
                }
            },
            'ENABLE_SCHEDULING': False,
            'ENABLE_CONTINUOUS_MODE': True,
            'SCHEDULE_TIMEFRAME': 'M5',
            'SCHEDULE_OFFSET_SECONDS': 60,
            'CONTINUOUS_DELAY_SECONDS': 5,
            'CONTINUOUS_MAX_RUNTIME_HOURS': 0,
            'LOGGING_CONFIG': {
                'level': 'INFO',
                'console_output': True
            }
        }
        
        is_valid, errors = validate_config(valid_config)
        self.assertTrue(is_valid, f"Valid config failed validation: {errors}")
        
        # Invalid config - missing source terminal
        invalid_config = valid_config.copy()
        del invalid_config['SOURCE_TERMINAL']
        
        is_valid, errors = validate_config(invalid_config)
        self.assertFalse(is_valid)
        self.assertTrue(any('Source terminal' in error for error in errors))

class TestMT5Connector(unittest.TestCase):
    """Test MT5 connector functionality (mocked)"""
    
    def setUp(self):
        """Set up test environment"""
        self.connector = MT5Connector()
    
    @patch('mt5_connector.mt5')
    def test_connection_success(self, mock_mt5):
        """Test successful MT5 connection"""
        mock_mt5.initialize.return_value = True
        mock_mt5.login.return_value = True
        
        terminal_config = {
            'MT5_ACCOUNT': 123456,
            'MT5_PASSWORD': 'test',
            'MT5_SERVER': 'test-server',
            'MT5_TERMINAL_PATH': r'C:\test\path.exe',
            'timeout': 10000
        }
        
        result = self.connector.connect(terminal_config, 'Test')
        self.assertTrue(result)
        
        mock_mt5.initialize.assert_called_once()
        mock_mt5.login.assert_called_once_with(123456, 'test', 'test-server')
    
    @patch('mt5_connector.mt5')
    def test_connection_failure(self, mock_mt5):
        """Test MT5 connection failure"""
        mock_mt5.initialize.return_value = False
        mock_mt5.last_error.return_value = (1, 'Test error')
        
        terminal_config = {
            'MT5_ACCOUNT': 123456,
            'MT5_PASSWORD': 'test',
            'MT5_SERVER': 'test-server',
            'MT5_TERMINAL_PATH': r'C:\test\path.exe',
            'timeout': 10000
        }
        
        result = self.connector.connect(terminal_config, 'Test')
        self.assertFalse(result)
    
    @patch('mt5_connector.mt5')
    def test_get_pending_orders(self, mock_mt5):
        """Test getting pending orders"""
        # Set connector as connected for test
        self.connector.is_connected = True
        
        # Mock order data
        mock_orders = [
            Mock(
                ticket=123456,
                symbol='EURUSD',
                type=2,  # BUY_LIMIT
                volume_initial=1.0,
                price_open=1.1234,
                sl=1.1200,
                tp=1.1300,
                magic=0,
                comment='Test order',
                time_setup=1640995200,
                time_expiration=0
            )
        ]
        
        mock_mt5.orders_get.return_value = mock_orders
        
        orders = self.connector.get_pending_orders()
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0]['ticket'], 123456)
        self.assertEqual(orders[0]['symbol'], 'EURUSD')
        self.assertEqual(orders[0]['type_name'], 'BUY_LIMIT')

class TestSystemIntegration(unittest.TestCase):
    """Test system integration"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create minimal test config
        self.test_config = {
            'SOURCE_TERMINAL': {
                'login': 123456,
                'password': 'test',
                'server': 'test-server',
                'path': r'C:\test\path.exe',
                'timeout': 10000
            },
            'TARGET_TERMINALS': {
                'Test1': {
                    'login': 654321,
                    'password': 'test',
                    'server': 'test-server',
                    'path': r'C:\test\path.exe',
                    'timeout': 10000,
                    'lot_multiplier': 1.0,
                    'min_lot_size': 0.01,
                    'max_lot_size': 100.0,
                    'allowed_order_types': ['BUY_LIMIT', 'SELL_LIMIT'],
                    'symbol_mapping': {},
                    'orphan_management': {
                        'kill_orphaned_orders': True,
                        'max_orphan_checks': 3
                    }
                }
            },
            'ENABLE_SCHEDULING': False,
            'ENABLE_CONTINUOUS_MODE': True,
            'SCHEDULE_TIMEFRAME': 'M5',
            'SCHEDULE_OFFSET_SECONDS': 60,
            'CONTINUOUS_DELAY_SECONDS': 5,
            'CONTINUOUS_MAX_RUNTIME_HOURS': 0,
            'LOGGING_CONFIG': {
                'level': 'INFO',
                'console_output': False
            },
            'SYSTEM_CONFIG': {
                'state_file_path': os.path.join(self.temp_dir, 'test_state.json')
            }
        }
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_order_manager_initialization(self):
        """Test order manager initialization"""
        try:
            manager = OrderManager(self.test_config)
            self.assertIsNotNone(manager)
            self.assertIsNotNone(manager.connector)
            self.assertIsNotNone(manager.tracker)
        except Exception as e:
            self.fail(f"OrderManager initialization failed: {e}")
    
    @patch('order_manager.MT5Connector')
    def test_order_manager_mock_processing(self, mock_connector_class):
        """Test order manager with mocked MT5 operations"""
        # Set up mock connector
        mock_connector = Mock()
        mock_connector.connect.return_value = True
        mock_connector.disconnect.return_value = None
        mock_connector.get_pending_orders.return_value = []
        mock_connector_class.return_value = mock_connector
        
        # Create order manager
        manager = OrderManager(self.test_config)
        
        # Test processing (should not fail with empty orders)
        try:
            result = manager.process_all_terminals()
            # Result may be True or False depending on implementation
            # The important thing is that it doesn't raise an exception
            self.assertIsInstance(result, bool)
        except Exception as e:
            self.fail(f"Order processing failed: {e}")

def run_system_tests():
    """Run all system tests"""
    print("MT5 Pending Order Copier - System Tests")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestUtils))
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestOrderTracker))
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestConfiguration))
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestMT5Connector))
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestSystemIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('\n')[-2]}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('\n')[-2]}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall result: {'PASS' if success else 'FAIL'}")
    
    return success

def run_configuration_check():
    """Check configuration files"""
    print("\nConfiguration Check")
    print("-" * 30)
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if config files exist
    config_files = ['config.py', 'config_sample.py']
    
    for config_file in config_files:
        config_path = os.path.join(script_dir, config_file)
        if os.path.exists(config_path):
            print(f"✓ {config_file} exists")
            
            try:
                config = load_config(config_path)
                if config:
                    print(f"✓ {config_file} loads successfully")
                    
                    is_valid, errors = validate_config(config)
                    if is_valid:
                        print(f"✓ {config_file} validation passed")
                    else:
                        print(f"✗ {config_file} validation failed:")
                        for error in errors[:3]:  # Show first 3 errors
                            print(f"    - {error}")
                        if len(errors) > 3:
                            print(f"    ... and {len(errors) - 3} more errors")
                else:
                    print(f"✗ {config_file} failed to load")
            except Exception as e:
                print(f"✗ {config_file} error: {e}")
        else:
            print(f"✗ {config_file} not found")

def run_dependency_check():
    """Check system dependencies"""
    print("\nDependency Check")
    print("-" * 30)
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 7):
        print(f"✓ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"✗ Python {python_version.major}.{python_version.minor}.{python_version.micro} (requires 3.7+)")
    
    # Check required modules
    required_modules = [
        'MetaTrader5',
        'schedule',
        'pandas',
        'numpy',
        'yaml',
        'dateutil',
        'psutil'
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError:
            print(f"✗ {module} (install with: pip install {module})")
    
    # Check system modules
    system_modules = ['json', 'logging', 'datetime', 'time', 'os', 'sys']
    for module in system_modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError:
            print(f"✗ {module} (system module missing)")

def main():
    """Main test function"""
    print("MT5 Pending Order Copier - System Validation")
    print("=" * 60)
    
    # Run dependency check
    run_dependency_check()
    
    # Run configuration check
    run_configuration_check()
    
    # Run system tests
    print("\nRunning System Tests...")
    success = run_system_tests()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ All tests passed! System appears to be working correctly.")
        print("\nNext steps:")
        print("1. Copy config_sample.py to config.py")
        print("2. Edit config.py with your MT5 terminal details")
        print("3. Test with demo accounts first")
        print("4. Run: python main.py")
    else:
        print("✗ Some tests failed. Please review the errors above.")
        print("\nTroubleshooting:")
        print("1. Ensure all dependencies are installed")
        print("2. Check that all module files are present")
        print("3. Verify Python version is 3.7 or higher")
        print("4. Review any error messages above")
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())