# MT5 Pending Order Copier System - Configuration File
# This file contains all system configuration parameters

import os

# Source Terminal Configuration
SOURCE_TERMINAL = {
    'MT5_ACCOUNT': "YOUR_SOURCE_ACCOUNT",
    'MT5_PASSWORD': "YOUR_SOURCE_PASSWORD",
    'MT5_SERVER': "YOUR_SOURCE_SERVER",
    'MT5_TERMINAL_PATH': r"C:\path\to\your\source\terminal64.exe",
    'timeout': 10000
}

# Target Terminals Configuration
# Each terminal has individual settings for lot multipliers, constraints, and policies
TARGET_TERMINALS = {
    'terminal_1': {
        'MT5_ACCOUNT': "YOUR_TARGET_ACCOUNT",
        'MT5_PASSWORD': "YOUR_TARGET_PASSWORD",
        'MT5_SERVER': "YOUR_TARGET_SERVER",
        'MT5_TERMINAL_PATH': r"C:\path\to\your\target\terminal64.exe",
        'timeout': 10000,
        'lot_multiplier': 1.0,
        'min_lot_size': 0.01,
        'max_lot_size': 1.0,
        'allowed_order_types': ['BUY_LIMIT', 'SELL_LIMIT', 'BUY_STOP', 'SELL_STOP', 'BUY_STOP_LIMIT', 'SELL_STOP_LIMIT'],
        'symbol_mapping': {
            'AUDCAD': 'AUDCAD.x',
            'AUDCHF': 'AUDCHF.x',
            'AUDJPY': 'AUDJPY.x',
            'AUDNZD': 'AUDNZD.x',
            'AUDUSD': 'AUDUSD.x',
            'CADCHF': 'CADCHF.x',
            'CADJPY': 'CADJPY.x',
            'CHFJPY': 'CHFJPY.x',
            'EURAUD': 'EURAUD.x',
            'EURCAD': 'EURCAD.x',
            'EURCHF': 'EURCHF.x',
            'EURGBP': 'EURGBP.x',
            'EURJPY': 'EURJPY.x',
            'EURNZD': 'EURNZD.x',
            'EURUSD': 'EURUSD.x',
            'GBPAUD': 'GBPAUD.x',
            'GBPCAD': 'GBPCAD.x',
            'GBPCHF': 'GBPCHF.x',
            'GBPJPY': 'GBPJPY.x',
            'GBPNZD': 'GBPNZD.x',
            'GBPUSD': 'GBPUSD.x',
            'NZDCAD': 'NZDCAD.x',
            'NZDCHF': 'NZDCHF.x',
            'NZDJPY': 'NZDJPY.x',
            'NZDUSD': 'NZDUSD.x',
            'USDCAD': 'USDCAD.x',
            'USDCHF': 'USDCHF.x',
            'USDJPY': 'USDJPY.x',
        },
        'orphan_management': {
            'kill_orphaned_orders': True,
            'kill_orphaned_positions': True,
            'orphan_check_interval': 1,  # seconds
            'max_orphan_checks': 1
        },
        'max_pending_orders': {
            'enabled': True,
            'max_orders': 30
        }
    },
    # 'terminal_2': {
    #     'MT5_ACCOUNT': 67890,
    #     'MT5_PASSWORD': "password456",
    #     'MT5_SERVER': "Broker-Server-2",
    #     'MT5_TERMINAL_PATH': r"C:\Program Files\MT5_2\terminal64.exe",
    #     'lot_multiplier': 0.5,
    #     'min_lot_size': 0.1,
    #     'max_lot_size': 10.0,
    #     'allowed_order_types': ['BUY_LIMIT', 'SELL_LIMIT'],  # Only limit orders
    #     'symbol_mapping': {
    #         'EURUSD': 'EURUSDm',
    #         'XAUUSD': 'XAUUSDm'
    #     },
    #     'orphan_management': {
    #         'kill_orphaned_orders': False,  # Different policy for this terminal
    #         'orphan_check_interval': 600,
    #         'max_orphan_checks': 5
    #     },
    #     'max_pending_orders': {
    #         'enabled': False  # No limit for this terminal
    #     }
    # }
}

# =============================================================================
# EXECUTION MODE CONFIGURATION
# =============================================================================
# Choose execution mode: 'once', 'scheduled', or 'continuous'
EXECUTION_MODE = 'once'  # Set to 'once' to run once and exit

# Configuration for scheduled execution mode
SCHEDULE_CONFIG = {
    'interval_seconds': 60,                                        # Run every 60 seconds
    'max_iterations': 0                                            # 0 = unlimited iterations
}

