# MT5 Pending Order Copier System - Sample Configuration
# Copy this file to 'config.py' and modify the settings for your environment

# =============================================================================
# SOURCE TERMINAL CONFIGURATION
# =============================================================================
# The terminal from which orders will be copied
SOURCE_TERMINAL = {
    'login': 12345678,                                              # Your MT5 login number
    'password': 'your_source_password',                             # Your MT5 password
    'server': 'YourBroker-Demo',                                   # Your broker's server name
    'path': r'C:\Program Files\MetaTrader 5\terminal64.exe',       # Path to MT5 executable
    'timeout': 10000                                               # Connection timeout in milliseconds
}

# =============================================================================
# TARGET TERMINALS CONFIGURATION
# =============================================================================
# Terminals to which orders will be copied
TARGET_TERMINALS = {
    # Example Terminal 1 - Conservative Copy
    'ConservativeAccount': {
        'login': 87654321,
        'password': 'target_password_1',
        'server': 'TargetBroker-Demo',
        'path': r'C:\Program Files\MetaTrader 5\terminal64.exe',
        'timeout': 10000,
        
        # Lot size management
        'lot_multiplier': 0.5,                                     # Copy with 50% of source lot size
        'min_lot_size': 0.01,                                      # Minimum allowed lot size
        'max_lot_size': 10.0,                                      # Maximum allowed lot size
        
        # Order type filtering
        'allowed_order_types': [
            'BUY_LIMIT',
            'SELL_LIMIT',
            'BUY_STOP',
            'SELL_STOP'
        ],
        
        # Symbol mapping (source_symbol: target_symbol)
        'symbol_mapping': {
            'EURUSD': 'EURUSD',
            'GBPUSD': 'GBPUSD',
            'USDJPY': 'USDJPY',
            'AUDUSD': 'AUDUSD',
            'USDCAD': 'USDCAD',
            'USDCHF': 'USDCHF',
            'NZDUSD': 'NZDUSD',
            'EURGBP': 'EURGBP',
            'EURJPY': 'EURJPY',
            'GBPJPY': 'GBPJPY'
        },
        
        # Orphan order management
        'orphan_management': {
            'kill_orphaned_orders': True,                          # Remove orders that no longer exist in source
            'max_orphan_checks': 3                                 # Number of checks before removing orphan
        },
        
        # Maximum pending orders limit
        'max_pending_orders': {
            'enabled': True,
            'max_orders': 50                                       # Maximum number of pending orders
        }
    },
    
    # Example Terminal 2 - Aggressive Copy
    'AggressiveAccount': {
        'login': 11223344,
        'password': 'target_password_2',
        'server': 'AnotherBroker-Demo',
        'path': r'C:\Program Files\MetaTrader 5\terminal64.exe',
        'timeout': 10000,
        
        # Lot size management
        'lot_multiplier': 2.0,                                     # Copy with 200% of source lot size
        'min_lot_size': 0.01,
        'max_lot_size': 100.0,
        
        # Order type filtering - all types allowed
        'allowed_order_types': [
            'BUY_LIMIT',
            'SELL_LIMIT',
            'BUY_STOP',
            'SELL_STOP',
            'BUY_STOP_LIMIT',
            'SELL_STOP_LIMIT'
        ],
        
        # Symbol mapping with different broker suffixes
        'symbol_mapping': {
            'EURUSD': 'EURUSD.raw',
            'GBPUSD': 'GBPUSD.raw',
            'USDJPY': 'USDJPY.raw',
            'AUDUSD': 'AUDUSD.raw',
            'GOLD': 'XAUUSD',
            'SILVER': 'XAGUSD',
            'US30': 'US30.cash',
            'SPX500': 'SPX500.cash'
        },
        
        # Orphan order management
        'orphan_management': {
            'kill_orphaned_orders': True,
            'max_orphan_checks': 1                                 # Quick orphan removal
        },
        
        # Maximum pending orders limit
        'max_pending_orders': {
            'enabled': True,
            'max_orders': 100
        }
    },
    
    # Example Terminal 3 - Micro Account
    'MicroAccount': {
        'login': 55667788,
        'password': 'target_password_3',
        'server': 'MicroBroker-Demo',
        'path': r'C:\Program Files\MetaTrader 5\terminal64.exe',
        'timeout': 10000,
        
        # Lot size management for micro account
        'lot_multiplier': 0.1,                                     # Copy with 10% of source lot size
        'min_lot_size': 0.01,
        'max_lot_size': 1.0,                                       # Lower maximum for micro account
        
        # Order type filtering - only limit orders
        'allowed_order_types': [
            'BUY_LIMIT',
            'SELL_LIMIT'
        ],
        
        # Symbol mapping
        'symbol_mapping': {
            'EURUSD': 'EURUSDm',
            'GBPUSD': 'GBPUSDm',
            'USDJPY': 'USDJPYm'
        },
        
        # Orphan order management - keep orphans for manual review
        'orphan_management': {
            'kill_orphaned_orders': False,                         # Don't auto-remove orphans
            'max_orphan_checks': 5
        },
        
        # Maximum pending orders limit
        'max_pending_orders': {
            'enabled': True,
            'max_orders': 20                                       # Lower limit for micro account
        }
    }
}

