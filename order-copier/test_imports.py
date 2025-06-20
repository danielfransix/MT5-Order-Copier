#!/usr/bin/env python3
# Quick import test script

try:
    print("Testing imports...")
    
    from config import load_config, validate_config
    print("✓ config module imported successfully")
    
    from order_manager import OrderManager
    print("✓ order_manager module imported successfully")
    
    from mt5_connector import MT5Connector
    print("✓ mt5_connector module imported successfully")
    
    from order_tracker import OrderTracker
    print("✓ order_tracker module imported successfully")
    
    from utils import setup_logging
    print("✓ utils module imported successfully")
    
    print("\nAll imports successful! No import errors found.")
    
except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")