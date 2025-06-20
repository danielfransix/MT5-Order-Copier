#!/usr/bin/env python3
"""Test script to validate the configuration"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config import validate_config, load_config
    
    print("Loading configuration...")
    config = load_config()
    
    print("\nValidating configuration...")
    is_valid, errors = validate_config(config)
    
    if is_valid:
        print("✓ Configuration is valid - all validations passed")
        print("\nConfiguration summary:")
        print(f"  - Execution mode: {config.get('EXECUTION_MODE')}")
        print(f"  - Source terminal: {config['SOURCE_TERMINAL']['MT5_SERVER']}")
        print(f"  - Target terminals: {len(config['TARGET_TERMINALS'])}")
        print(f"  - Logging level: {config['LOGGING_CONFIG']['level']}")
    else:
        print("✗ Configuration errors found:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
        
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

print("\nConfiguration test completed successfully!")