# Configuration for continuous execution mode
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
    'file_path': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'mt5_order_copier.log'),  # Log file path
    'max_file_size': 10,                                          # Maximum log file size in MB
    'backup_count': 5,                                            # Number of backup files to keep
    'console_output': True,                                       # Enable console output
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # Log format
}

# System Configuration
SYSTEM_CONFIG = {
    'connection_timeout': 90,      # seconds
    'max_retries': 5,
    'retry_delay': 5,              # seconds
    'log_level': 'INFO',           # DEBUG, INFO, WARNING, ERROR (deprecated - use LOGGING_CONFIG)
    'log_file': 'mt5_copier.log'   # (deprecated - use LOGGING_CONFIG)
}

# Configuration Loading Function
def load_config(config_path=None):
    """Load and return the complete configuration dictionary
    
    Args:
        config_path: Optional path to config file (for compatibility, currently unused)
    """
    return {
        'SOURCE_TERMINAL': SOURCE_TERMINAL,
        'TARGET_TERMINALS': TARGET_TERMINALS,
        'EXECUTION_MODE': EXECUTION_MODE,
        'SCHEDULE_CONFIG': SCHEDULE_CONFIG,
        'CONTINUOUS_CONFIG': CONTINUOUS_CONFIG,
        'LOGGING_CONFIG': LOGGING_CONFIG,
        'SCHEDULED_EXECUTION': SCHEDULED_EXECUTION,  # Legacy support
        'SYSTEM_CONFIG': SYSTEM_CONFIG
    }