# =============================================================================
# EXECUTION CONFIGURATION (Claude-style)
# =============================================================================
# Enable/disable execution modes
ENABLE_SCHEDULING = True                                           # Enable scheduled execution
ENABLE_CONTINUOUS_MODE = False                                     # Enable continuous execution

# Scheduling parameters (when ENABLE_SCHEDULING = True)
SCHEDULE_TIMEFRAME = 'M5'                                         # M1, M5, M15, M30, H1, H4, D1
SCHEDULE_OFFSET_SECONDS = 60                                       # Offset from timeframe boundary

# Continuous mode parameters (when ENABLE_CONTINUOUS_MODE = True)
CONTINUOUS_DELAY_SECONDS = 5                                       # Delay between iterations
CONTINUOUS_MAX_RUNTIME_HOURS = 0                                   # 0 = unlimited runtime

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
LOGGING_CONFIG = {
    'level': 'INFO',                                               # Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
    'file_path': 'logs/mt5_order_copier.log',                     # Log file path
    'max_file_size': 10,                                          # Maximum log file size in MB
    'backup_count': 5,                                            # Number of backup log files to keep
    'console_output': True                                        # Also output logs to console
}

# =============================================================================
# SYSTEM CONFIGURATION
# =============================================================================
SYSTEM_CONFIG = {
    'state_file_path': 'data/order_tracker_state.json',          # Path to state persistence file
    'connection_retry_attempts': 3,                               # Number of connection retry attempts
    'connection_retry_delay': 5,                                  # Delay between retry attempts in seconds
    'order_operation_timeout': 30,                               # Timeout for order operations in seconds
    'price_tolerance': 1e-5,                                     # Price comparison tolerance
    'volume_tolerance': 1e-6                                     # Volume comparison tolerance
}

# =============================================================================
# ADVANCED CONFIGURATION OPTIONS
# =============================================================================

# Global order type mappings (if needed)
ORDER_TYPE_MAPPINGS = {
    # Map source order types to target order types if different
    # 'SOURCE_TYPE': 'TARGET_TYPE'
}

# Global symbol filters
SYMBOL_FILTERS = {
    'include_patterns': [],                                       # Only include symbols matching these patterns
    'exclude_patterns': ['*_test*', '*_demo*'],                  # Exclude symbols matching these patterns
    'case_sensitive': False                                       # Pattern matching case sensitivity
}

# Performance optimization settings
PERFORMANCE_CONFIG = {
    'batch_size': 10,                                            # Number of orders to process in batch
    'parallel_terminals': False,                                 # Process terminals in parallel (experimental)
    'cache_symbol_info': True,                                   # Cache symbol information
    'cache_duration_seconds': 300                                # Cache duration in seconds
}

# =============================================================================
# NOTIFICATION CONFIGURATION (Optional)
# =============================================================================
NOTIFICATION_CONFIG = {
    'enabled': False,                                            # Enable notifications
    'email': {
        'enabled': False,
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'username': 'your_email@gmail.com',
        'password': 'your_app_password',
        'to_addresses': ['recipient@example.com'],
        'subject_prefix': '[MT5 Order Copier]'
    },
    'webhook': {
        'enabled': False,
        'url': 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL',
        'method': 'POST',
        'headers': {'Content-Type': 'application/json'}
    }
}

