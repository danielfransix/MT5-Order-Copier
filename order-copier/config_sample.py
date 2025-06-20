# MT5 Pending Order Copier System - Sample Configuration
# Copy this file to 'config.py' and modify the settings for your environment

import os

# =============================================================================
# SOURCE TERMINAL CONFIGURATION
# =============================================================================
# The terminal from which orders will be copied
SOURCE_TERMINAL = {
    'MT5_ACCOUNT': 12345678,                                      # Your MT5 account number
    'MT5_PASSWORD': 'your_source_password',                       # Your MT5 password
    'MT5_SERVER': 'YourBroker-Demo',                              # Your broker's server name
    'MT5_TERMINAL_PATH': r'C:\Program Files\MetaTrader 5\terminal64.exe', # Path to MT5 executable
    'timeout': 10000                                              # Connection timeout in milliseconds
}

# =============================================================================
# TARGET TERMINALS CONFIGURATION
# =============================================================================
# Terminals to which orders will be copied
# Each terminal has individual settings for lot multipliers, constraints, and policies
TARGET_TERMINALS = {
    # Example Terminal 1 - Conservative Copy
    'ConservativeAccount': {
        'MT5_ACCOUNT': 87654321,
        'MT5_PASSWORD': 'target_password_1',
        'MT5_SERVER': 'TargetBroker-Demo',
        'MT5_TERMINAL_PATH': r'C:\Program Files\MetaTrader 5\terminal64.exe',
        'timeout': 10000,
        
        # Lot size management
        'lot_multiplier': 0.5,                                     # Copy with 50% of source lot size
        'min_lot_size': 0.01,                                      # Minimum allowed lot size
        'max_lot_size': 1.0,                                       # Maximum allowed lot size
        
        # Order type filtering
        'allowed_order_types': ['BUY_LIMIT', 'SELL_LIMIT', 'BUY_STOP', 'SELL_STOP', 'BUY_STOP_LIMIT', 'SELL_STOP_LIMIT'],
        
        # Symbol mapping (source_symbol: target_symbol)
        'symbol_mapping': {
            'EURUSD': 'EURUSD.m',
            'GBPUSD': 'GBPUSD.m',
            # Add more mappings as needed
        },
        
        # Orphan order/position management
        'orphan_management': {
            'kill_orphaned_orders': True,                          # Remove orders that no longer exist in source
            'kill_orphaned_positions': True,                       # Close positions that no longer exist in source
            'orphan_check_interval': 60,                           # seconds between checks
            'max_orphan_checks': 3                                 # Number of checks before declaring orphan
        },
        
        # Maximum pending orders limit
        'max_pending_orders': {
            'enabled': True,
            'max_orders': 30                                       # Maximum number of pending orders
        }
    },
    
    # Example Terminal 2 - Add more terminals here
    # 'AggressiveAccount': {
    #     'MT5_ACCOUNT': 11223344,
    #     'MT5_PASSWORD': 'target_password_2',
    #     'MT5_SERVER': 'AnotherBroker-Demo',
    #     'MT5_TERMINAL_PATH': r'C:\Program Files\Another MT5\terminal64.exe',
    #     'timeout': 10000,
    #     'lot_multiplier': 2.0,
    #     'min_lot_size': 0.1,
    #     'max_lot_size': 20.0,
    #     'allowed_order_types': ['BUY_LIMIT', 'SELL_LIMIT', 'BUY_STOP', 'SELL_STOP'],
    #     'symbol_mapping': {
    #         'XAUUSD': 'GOLD'
    #     },
    #     'orphan_management': {
    #         'kill_orphaned_orders': False,
    #         'kill_orphaned_positions': False,
    #         'orphan_check_interval': 300,
    #         'max_orphan_checks': 5
    #     },
    #     'max_pending_orders': {
    #         'enabled': False
    #     }
    # }
}

# =============================================================================
# EXECUTION MODE CONFIGURATION
# =============================================================================
# Choose execution mode: 'once', 'scheduled', or 'continuous'
EXECUTION_MODE = 'once'  # Set to 'once' to run once and exit, 'scheduled' for periodic runs, 'continuous' for non-stop operation

# Configuration for 'scheduled' execution mode
SCHEDULE_CONFIG = {
    'interval_seconds': 60,                                        # Run every 60 seconds
    'max_iterations': 0                                            # 0 = unlimited iterations
}

# Configuration for 'continuous' execution mode
CONTINUOUS_CONFIG = {
    'delay_seconds': 5,                                            # 5 second delay between iterations
    'max_runtime_hours': 0                                        # 0 = unlimited runtime
}

# Legacy scheduled execution configuration (deprecated - use EXECUTION_MODE instead)
SCHEDULED_EXECUTION = {
    'enabled': False,          # Boolean: Enable scheduled runs
    'interval_seconds': 300,   # Integer: Seconds between runs (when enabled)
}

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
LOGGING_CONFIG = {
    'level': 'INFO',                                               # Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
    # The log file path is relative to this config file.
    'file_path': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'mt5_order_copier.log'),
    'max_file_size': 10,                                          # Maximum log file size in MB
    'backup_count': 5,                                            # Number of backup files to keep
    'console_output': True,                                       # Enable console output
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # Log format
}

# =============================================================================
# SYSTEM CONFIGURATION
# =============================================================================
SYSTEM_CONFIG = {
    'connection_timeout': 90,      # seconds to wait for terminal connection
    'max_retries': 5,              # max number of retries for failed connections
    'retry_delay': 5,              # seconds to wait between retries
    'log_level': 'INFO',           # (deprecated - use LOGGING_CONFIG)
    'log_file': 'mt5_copier.log'   # (deprecated - use LOGGING_CONFIG)
}

# NOTE: The functions below (load_config, validate_config, etc.) are part of the
# main application's config module ('config.py') and are not needed in this sample file.
# When you copy this file to 'config.py', the application will use these settings
# and its own internal functions to load and validate them.