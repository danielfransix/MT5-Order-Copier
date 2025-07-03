# MT5 Pending Order Copier System - Feature Specifications

## Overview

The MT5 Pending Order Copier is a system designed to copy pending orders from a source MT5 terminal to multiple target MT5 terminals. The system operates on a run-based synchronization model (not real-time), where it connects to terminals sequentially, performs synchronization tasks, and then disconnects. It can run once or be scheduled to run at specified intervals.

## Core Concept

The system uses the **source order's ticket ID as the magic number** for copied orders on target terminals. This creates a direct, stateless relationship that eliminates the need for external databases or mapping files while ensuring reliable order tracking and synchronization.

## System Architecture

### Multi-Terminal Setup
- **Source Terminal**: The MT5 terminal where original pending orders are placed
- **Target Terminals**: Multiple MT5 terminals that receive copies of source orders
- **One-Process-Per-Terminal**: Each MT5 connection requires a separate Python process due to MT5 API limitations

### Order Relationship Model
```
Source Order (Ticket: 12345) → Target Order A (Magic: 12345)
                             → Target Order B (Magic: 12345)
                             → Target Order C (Magic: 12345)
```

## Core Features

### 1. Order Discovery and Copying

**Capabilities:**
- Automatically detect new pending orders on source terminal
- Copy orders to all configured target terminals
- Apply lot size multipliers per target terminal
- Handle symbol mapping between different brokers
- Support all pending order types (BUY_LIMIT, SELL_LIMIT, BUY_STOP, SELL_STOP, BUY_STOP_LIMIT, SELL_STOP_LIMIT)

**Order Matching Logic:**
- System retrieves all pending orders from source terminal
- For each target terminal, retrieves all pending orders
- Matches target orders to source orders using magic number = source ticket ID
- Identifies new source orders that don't have corresponding target orders
- Creates new orders on target terminals for unmatched source orders

### 2. Order Synchronization and Updates

**Run-Based Synchronization:**
- Check source orders for parameter changes during each run
- Detect modifications to: entry price, stop loss, take profit, expiration time
- Update corresponding target orders when source changes detected during run
- Maintain proportional relationships (e.g., lot sizes based on multipliers)

**Change Detection:**
- Compare current source order parameters with last known state
- Generate modification requests for target orders when discrepancies found
- Handle partial modifications (e.g., only stop loss changed)

### 3. Orphaned Order Management

**Orphan Detection:**
- Identify target orders whose magic numbers don't match any existing source ticket
- Occurs when source orders are filled, cancelled, or manually closed
- Track orphaned orders across multiple system runs

**Per-Terminal Orphan Policies:**
Orphan management settings are configured individually for each target terminal, allowing different policies per account.

```python
# Example per-terminal orphan configuration (within TARGET_TERMINALS)
'orphan_management': {
    'kill_orphaned_orders': True,  # Boolean: Auto-cancel orphans
    'orphan_check_interval': 300,  # Seconds: Interval between orphan checks
    'max_orphan_checks': 3,        # Integer: Number of checks before killing orphan
}
```

**Orphan Handling Logic:**
- **Kill Mode** (`kill_orphaned_orders: True`): Track orphan check count, kill after max checks reached
- **Preserve Mode** (`kill_orphaned_orders: False`): Leave orphaned orders untouched

### 4. Symbol Mapping System

**Cross-Broker Symbol Translation:**
- Handle different symbol naming conventions between brokers
- Support suffix/prefix variations (e.g., "EURUSD" vs "EURUSD.x" vs "EURUSDm")
- Configurable mapping rules per target terminal

**Mapping Configuration:**
```python
SYMBOL_MAPPING = {
    'target_terminal_1': {
        'EURUSD': 'EURUSD.x',
        'XAUUSD': 'GOLD',
        'BTCUSD': 'BITCOIN'
    },
    'target_terminal_2': {
        'EURUSD': 'EURUSDm',
        'XAUUSD': 'XAUUSDm'
    }
}
```

### 5. Lot Size Management