# =============================================================================
# DEVELOPMENT AND TESTING CONFIGURATION
# =============================================================================
DEVELOPMENT_CONFIG = {
    'dry_run': False,                                            # Enable dry run mode (no actual orders placed)
    'debug_mode': False,                                         # Enable debug mode with extra logging
    'test_mode': False,                                          # Enable test mode with mock data
    'simulation_delay': 0,                                       # Add artificial delay for testing
    'max_test_orders': 5                                         # Maximum orders to process in test mode
}

# =============================================================================
# VALIDATION RULES
# =============================================================================
# These settings help validate the configuration
VALIDATION_RULES = {
    'require_source_terminal': True,
    'require_target_terminals': True,
    'min_target_terminals': 1,
    'max_target_terminals': 10,
    'validate_mt5_paths': True,
    'validate_symbol_mappings': True,
    'validate_lot_sizes': True
}

# =============================================================================
# EXAMPLE CONFIGURATIONS FOR DIFFERENT USE CASES
# =============================================================================

# Uncomment and modify one of these examples for quick setup:

# # Example 1: Simple 1-to-1 copy with same broker
# SOURCE_TERMINAL = {
#     'login': 12345678,
#     'password': 'password123',
#     'server': 'Broker-Demo',
#     'path': r'C:\Program Files\MetaTrader 5\terminal64.exe',
#     'timeout': 10000
# }
# 
# TARGET_TERMINALS = {
#     'CopyAccount': {
#         'login': 87654321,
#         'password': 'password456',
#         'server': 'Broker-Demo',
#         'path': r'C:\Program Files\MetaTrader 5\terminal64.exe',
#         'timeout': 10000,
#         'lot_multiplier': 1.0,
#         'min_lot_size': 0.01,
#         'max_lot_size': 100.0,
#         'allowed_order_types': ['BUY_LIMIT', 'SELL_LIMIT', 'BUY_STOP', 'SELL_STOP'],
#         'symbol_mapping': {},  # Empty = direct copy
#         'orphan_management': {'kill_orphaned_orders': True, 'max_orphan_checks': 3},
#         'max_pending_orders': {'enabled': False}
#     }
# }

# # Example 2: Risk-managed copy with reduced lot sizes
# TARGET_TERMINALS = {
#     'RiskManagedAccount': {
#         'login': 11111111,
#         'password': 'riskpass',
#         'server': 'RiskBroker-Demo',
#         'path': r'C:\Program Files\MetaTrader 5\terminal64.exe',
#         'timeout': 10000,
#         'lot_multiplier': 0.1,  # 10% of source position
#         'min_lot_size': 0.01,
#         'max_lot_size': 1.0,    # Maximum 1 lot
#         'allowed_order_types': ['BUY_LIMIT', 'SELL_LIMIT'],  # Only limit orders
#         'symbol_mapping': {},
#         'orphan_management': {'kill_orphaned_orders': True, 'max_orphan_checks': 2},
#         'max_pending_orders': {'enabled': True, 'max_orders': 10}
#     }
# }

# # Example 3: Multi-broker setup with symbol mapping
# TARGET_TERMINALS = {
#     'BrokerA': {
#         'login': 22222222,
#         'password': 'brokerA_pass',
#         'server': 'BrokerA-Demo',
#         'path': r'C:\Program Files\MetaTrader 5\terminal64.exe',
#         'timeout': 10000,
#         'lot_multiplier': 1.0,
#         'symbol_mapping': {
#             'EURUSD': 'EURUSD.raw',
#             'GBPUSD': 'GBPUSD.raw',
#             'GOLD': 'XAUUSD'
#         },
#         'orphan_management': {'kill_orphaned_orders': True, 'max_orphan_checks': 3}
#     },
#     'BrokerB': {
#         'login': 33333333,
#         'password': 'brokerB_pass',
#         'server': 'BrokerB-Demo',
#         'path': r'C:\Program Files\MetaTrader 5\terminal64.exe',
#         'timeout': 10000,
#         'lot_multiplier': 0.5,
#         'symbol_mapping': {
#             'EURUSD': 'EUR/USD',
#             'GBPUSD': 'GBP/USD',
#             'GOLD': 'Gold'
#         },
#         'orphan_management': {'kill_orphaned_orders': True, 'max_orphan_checks': 3}
#     }
# }