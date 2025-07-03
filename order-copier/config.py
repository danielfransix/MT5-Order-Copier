# MT5 Pending Order Copier System - Configuration File
# This file contains all system configuration parameters

import os

# Source Terminal Configuration
SOURCE_TERMINAL = {
    'MT5_ACCOUNT': 123456789,
    'MT5_PASSWORD': "YOUR_SOURCE_PASSWORD",
    'MT5_SERVER': "YourBroker-Server",
    'MT5_TERMINAL_PATH': r"C:\Program Files\MetaTrader 5\terminal64.exe",
    'timeout': 10000
}

# Target Terminals Configuration
# Each terminal has individual settings for lot multipliers, constraints, and policies
TARGET_TERMINALS = {
    # 'terminal_1': {
    #     'MT5_ACCOUNT': 123456789,
    #     'MT5_PASSWORD': "YOUR_PASSWORD",
    #     'MT5_SERVER': "YourBroker-Server",
    #     'MT5_TERMINAL_PATH': r"C:\Program Files\MetaTrader 5\terminal64.exe",
    #     'timeout': 10000,
    #     'lot_multiplier': 1.0,
    #     'min_lot_size': 0.01,
    #     'max_lot_size': 100.0,
    #     'allowed_order_types': ['BUY_LIMIT', 'SELL_LIMIT', 'BUY_STOP', 'SELL_STOP', 'BUY_STOP_LIMIT', 'SELL_STOP_LIMIT'],
    #     'symbol_mapping': {
    #         'AUDJPY': 'AUDJPY.x',
    #         'AUDUSD': 'AUDUSD.x',
    #         'BRENT': 'BRENT.x',
    #         'BTCUSD': 'BTCUSD.x',
    #         'ETHUSD': 'ETHUSD.x',
    #         'GBPJPY': 'GBPJPY.x',
    #         'GBPUSD': 'GBPUSD.x',
    #         'NAT.GAS': 'NAT.GAS.x',
    #         'US2000': 'US2000.x',
    #         'US500': 'US500.x',
    #         'USDCAD': 'USDCAD.x',
    #         'USDCHF': 'USDCHF.x',
    #         'USDJPY': 'USDJPY.x',
    #         'USTEC': 'NAS100.x',
    #         'XAGUSD': 'XAGUSD.x',
    #         'XAUUSD': 'XAUUSD.x',
    #     },
    #     'orphan_management': {
    #         'kill_orphaned_orders': False,
    #         'kill_orphaned_positions': False,
    #         'orphan_check_interval': 1,  # seconds
    #         'max_orphan_checks': 1
    #     },
    #     'max_pending_orders': {
    #         'enabled': True,
    #         'max_orders': 30
    #     }
    # },
    'terminal_2': {
        'MT5_ACCOUNT': 987654321,
        'MT5_PASSWORD': "YOUR_TARGET_PASSWORD_1",
        'MT5_SERVER': "YourBroker-Server",
        'MT5_TERMINAL_PATH': r"C:\Program Files\MetaTrader 5\terminal64.exe",
        'timeout': 10000,
        'lot_multiplier': 0.5,
        'min_lot_size': 0.01,
        'max_lot_size': 100.0,
        'allowed_order_types': ['BUY_LIMIT', 'SELL_LIMIT', 'BUY_STOP', 'SELL_STOP', 'BUY_STOP_LIMIT', 'SELL_STOP_LIMIT'],
        'symbol_mapping': {
            # 'AUDJPY': 'AUDJPY.x',
            # 'AUDUSD': 'AUDUSD.x',
            # 'BRENT': 'BRENT.x',
            'BTCUSD': 'BTCUSD.x',
            # 'ETHUSD': 'ETHUSD.x',
            # 'GBPJPY': 'GBPJPY.x',
            'GBPUSD': 'GBPUSD.x',
            # 'NAT.GAS': 'NAT.GAS.x',
            # 'US2000': 'US2000.x',
            # 'US500': 'US500.x',
            'USDCAD': 'USDCAD.x',
            'USDCHF': 'USDCHF.x',
            # 'USDJPY': 'USDJPY.x',
            # 'USTEC': 'USTEC.x',
            # 'XAGUSD': 'XAGUSD.x',
            # 'XAUUSD': 'XAUUSD.x',
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
    'terminal_3': {
        'MT5_ACCOUNT': 111222333,
        'MT5_PASSWORD': "YOUR_TARGET_PASSWORD_2",
        'MT5_SERVER': "YourBroker-Server",
        'MT5_TERMINAL_PATH': r"C:\Program Files\MetaTrader 5\terminal64.exe",
        'timeout': 10000,
        'lot_multiplier': 0.5,
        'min_lot_size': 0.01,
        'max_lot_size': 100.0,
        'allowed_order_types': ['BUY_LIMIT', 'SELL_LIMIT', 'BUY_STOP', 'SELL_STOP', 'BUY_STOP_LIMIT', 'SELL_STOP_LIMIT'],
        'symbol_mapping': {
            # 'AUDJPY': 'AUDJPY.x',
            # 'AUDUSD': 'AUDUSD.x',
            # 'BRENT': 'BRENT.x',
            'BTCUSD': 'BTCUSD.x',
            # 'ETHUSD': 'ETHUSD.x',
            # 'GBPJPY': 'GBPJPY.x',
            'GBPUSD': 'GBPUSD.x',
            # 'NAT.GAS': 'NAT.GAS.x',
            # 'US2000': 'US2000.x',
            # 'US500': 'US500.x',
            'USDCAD': 'USDCAD.x',
            'USDCHF': 'USDCHF.x',
            # 'USDJPY': 'USDJPY.x',
            # 'USTEC': 'USTEC.x',
            # 'XAGUSD': 'XAGUSD.x',
            # 'XAUUSD': 'XAUUSD.x',
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
    }
}

# =============================================================================
# EXECUTION MODE CONFIGURATION (Claude-style)
# =============================================================================

# Scheduling Configuration (Claude-style)
ENABLE_SCHEDULING = False        # Set to True to run on a schedule, False for single run
SCHEDULE_TIMEFRAME = "M5"        # Candle timeframe (e.g., "M1", "M5", "M10", "M15", "M30", "H1", "H4")
SCHEDULE_OFFSET_SECONDS = 60     # Seconds *after* the candle completion to run the script

# Continuous Mode Configuration
ENABLE_CONTINUOUS_MODE = False    # Set to True for continuous operation with delays
CONTINUOUS_DELAY_SECONDS = 500     # Delay in seconds between continuous iterations
CONTINUOUS_MAX_RUNTIME_HOURS = 0 # Maximum runtime in hours (0 = unlimited)

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
        'ENABLE_SCHEDULING': ENABLE_SCHEDULING,
        'SCHEDULE_TIMEFRAME': SCHEDULE_TIMEFRAME,
        'SCHEDULE_OFFSET_SECONDS': SCHEDULE_OFFSET_SECONDS,
        'ENABLE_CONTINUOUS_MODE': ENABLE_CONTINUOUS_MODE,
        'CONTINUOUS_DELAY_SECONDS': CONTINUOUS_DELAY_SECONDS,
        'CONTINUOUS_MAX_RUNTIME_HOURS': CONTINUOUS_MAX_RUNTIME_HOURS,
        'LOGGING_CONFIG': LOGGING_CONFIG,
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
        enable_scheduling = config.get('ENABLE_SCHEDULING', False)
        schedule_timeframe = config.get('SCHEDULE_TIMEFRAME', 'M5')
        schedule_offset_seconds = config.get('SCHEDULE_OFFSET_SECONDS', 60)
        enable_continuous_mode = config.get('ENABLE_CONTINUOUS_MODE', True)
        continuous_delay_seconds = config.get('CONTINUOUS_DELAY_SECONDS', 5)
        continuous_max_runtime_hours = config.get('CONTINUOUS_MAX_RUNTIME_HOURS', 0)
        logging_config = config.get('LOGGING_CONFIG', {})
        system_config = config.get('SYSTEM_CONFIG', {})
    else:
        source_terminal = SOURCE_TERMINAL
        target_terminals = TARGET_TERMINALS
        enable_scheduling = ENABLE_SCHEDULING
        schedule_timeframe = SCHEDULE_TIMEFRAME
        schedule_offset_seconds = SCHEDULE_OFFSET_SECONDS
        enable_continuous_mode = ENABLE_CONTINUOUS_MODE
        continuous_delay_seconds = CONTINUOUS_DELAY_SECONDS
        continuous_max_runtime_hours = CONTINUOUS_MAX_RUNTIME_HOURS
        logging_config = LOGGING_CONFIG
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
    
    # Validate scheduling configuration
    if not isinstance(enable_scheduling, bool):
        errors.append("ENABLE_SCHEDULING must be a boolean")
    
    if enable_scheduling:
        # Validate schedule timeframe
        valid_timeframes = ['M1', 'M5', 'M10', 'M15', 'M30', 'H1', 'H4', 'D1']
        if schedule_timeframe not in valid_timeframes:
            errors.append(f"SCHEDULE_TIMEFRAME must be one of: {', '.join(valid_timeframes)}")
        
        # Validate schedule offset
        if not isinstance(schedule_offset_seconds, int) or schedule_offset_seconds < 0:
            errors.append("SCHEDULE_OFFSET_SECONDS must be a non-negative integer")
    
    # Validate continuous mode configuration
    if not isinstance(enable_continuous_mode, bool):
        errors.append("ENABLE_CONTINUOUS_MODE must be a boolean")
    
    if enable_continuous_mode:
        # Validate continuous delay
        if not isinstance(continuous_delay_seconds, (int, float)) or continuous_delay_seconds < 0:
            errors.append("CONTINUOUS_DELAY_SECONDS must be a non-negative number")
        
        # Validate max runtime
        if not isinstance(continuous_max_runtime_hours, (int, float)) or continuous_max_runtime_hours < 0:
            errors.append("CONTINUOUS_MAX_RUNTIME_HOURS must be a non-negative number")
    
    # Note: When both execution modes are disabled, system runs once and exits
    
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

def is_scheduling_enabled():
    """Check if scheduling is enabled"""
    return ENABLE_SCHEDULING

def is_continuous_mode_enabled():
    """Check if continuous mode is enabled"""
    return ENABLE_CONTINUOUS_MODE

def get_schedule_timeframe():
    """Get schedule timeframe"""
    return SCHEDULE_TIMEFRAME

def get_schedule_offset_seconds():
    """Get schedule offset in seconds"""
    return SCHEDULE_OFFSET_SECONDS

def get_continuous_delay_seconds():
    """Get continuous mode delay in seconds"""
    return CONTINUOUS_DELAY_SECONDS