**Proportional Scaling:**
- Apply different lot multipliers for each target terminal
- Support fractional multipliers (e.g., 0.5x, 1.5x, 2.0x)
- Configurable minimum and maximum lot sizes per target terminal
- Handle micro/mini lot accounts automatically

### 6. Pending Order Type Filtering

**Per-Account Order Type Control:**
- Configure which pending order types each target account should accept
- Filter orders based on type before copying to target terminals
- Support all MT5 pending order types: BUY_LIMIT, SELL_LIMIT, BUY_STOP, SELL_STOP, BUY_STOP_LIMIT, SELL_STOP_LIMIT

**Configuration Example:**
```python
TARGET_TERMINALS = {
    'terminal_1': {
        'MT5_ACCOUNT': 12345,
        'MT5_PASSWORD': "password123",
        'MT5_SERVER': "Broker-Server",
        'MT5_TERMINAL_PATH': r"C:\Program Files\MT5\terminal64.exe",
        'lot_multiplier': 1.0,
        'min_lot_size': 0.01,
        'max_lot_size': 100.0,
        'allowed_order_types': ['BUY_LIMIT', 'SELL_LIMIT', 'BUY_STOP', 'SELL_STOP'],
        'symbol_mapping': {...},
        'orphan_management': {
            'kill_orphaned_orders': True,
            'orphan_check_interval': 300,
            'max_orphan_checks': 3
        },
        'max_pending_orders': {
            'enabled': True,
            'max_orders': 50
        }
    },
    'terminal_2': {
        'MT5_ACCOUNT': 67890,
        'MT5_PASSWORD': "password456",
        'MT5_SERVER': "Broker-Server-2",
        'MT5_TERMINAL_PATH': r"C:\Program Files\MT5_2\terminal64.exe",
        'lot_multiplier': 0.5,
        'min_lot_size': 0.1,
        'max_lot_size': 10.0,
        'allowed_order_types': ['BUY_LIMIT', 'SELL_LIMIT'],  # Only limit orders
        'symbol_mapping': {...},
        'orphan_management': {
            'kill_orphaned_orders': False,  # Different policy for this terminal
            'orphan_check_interval': 600,
            'max_orphan_checks': 5
        },
        'max_pending_orders': {
            'enabled': False  # No limit for this terminal
        }
    }
}
```

### 7. Maximum Pending Orders Limit

**Per-Terminal Order Count Management:**
- Set maximum number of allowed pending orders individually for each target terminal
- Reject new order copying if terminal-specific limit would be exceeded
- Configurable feature that can be enabled/disabled per terminal

**Per-Terminal Configuration:**
```python
# Example per-terminal max orders configuration (within TARGET_TERMINALS)
'max_pending_orders': {
    'enabled': True,    # Boolean: Enable/disable this feature for this terminal
    'max_orders': 50,   # Integer: Maximum pending orders allowed for this terminal
}
```

### 8. Error Handling and Recovery

**Connection Management:**
- Sequential terminal connections (connect → process → disconnect → next terminal)
- Graceful handling of terminal disconnections
- Proper cleanup of connections after each terminal

**Order Operation Failures:**
- Stop execution immediately upon encountering errors
- Provide clear error articulation without workaround attempts
- Graceful system shutdown with error details

### 9. Scheduled Execution Control

**Run Modes:**
- **Single Run Mode**: Execute once and stop
- **Scheduled Mode**: Run at specified intervals automatically
- **Configurable Toggle**: Enable/disable scheduled execution

**Configuration:**
```python
SCHEDULED_EXECUTION = {
    'enabled': False,          # Boolean: Enable scheduled runs
    'interval_seconds': 300,   # Integer: Seconds between runs (when enabled)
}
```

### 10. Configuration Management

**Python Configuration File:**
- Configuration stored in Python (.py) file for easy editing
- Environment-specific settings (demo vs live)
- Validation of configuration parameters on startup