# Validation Functions
def validate_config(config=None):
    """Validate all configuration parameters"""
    errors = []
    
    # Use passed config or fall back to global variables
    if config:
        source_terminal = config.get('SOURCE_TERMINAL', {})
        target_terminals = config.get('TARGET_TERMINALS', {})
        execution_mode = config.get('EXECUTION_MODE', 'once')
        schedule_config = config.get('SCHEDULE_CONFIG', {})
        continuous_config = config.get('CONTINUOUS_CONFIG', {})
        logging_config = config.get('LOGGING_CONFIG', {})
        scheduled_execution = config.get('SCHEDULED_EXECUTION', {})
        system_config = config.get('SYSTEM_CONFIG', {})
    else:
        source_terminal = SOURCE_TERMINAL
        target_terminals = TARGET_TERMINALS
        execution_mode = EXECUTION_MODE
        schedule_config = SCHEDULE_CONFIG
        continuous_config = CONTINUOUS_CONFIG
        logging_config = LOGGING_CONFIG
        scheduled_execution = SCHEDULED_EXECUTION
        system_config = SYSTEM_CONFIG

    # Validate source terminal
    if not source_terminal.get('MT5_ACCOUNT'):
        errors.append("Source terminal MT5_ACCOUNT is required")
    if not source_terminal.get('MT5_PASSWORD'):
        errors.append("Source terminal MT5_PASSWORD is required")
    if not source_terminal.get('MT5_SERVER'):
        errors.append("Source terminal MT5_SERVER is required")
    if not source_terminal.get('MT5_TERMINAL_PATH'):
        errors.append("Source terminal MT5_TERMINAL_PATH is required")

    # Validate target terminals
    if not target_terminals:
        errors.append("At least one target terminal must be configured")
    
    for terminal_name, terminal_config in target_terminals.items():
        # Required fields
        required_fields = ['MT5_ACCOUNT', 'MT5_PASSWORD', 'MT5_SERVER', 'MT5_TERMINAL_PATH']
        for field in required_fields:
            if not terminal_config.get(field):
                errors.append(f"Terminal {terminal_name}: {field} is required")

        # Lot multiplier validation
        lot_multiplier = terminal_config.get('lot_multiplier', 1.0)
        if not isinstance(lot_multiplier, (int, float)) or lot_multiplier <= 0:
            errors.append(f"Terminal {terminal_name}: lot_multiplier must be a positive number")

        # Lot size validation
        min_lot = terminal_config.get('min_lot_size', 0.01)
        max_lot = terminal_config.get('max_lot_size', 100.0)
        if not isinstance(min_lot, (int, float)) or min_lot <= 0:
            errors.append(f"Terminal {terminal_name}: min_lot_size must be a positive number")
        if not isinstance(max_lot, (int, float)) or max_lot <= 0:
            errors.append(f"Terminal {terminal_name}: max_lot_size must be a positive number")
        if min_lot >= max_lot:
            errors.append(f"Terminal {terminal_name}: min_lot_size must be less than max_lot_size")
        
        # Order types validation
        allowed_types = terminal_config.get('allowed_order_types', [])
        valid_order_types = ['BUY_LIMIT', 'SELL_LIMIT', 'BUY_STOP', 'SELL_STOP', 'BUY_STOP_LIMIT', 'SELL_STOP_LIMIT']
        for order_type in allowed_types:
            if order_type not in valid_order_types:
                errors.append(f"Terminal {terminal_name}: Invalid order type '{order_type}'")

        # Orphan management validation
        orphan_config = terminal_config.get('orphan_management', {})
        if 'orphan_check_interval' in orphan_config:
            interval = orphan_config['orphan_check_interval']
            if not isinstance(interval, int) or interval <= 0:
                errors.append(f"Terminal {terminal_name}: orphan_check_interval must be a positive integer")
        
        if 'max_orphan_checks' in orphan_config:
            max_checks = orphan_config['max_orphan_checks']
            if not isinstance(max_checks, int) or max_checks <= 0:
                errors.append(f"Terminal {terminal_name}: max_orphan_checks must be a positive integer")
        
        # Max pending orders validation
        max_orders_config = terminal_config.get('max_pending_orders', {})
        if max_orders_config.get('enabled', False):
            max_orders = max_orders_config.get('max_orders')
            if not isinstance(max_orders, int) or max_orders <= 0:
                errors.append(f"Terminal {terminal_name}: max_orders must be a positive integer when enabled")
    
    # Validate execution mode
    valid_execution_modes = ['once', 'scheduled', 'continuous']
    if execution_mode not in valid_execution_modes:
        errors.append(f"EXECUTION_MODE must be one of: {', '.join(valid_execution_modes)}")
    
    # Validate schedule config
    if execution_mode == 'scheduled':
        interval = schedule_config.get('interval_seconds')
        if not isinstance(interval, int) or interval <= 0:
            errors.append("SCHEDULE_CONFIG interval_seconds must be a positive integer")
        
        max_iterations = schedule_config.get('max_iterations', 0)
        if not isinstance(max_iterations, int) or max_iterations < 0:
            errors.append("SCHEDULE_CONFIG max_iterations must be a non-negative integer")
    
    # Validate continuous config
    if execution_mode == 'continuous':
        delay = continuous_config.get('delay_seconds')
        if not isinstance(delay, (int, float)) or delay < 0:
            errors.append("CONTINUOUS_CONFIG delay_seconds must be a non-negative number")
        
        max_runtime = continuous_config.get('max_runtime_hours', 0)
        if not isinstance(max_runtime, (int, float)) or max_runtime < 0:
            errors.append("CONTINUOUS_CONFIG max_runtime_hours must be a non-negative number")
    
    # Validate logging config
    log_level = logging_config.get('level', 'INFO')
    valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if log_level not in valid_log_levels:
        errors.append(f"LOGGING_CONFIG level must be one of: {', '.join(valid_log_levels)}")
    
    max_file_size = logging_config.get('max_file_size', 10)
    if not isinstance(max_file_size, (int, float)) or max_file_size <= 0:
        errors.append("LOGGING_CONFIG max_file_size must be a positive number")
    
    backup_count = logging_config.get('backup_count', 5)
    if not isinstance(backup_count, int) or backup_count < 0:
        errors.append("LOGGING_CONFIG backup_count must be a non-negative integer")

    # Validate scheduled execution (legacy)
    if scheduled_execution.get('enabled', False):
        interval = scheduled_execution.get('interval_seconds')
        if not isinstance(interval, int) or interval <= 0:
            errors.append("Scheduled execution interval_seconds must be a positive integer")

    # Validate system config
    timeout = system_config.get('connection_timeout', 30)
    if not isinstance(timeout, int) or timeout <= 0:
        errors.append("System connection_timeout must be a positive integer")

    retries = system_config.get('max_retries', 3)
    if not isinstance(retries, int) or retries < 0:
        errors.append("System max_retries must be a non-negative integer")

    delay = system_config.get('retry_delay', 5)
    if not isinstance(delay, (int, float)) or delay < 0:
        errors.append("System retry_delay must be a non-negative number")
    
    return len(errors) == 0, errors

def get_terminal_config(terminal_name):
    """Get configuration for a specific terminal"""
    return TARGET_TERMINALS.get(terminal_name)

def get_all_terminal_names():
    """Get list of all configured terminal names"""
    return list(TARGET_TERMINALS.keys())

def is_scheduled_execution_enabled():
    """Check if scheduled execution is enabled"""
    return SCHEDULED_EXECUTION.get('enabled', False)

def get_execution_interval():
    """Get execution interval in seconds"""
    return SCHEDULED_EXECUTION.get('interval_seconds', 300)