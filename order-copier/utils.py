# MT5 Pending Order Copier System - Utility Functions
# This module contains helper functions and utilities used throughout the system

import logging
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union

# Logging setup
def setup_logging(log_level: str = 'INFO', log_file: str = 'mt5_copier.log') -> logging.Logger:
    """Setup logging configuration for the system"""
    logger = logging.getLogger('MT5_Copier')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def format_currency_pair(symbol: str) -> str:
    """Format currency pair symbol consistently"""
    return symbol.upper().strip()

def calculate_lot_size(source_lot: float, multiplier: float, min_lot: float, max_lot: float) -> float:
    """Calculate target lot size with constraints"""
    target_lot = source_lot * multiplier
    
    # Apply constraints
    target_lot = max(min_lot, min(max_lot, target_lot))
    
    # Round to appropriate precision (typically 0.01 for most brokers)
    target_lot = round(target_lot, 2)
    
    return target_lot

def validate_lot_size(lot_size: float, min_lot: float, max_lot: float) -> bool:
    """Validate if lot size is within acceptable range"""
    return min_lot <= lot_size <= max_lot

def format_price(price: float, digits: int = 5) -> float:
    """Format price to appropriate decimal places"""
    return round(price, digits)

def is_valid_order_type(order_type: str, allowed_types: List[str]) -> bool:
    """Check if order type is allowed for the terminal"""
    return order_type in allowed_types

def get_order_type_name(order_type_code: int) -> str:
    """Convert MT5 order type code to readable name"""
    order_type_map = {
        2: 'BUY_LIMIT',
        3: 'SELL_LIMIT',
        4: 'BUY_STOP',
        5: 'SELL_STOP',
        6: 'BUY_STOP_LIMIT',
        7: 'SELL_STOP_LIMIT'
    }
    return order_type_map.get(order_type_code, f'UNKNOWN_{order_type_code}')

def get_order_type_code(order_type_name: str) -> int:
    """Convert order type name to MT5 code"""
    order_type_map = {
        'BUY_LIMIT': 2,
        'SELL_LIMIT': 3,
        'BUY_STOP': 4,
        'SELL_STOP': 5,
        'BUY_STOP_LIMIT': 6,
        'SELL_STOP_LIMIT': 7
    }
    return order_type_map.get(order_type_name, -1)

def safe_float_compare(a: float, b: float, tolerance: float = 1e-5) -> bool:
    """Safely compare floating point numbers with tolerance"""
    return abs(a - b) <= tolerance

def format_datetime(dt: datetime) -> str:
    """Format datetime for logging and display"""
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def parse_datetime(dt_str: str) -> Optional[datetime]:
    """Parse datetime string safely"""
    try:
        return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return None

def retry_operation(func, max_retries: int = 3, delay: float = 1.0, logger: Optional[logging.Logger] = None):
    """Retry operation with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if logger:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
            
            if attempt == max_retries - 1:
                raise e
            
            time.sleep(delay * (2 ** attempt))
    
    return None

def validate_file_path(file_path: str) -> bool:
    """Validate if file path exists and is accessible"""
    return os.path.exists(file_path) and os.path.isfile(file_path)

def validate_directory_path(dir_path: str) -> bool:
    """Validate if directory path exists and is accessible"""
    return os.path.exists(dir_path) and os.path.isdir(dir_path)

def create_order_summary(order_data: Dict[str, Any]) -> str:
    """Create a readable summary of order data"""
    ticket = order_data.get('ticket', 'N/A')
    symbol = order_data.get('symbol', 'N/A')
    order_type = order_data.get('type_name', 'N/A')
    volume = order_data.get('volume_initial', 0)
    price_open = order_data.get('price_open', 0)
    
    return f"Order {ticket}: {order_type} {volume} {symbol} @ {price_open}"

def calculate_price_difference(price1: float, price2: float) -> float:
    """Calculate absolute difference between two prices"""
    return abs(price1 - price2)

def is_price_changed(old_price: float, new_price: float, min_change: float = 1e-5) -> bool:
    """Check if price has changed significantly"""
    return calculate_price_difference(old_price, new_price) > min_change

def format_error_message(error: Exception, context: str = "") -> str:
    """Format error message with context"""
    error_msg = str(error)
    if context:
        return f"{context}: {error_msg}"
    return error_msg

def get_current_timestamp() -> str:
    """Get current timestamp as string"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def convert_mt5_time(mt5_time: int) -> datetime:
    """Convert MT5 timestamp to datetime object"""
    return datetime.fromtimestamp(mt5_time)

def convert_to_mt5_time(dt: datetime) -> int:
    """Convert datetime to MT5 timestamp"""
    return int(dt.timestamp())

def validate_symbol_mapping(symbol: str, mapping: Dict[str, str]) -> str:
    """Get mapped symbol or return original if no mapping exists"""
    return mapping.get(symbol, symbol)

def clean_symbol_name(symbol: str) -> str:
    """Clean and standardize symbol name"""
    return symbol.upper().strip().replace(' ', '')

def is_market_hours(symbol: str = None) -> bool:
    """Basic market hours check (can be enhanced with specific symbol logic)"""
    # This is a basic implementation - can be enhanced with specific market hours
    current_time = datetime.now()
    weekday = current_time.weekday()
    
    # Basic forex market hours (Sunday 5 PM EST to Friday 5 PM EST)
    # This is simplified - real implementation would consider specific market hours
    if weekday == 6:  # Sunday
        return current_time.hour >= 17
    elif weekday == 5:  # Saturday
        return current_time.hour < 17
    else:  # Monday to Friday
        return True

def format_volume(volume: float) -> str:
    """Format volume for display"""
    return f"{volume:.2f}"

def format_price_display(price: float, digits: int = 5) -> str:
    """Format price for display"""
    return f"{price:.{digits}f}"

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values"""
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / old_value) * 100

def truncate_string(text: str, max_length: int = 100) -> str:
    """Truncate string to maximum length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def safe_dict_get(dictionary: Dict, key: str, default: Any = None) -> Any:
    """Safely get value from dictionary with default"""
    return dictionary.get(key, default)

def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """Merge two dictionaries, with dict2 values taking precedence"""
    result = dict1.copy()
    result.update(dict2)
    return result

def filter_none_values(data: Dict) -> Dict:
    """Remove None values from dictionary"""
    return {k: v for k, v in data.items() if v is not None}

def ensure_directory_exists(directory_path: str) -> bool:
    """Ensure directory exists, create if it doesn't"""
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception:
        return False