**Configuration Structure:**
```python
# config.py

# Source Terminal Configuration
SOURCE_TERMINAL = {
    'MT5_ACCOUNT': 25178772,
    'MT5_PASSWORD': "wE&QH3)M{DpA",
    'MT5_SERVER': "Tickmill-Demo",
    'MT5_TERMINAL_PATH': r"C:\Program Files\Tickmill MT5 Terminal\terminal64.exe"
}

# Target Terminals Configuration
TARGET_TERMINALS = {
    'terminal_1': {
        'MT5_ACCOUNT': 12345,
        'MT5_PASSWORD': "password123",
        'MT5_SERVER': "Broker-Server",
        'MT5_TERMINAL_PATH': r"C:\Program Files\MT5\terminal64.exe",
        'lot_multiplier': 1.0,
        'min_lot_size': 0.01,
        'max_lot_size': 100.0,
        'allowed_order_types': ['BUY_LIMIT', 'SELL_LIMIT', 'BUY_STOP', 'SELL_STOP'],
        'symbol_mapping': {
            'EURUSD': 'EURUSD.x',
            'XAUUSD': 'GOLD'
        },
        'orphan_management': {
            'kill_orphaned_orders': True,
            'orphan_check_interval': 300,
            'max_orphan_checks': 3
        },
        'max_pending_orders': {
            'enabled': True,
            'max_orders': 50
        }
    }
}

# Scheduled Execution
SCHEDULED_EXECUTION = {
    'enabled': False,
    'interval_seconds': 300
}
```

## Operational Workflow

### System Startup
1. Load and validate configuration from Python file
2. Initialize system state tracking
3. Prepare for sequential terminal processing

### Main Processing Loop (Per Run)
1. **Source Terminal Phase**: 
   - Connect to source terminal
   - Retrieve all pending orders
   - Disconnect from source terminal

2. **Target Terminal Processing** (Sequential):
   For each target terminal:
   - Connect to target terminal
   - Retrieve existing pending orders
   - Match source orders to target orders via magic numbers
   - Apply order type filtering based on terminal's allowed_order_types
   - Check terminal's max pending orders limit (if enabled for this terminal)
   - Apply terminal's min/max lot size constraints
   - Copy new source orders (if within limits, allowed types, and lot constraints)
   - Update modified orders
   - Handle orphaned orders according to terminal's orphan management policy
   - Disconnect from target terminal

3. **Completion**: 
   - Update orphan check counters
   - Prepare for next run (if scheduled mode enabled)

### Shutdown Procedure
1. Complete current terminal processing
2. Ensure all connections are properly closed
3. Stop scheduled execution (if running)

## System Files Structure

The following files need to be created for the complete system, all residing in the same directory:

### Core System Files
1. **`config.py`** - Main configuration file containing all settings
2. **`main.py`** - Entry point and main execution controller
3. **`mt5_connector.py`** - MT5 connection and operation handler
4. **`order_manager.py`** - Order copying and synchronization logic
5. **`order_tracker.py`** - Orphan tracking and state management
6. **`scheduler.py`** - Scheduled execution controller (when enabled)
7. **`utils.py`** - Utility functions and helpers
8. **`requirements.txt`** - Python package dependencies

### Dependency Management
To avoid circular dependencies, the system follows this import hierarchy:
- `main.py` → imports `scheduler.py`, `order_manager.py`, `config.py`
- `scheduler.py` → imports `main.py` execution functions only
- `order_manager.py` → imports `mt5_connector.py`, `order_tracker.py`, `utils.py`
- `mt5_connector.py` → imports `utils.py` only
- `order_tracker.py` → imports `utils.py` only
- `utils.py` → no internal imports (only external libraries)
- `config.py` → no imports (pure configuration)

## Security Considerations

### Account Protection
- Configuration file contains sensitive account credentials
- Ensure proper file permissions on config.py

## System Characteristics

### Execution Model
- **Non-Real-Time**: System runs periodically, not continuously
- **Sequential Processing**: Connects to one terminal at a time
- **Stateless Between Runs**: Each run is independent
- **Graceful Error Handling**: Stops on errors with clear messages
- **Configurable Scheduling**: Can run once or on intervals

This specification provides the foundation for a reliable pending order copying system that maintains synchronization between multiple MT5 terminals through run-based execution, with flexible configuration options and intelligent error handling.