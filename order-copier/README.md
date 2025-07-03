# MT5 Pending Order Copier System

A robust, production-ready system for copying pending orders between MetaTrader 5 terminals with advanced features including order tracking, orphan management, and flexible execution modes.

## Table of Contents
- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation Guide](#installation-guide)
- [Quick Start Guide](#quick-start-guide)
- [Configuration](#configuration)
- [Usage](#usage)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Advanced Configuration](#advanced-configuration)

## Features

### Core Functionality
- **Pending Order Copying**: Automatically copy new pending orders from source to target terminals
- **Active Position Management**: Monitor and manage active positions that were created when copied pending orders get triggered
- **Multi-Terminal Support**: Copy orders from one source terminal to multiple target terminals
- **Real-time Synchronization**: Continuously monitor for new pending orders and position changes

## How It Works

### System Overview

The MT5 Order Copier is designed to handle two distinct types of trading instruments:

1. **Pending Orders**: Orders waiting to be triggered (BUY_LIMIT, SELL_LIMIT, BUY_STOP, SELL_STOP)
2. **Active Positions**: Live trades that resulted from triggered pending orders

### Detailed Workflow

#### Phase 1: Pending Order Management
1. **Source Monitoring**: Continuously monitors the source terminal for new pending orders
2. **Order Analysis**: Identifies new pending orders that haven't been copied yet
3. **Target Processing**: For each target terminal:
   - Maps symbols according to `symbol_mapping` configuration
   - Adjusts lot sizes using `lot_multiplier` settings
   - Applies `min_lot_size` and `max_lot_size` constraints
   - Filters orders based on `allowed_order_types`
4. **Order Copying**: Places equivalent pending orders on target terminals
5. **State Tracking**: Records the relationship between source and target orders

#### Phase 2: Active Position Management
1. **Trigger Detection**: Monitors when pending orders get triggered and become active positions
2. **Position Tracking**: Tracks active positions that originated from copied pending orders
3. **Lifecycle Management**: Continues monitoring until positions are closed on the source
4. **Synchronization**: Ensures target positions remain aligned with source position status

#### Phase 3: Orphan Management
1. **Orphan Detection**: Identifies orders/positions on targets that no longer exist on source
2. **Cleanup Actions**: Based on `orphan_management.kill_orphaned_orders` setting:
   - `True`: Automatically closes orphaned orders/positions
   - `False`: Logs orphans for manual review
3. **Safety Checks**: Performs multiple verification cycles before taking action

### Important Behavioral Notes

**What the System DOES:**
- ✅ **Copies New Pending Orders**: Copies `BUY_LIMIT`, `SELL_LIMIT`, `BUY_STOP`, and `BUY_STOP_LIMIT` orders from the source to one or more target terminals.
- ✅ **Updates Modified Pending Orders**: If a pending order on the source terminal is modified (e.g., price, stop-loss, take-profit, or expiration is changed), the system will update the corresponding order on the target terminals.
- ✅ **Synchronizes Position SL/TP**: When a copied pending order becomes an active position, the system monitors the source position and synchronizes any changes to its Stop Loss (SL) and Take Profit (TP) to the target positions.
- ✅ **Manages Orphaned Orders and Positions**: Detects and handles orders and positions on target terminals that no longer have a corresponding entry on the source terminal. Depending on the configuration, it can automatically cancel/close them.
- ✅ **Applies Risk Management**: Uses flexible position sizing (lot multiplier, min/max lot size), symbol mapping, and order type filtering for each target terminal.
- ✅ **Tracks State Persistently**: Saves the state of all copied orders and positions, allowing it to resume tracking correctly after a restart.

**What the System DOES NOT DO:**
- ❌ **Copy Active Positions**: It does not copy positions that are already active on the source terminal. It only manages positions that originate from a copied pending order.
- ❌ **Copy Market Orders**: It does not copy trades that are executed manually as market orders.

### State Persistence

The system maintains a persistent state file (`data/order_tracker_state.json`) that stores:
- Mapping between source and target orders
- Order status and lifecycle information
- Position tracking data
- System statistics and performance metrics

This ensures that if the system restarts, it can resume monitoring existing copied orders and positions without duplication or loss of tracking.

### Order and Position Handling
- **Pending Orders**: The system copies BUY_LIMIT, SELL_LIMIT, BUY_STOP, SELL_STOP orders
- **Active Positions**: When a copied pending order gets triggered and becomes an active position, the system tracks and manages it
- **Position Lifecycle**: Monitors active positions until they are closed on the source terminal
- **Orphan Management**: Handles orders/positions that exist on targets but not on source

### Configuration and Safety
- **Flexible Position Sizing**: Configure lot multipliers for each target terminal
- **Symbol Mapping**: Map different symbol names between brokers
- **Order Type Filtering**: Choose which order types to copy for safety
- **Risk Management**: Set maximum lot sizes, order limits, and position limits
- **State Persistence**: Maintains complete order and position tracking across system restarts

### Execution and Monitoring
- **Multiple Execution Modes**: Run once, scheduled, or continuous operation
- **Comprehensive Logging**: Detailed logging with rotation and multiple levels
- **Built-in Testing**: Comprehensive test suite for validation
- **Statistics Tracking**: Real-time monitoring of system performance

## System Requirements

### Prerequisites
- **Operating System**: Windows 10/11 (required for MetaTrader 5)
- **Python**: 3.7 or higher (3.9+ recommended)
- **MetaTrader 5**: Latest version installed
- **Memory**: Minimum 4GB RAM (8GB+ recommended for multiple terminals)
- **Storage**: At least 1GB free space for logs and state files

### Required Dependencies
The system requires the following Python packages (automatically installed via `requirements.txt`):

- **MetaTrader5** (>=5.0.45) - Core MT5 API for terminal communication
- **schedule** (>=1.2.0) - Task scheduling for automated execution
- **pandas** (>=1.5.0) - Data manipulation and analysis
- **numpy** (>=1.21.0) - Numerical computing support
- **pyyaml** (>=6.0) - Configuration file parsing
- **python-dateutil** (>=2.8.0) - Enhanced date/time handling
- **psutil** (>=5.9.0) - System and process monitoring

## Installation Guide

### Step 1: Download the System

**Option A: Clone from Repository**
```bash
git clone <repository-url>
cd mt5-order-copier
```

**Option B: Download ZIP**
1. Download the ZIP file from the repository
2. Extract to your desired directory
3. Open Command Prompt/PowerShell in the extracted folder

### Step 2: Set Up Python Environment

**Check Python Installation:**
```bash
python --version
```
If Python is not installed, download from [python.org](https://python.org)

**Create Virtual Environment (Recommended):**
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Verify Installation:**
```bash
python test_imports.py
```

### Step 4: Prepare MetaTrader 5 Terminals

1. **Install MT5**: Download from your broker or [MetaQuotes](https://www.metatrader5.com)
2. **Enable Algorithmic Trading**:
   - Open MT5 → Tools → Options → Expert Advisors
   - Check "Allow algorithmic trading"
   - Check "Allow DLL imports"
3. **Test Manual Connections**: Ensure you can manually log into all terminals

## Quick Start Guide

### Step 1: Create Configuration File

```bash
copy config_sample.py config.py
```

### Step 2: Edit Basic Settings

Open `config.py` and modify the essential settings:

```python
# Source terminal (where orders originate)
SOURCE_TERMINAL = {
    'login': 12345678,                    # Your MT5 account number
    'password': 'your_password',          # Your MT5 password
    'server': 'YourBroker-Demo',         # Your broker's server
    'path': r'C:\Program Files\MetaTrader 5\terminal64.exe'
}

# Target terminal (where orders are copied)
TARGET_TERMINALS = {
    'MyTargetAccount': {
        'login': 87654321,
        'password': 'target_password',
        'server': 'TargetBroker-Demo',
        'path': r'C:\Program Files\MetaTrader 5\terminal64.exe',
        'lot_multiplier': 1.0,            # Same lot size as source
        'symbol_mapping': {
            'EURUSD': 'EURUSD',           # Direct symbol mapping
            'GBPUSD': 'GBPUSD'
        }
    }
}
```

### Step 3: Test Configuration

```bash
python test_config.py
```

### Step 4: Run System Test

```bash
python test_system.py
```

### Step 5: Start the System

**One-time execution:**
```bash
python main.py
```

**Continuous monitoring:**
Edit `config.py` to set:
```python
ENABLE_SCHEDULING = False
ENABLE_CONTINUOUS_MODE = True
```
Then run:
```bash
python main.py
```

## Configuration

### Configuration File Structure

The system uses a Python configuration file (`config.py`) with the following main sections:

- **SOURCE_TERMINAL**: The MT5 terminal from which orders are copied
- **TARGET_TERMINALS**: Dictionary of target terminals where orders are copied to
- **ENABLE_SCHEDULING**: Enable Claude-style scheduled execution
- **ENABLE_CONTINUOUS_MODE**: Enable continuous execution mode
- **LOGGING_CONFIG**: Logging settings and output options
- **SYSTEM_CONFIG**: Global system settings and constraints

### Basic Configuration Example

Edit `config.py` to configure your terminals and settings:

```python
# =============================================================================
# SOURCE TERMINAL CONFIGURATION
# =============================================================================
SOURCE_TERMINAL = {
    'login': 12345678,                                              # Your MT5 account number
    'password': 'your_source_password',                             # Your MT5 password
    'server': 'YourBroker-Demo',                                   # Broker server name
    'path': r'C:\Program Files\MetaTrader 5\terminal64.exe',       # Path to MT5 executable
    'timeout': 10000                                               # Connection timeout (ms)
}

# =============================================================================
# TARGET TERMINALS CONFIGURATION
# =============================================================================
TARGET_TERMINALS = {
    'MyTargetAccount': {
        # Connection settings
        'login': 87654321,
        'password': 'target_password',
        'server': 'TargetBroker-Demo',
        'path': r'C:\Program Files\MetaTrader 5\terminal64.exe',
        'timeout': 10000,
        
        # Position sizing
        'lot_multiplier': 1.0,                                     # Same size as source
        'min_lot_size': 0.01,                                      # Minimum lot size
        'max_lot_size': 100.0,                                     # Maximum lot size
        
        # Order filtering
        'allowed_order_types': [
            'BUY_LIMIT', 'SELL_LIMIT', 'BUY_STOP', 'SELL_STOP'
        ],
        
        # Symbol mapping
        'symbol_mapping': {
            'EURUSD': 'EURUSD',
            'GBPUSD': 'GBPUSD'
        },
        
        # Orphan management (applies to both pending orders and active positions)
        'orphan_management': {
            'kill_orphaned_orders': True,           # Auto-close orphaned orders/positions
            'max_orphan_checks': 3                  # Verification cycles before action
        },
        
        # Order limits
        'max_pending_orders': {
            'enabled': True,
            'max_orders': 50
        }
    }
}

# =============================================================================
# EXECUTION CONFIGURATION (Claude-style)
# =============================================================================
ENABLE_SCHEDULING = False          # Enable scheduled execution
ENABLE_CONTINUOUS_MODE = True      # Enable continuous execution

# Scheduling parameters (when ENABLE_SCHEDULING = True)
SCHEDULE_TIMEFRAME = 'M5'         # M1, M5, M15, M30, H1, H4, D1
SCHEDULE_OFFSET_SECONDS = 60       # Offset from timeframe boundary

# Continuous mode parameters (when ENABLE_CONTINUOUS_MODE = True)
CONTINUOUS_DELAY_SECONDS = 5       # Delay between iterations
CONTINUOUS_MAX_RUNTIME_HOURS = 0   # 0 = unlimited

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
LOGGING_CONFIG = {
    'level': 'INFO',                                               # DEBUG, INFO, WARNING, ERROR
    'file_path': 'logs/mt5_order_copier.log',                     # Log file location
    'max_file_size': 10,                                          # MB before rotation
    'backup_count': 5,                                            # Number of backup files
    'console_output': True                                        # Also log to console
}
```

### Configuration Examples for Different Scenarios

#### Example 1: Conservative Risk Management

```python
TARGET_TERMINALS = {
    'ConservativeAccount': {
        'login': 87654321,
        'password': 'password',
        'server': 'Broker-Demo',
        'path': r'C:\MT5\terminal64.exe',
        
        # Conservative position sizing
        'lot_multiplier': 0.1,          # Only 10% of source position
        'min_lot_size': 0.01,
        'max_lot_size': 1.0,            # Cap at 1 lot maximum
        
        # Only limit orders (safer)
        'allowed_order_types': ['BUY_LIMIT', 'SELL_LIMIT'],
        
        # Strict order limits
        'max_pending_orders': {
            'enabled': True,
            'max_orders': 5             # Maximum 5 pending orders
        },
        
        # Conservative orphan handling
        'orphan_management': {
            'kill_orphaned_orders': False,  # Keep orphans for manual review
            'max_orphan_checks': 5
        }
    }
}
```

#### Example 2: Multiple Brokers with Symbol Mapping

```python
TARGET_TERMINALS = {
    'BrokerA_Account': {
        'login': 11111111,
        'password': 'password_a',
        'server': 'BrokerA-Live',
        'path': r'C:\MT5_BrokerA\terminal64.exe',
        'lot_multiplier': 0.5,
        
        # BrokerA uses standard symbols
        'symbol_mapping': {
            'EURUSD': 'EURUSD',
            'GBPUSD': 'GBPUSD',
            'USDJPY': 'USDJPY',
            'GOLD': 'XAUUSD'
        }
    },
    
    'BrokerB_Account': {
        'login': 22222222,
        'password': 'password_b',
        'server': 'BrokerB-Live',
        'path': r'C:\MT5_BrokerB\terminal64.exe',
        'lot_multiplier': 0.3,
        
        # BrokerB uses different symbol naming
        'symbol_mapping': {
            'EURUSD': 'EURUSD.m',       # Micro account suffix
            'GBPUSD': 'GBPUSD.m',
            'USDJPY': 'USDJPY.m',
            'GOLD': 'GOLD.spot'         # Different gold symbol
        }
    }
}
```

#### Example 3: Scheduled Execution (Claude-style)

```python
# Run on M5 timeframe with 60-second offset
ENABLE_SCHEDULING = True
ENABLE_CONTINUOUS_MODE = False

SCHEDULE_TIMEFRAME = 'M5'           # Execute every 5 minutes
SCHEDULE_OFFSET_SECONDS = 60        # 60 seconds after each 5-minute boundary
```

#### Example 4: Continuous Monitoring (Claude-style)

```python
# Run continuously with minimal delay
ENABLE_SCHEDULING = False
ENABLE_CONTINUOUS_MODE = True

CONTINUOUS_DELAY_SECONDS = 5         # 5-second delay between cycles
CONTINUOUS_MAX_RUNTIME_HOURS = 0     # 0 = unlimited runtime
```

### Execution Modes (Claude-style)

#### Single Run Mode
Run the copying process once and exit (when both modes are disabled):
```python
ENABLE_SCHEDULING = False
ENABLE_CONTINUOUS_MODE = False
```

#### Scheduled Mode
Run on Claude-style timeframe schedule:
```python
ENABLE_SCHEDULING = True
ENABLE_CONTINUOUS_MODE = False
SCHEDULE_TIMEFRAME = 'M5'        # M1, M5, M15, M30, H1, H4, D1
SCHEDULE_OFFSET_SECONDS = 60     # Offset from timeframe boundary
```

#### Continuous Mode
Run continuously with configurable delay:
```python
ENABLE_SCHEDULING = False
ENABLE_CONTINUOUS_MODE = True
CONTINUOUS_DELAY_SECONDS = 5         # Delay between iterations
CONTINUOUS_MAX_RUNTIME_HOURS = 0     # 0 = unlimited
```

### Logging Configuration

```python
LOGGING_CONFIG = {
    'level': 'INFO',                                               # DEBUG, INFO, WARNING, ERROR, CRITICAL
    'file_path': 'logs/mt5_order_copier.log',                     # Path to the log file
    'max_file_size': 10,                                          # Maximum size of the log file in MB before rotation
    'backup_count': 5,                                            # Number of backup log files to keep
    'console_output': True,                                       # Whether to output logs to the console
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # Log message format
}
```

### System Configuration

```python
SYSTEM_CONFIG = {
    'connection_timeout': 90,      # Integer: Maximum time in seconds to wait for a connection to the MT5 terminal.
    'max_retries': 5,              # Integer: Maximum number of times to retry an operation (e.g., connection, order placement) on failure.
    'retry_delay': 5,              # Integer/Float: Delay in seconds between retries.
    'log_level': 'INFO',           # DEPRECATED: Use LOGGING_CONFIG['level'] instead.
    'log_file': 'mt5_copier.log'   # DEPRECATED: Use LOGGING_CONFIG['file_path'] instead.
}
```

## Testing

### Pre-Flight Checks

Before running the system with real accounts, perform these essential tests:

#### 1. Import Test
```bash
python test_imports.py
```
Verifies all required modules are properly installed.

#### 2. Configuration Test
```bash
python test_config.py
```
Validates your configuration file for syntax and logical errors.

#### 3. System Test
```bash
python test_system.py
```
Runs comprehensive unit tests for all system components.

#### 4. Connection Test
Create a minimal test configuration with demo accounts:

```python
# test_connection_config.py
SOURCE_TERMINAL = {
    'login': 12345678,
    'password': 'demo_password',
    'server': 'YourBroker-Demo',
    'path': r'C:\Program Files\MetaTrader 5\terminal64.exe'
}

TARGET_TERMINALS = {
    'TestTarget': {
        'login': 87654321,
        'password': 'demo_password',
        'server': 'YourBroker-Demo',
        'path': r'C:\Program Files\MetaTrader 5\terminal64.exe',
        'lot_multiplier': 0.01,  # Very small lots for testing
        'symbol_mapping': {'EURUSD': 'EURUSD'}
    }
}

ENABLE_SCHEDULING = False
ENABLE_CONTINUOUS_MODE = False
```

Then test:
```bash
python main.py test_connection_config.py
```

### Testing Checklist

- [ ] Python environment setup correctly
- [ ] All dependencies installed
- [ ] MT5 terminals can connect manually
- [ ] Configuration file syntax is valid
- [ ] Demo account connections work
- [ ] System can retrieve orders from source
- [ ] System can place test orders on target
- [ ] Logging system works properly
- [ ] State tracking files are created

## Usage

### Command Line Options

```bash
# Run with default configuration
python main.py

# Run with custom configuration file
python main.py custom_config.py

# Run in test mode (dry run)
python main.py --test-mode

# Show help and available options
python main.py --help

# Run with verbose logging
python main.py --verbose
```

### Execution Modes (Updated)

#### Single Run Mode (Default)
Runs the copying process once and exits:
```python
ENABLE_SCHEDULING = False
ENABLE_CONTINUOUS_MODE = False
```

#### Scheduled Mode
Runs on Claude-style timeframe schedule:
```python
ENABLE_SCHEDULING = True
ENABLE_CONTINUOUS_MODE = False
SCHEDULE_TIMEFRAME = 'M1'        # M1, M5, M15, M30, H1, H4, D1
SCHEDULE_OFFSET_SECONDS = 60     # Offset from timeframe boundary
```

#### Continuous Mode
Runs continuously with configurable delay:
```python
ENABLE_SCHEDULING = False
ENABLE_CONTINUOUS_MODE = True
CONTINUOUS_DELAY_SECONDS = 5         # Delay between iterations
CONTINUOUS_MAX_RUNTIME_HOURS = 0     # 0 = unlimited runtime
```

### Running as Windows Service

For production use, you can run the system as a Windows service:

1. Install the service wrapper:
```bash
pip install pywin32
```

2. Create a service script (see documentation for details)

3. Install and start the service:
```bash
python service_installer.py install
python service_installer.py start
```

### Safety and Best Practices

⚠️ **IMPORTANT SAFETY GUIDELINES** ⚠️

1. **Always Test with Demo Accounts First**
   - Never run the system on live accounts without thorough testing
   - Use demo accounts that mirror your live account setup
   - Test all scenarios: new orders, modifications, cancellations

2. **Start Small**
   - Begin with very small lot multipliers (0.01 or 0.1)
   - Limit the number of target terminals initially
   - Monitor the system closely during initial runs

3. **Risk Management**
   ```python
   # Conservative settings for beginners
   'lot_multiplier': 0.1,        # Only 10% of source position
   'max_lot_size': 1.0,          # Cap maximum position size
   'max_pending_orders': {
       'enabled': True,
       'max_orders': 10          # Limit total orders
   }
   ```

4. **Monitor Continuously**
   - Check log files regularly
   - Monitor account balances
   - Set up alerts for errors
   - Have a manual override plan

### Terminal Configuration

1. **Ensure MT5 terminals are properly configured**:
   - Enable algorithmic trading
   - Configure login credentials
   - Test manual connections

2. **Configure symbol mappings** if using different brokers:
   ```python
   'symbol_mapping': {
       'EURUSD.m': 'EURUSD',  # Source -> Target
       'GBPUSD.m': 'GBPUSD'
   }
   ```

3. **Set appropriate lot multipliers**:
   ```python
   'lot_multiplier': 0.5,  # Copy with half the lot size
   'min_lot_size': 0.01,
   'max_lot_size': 10.0
   ```

### Order Type Filtering

Control which order types are copied:

```python
'allowed_order_types': [
    'BUY_LIMIT',
    'SELL_LIMIT',
    'BUY_STOP',
    'SELL_STOP',
    'BUY_STOP_LIMIT',
    'SELL_STOP_LIMIT'
]
```

### Orphan Management

Configure how orphaned orders are handled:

```python
'orphan_management': {
    'kill_orphaned_orders': True,    # Enable orphan killing
    'max_orphan_checks': 3           # Checks before killing
}
```

## System Architecture

### Core Components

1. **main.py**: Application entry point and execution control
2. **config.py**: Configuration management and validation
3. **order_manager.py**: Core order copying and synchronization logic
4. **mt5_connector.py**: MT5 terminal connection and operations
5. **order_tracker.py**: Order state tracking and orphan management
6. **utils.py**: Utility functions and helpers

### Data Flow

1. **Source Connection**: Connect to source terminal and retrieve pending orders
2. **Target Processing**: For each target terminal:
   - Connect and retrieve existing orders
   - Identify new orders to copy
   - Detect modified orders to update
   - Handle orphaned orders
3. **State Management**: Update tracking state and save to disk
4. **Statistics**: Log processing statistics and performance metrics

### State Persistence

The system maintains persistent state in `data/order_tracker_state.json`:
- Source order tracking
- Target order relationships
- Orphan check counters
- Terminal activity status

## Troubleshooting

### Log Files and Monitoring

Logs are written to the configured log file (default: `logs/mt5_order_copier.log`):

```
2024-01-15 10:30:15,123 - INFO - Starting order copying process for all terminals
2024-01-15 10:30:16,456 - INFO - Retrieved 5 orders from source terminal
2024-01-15 10:30:17,789 - INFO - Successfully copied order 123456 to Terminal1 as 789012
2024-01-15 10:30:18,012 - INFO - Processing statistics: 3 copied, 1 updated, 0 cancelled
```

### Common Setup Issues

#### 1. Python Installation Problems

**Error**: `'python' is not recognized as an internal or external command`

**Solutions**:
- Install Python from [python.org](https://python.org)
- During installation, check "Add Python to PATH"
- Restart Command Prompt after installation
- Try `py` instead of `python`

#### 2. Dependency Installation Issues

**Error**: `pip install failed` or `ModuleNotFoundError`

**Solutions**:
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install with verbose output to see errors
pip install -r requirements.txt -v

# Install packages individually if batch fails
pip install MetaTrader5>=5.0.45
pip install schedule>=1.2.0
pip install pandas>=1.5.0
```

#### 3. MetaTrader5 Module Issues

**Error**: `ImportError: No module named 'MetaTrader5'`

**Solutions**:
- Ensure you're on Windows (MT5 API only works on Windows)
- Install the official MetaTrader5 package:
```bash
pip uninstall MetaTrader5
pip install MetaTrader5
```
- Verify MT5 terminal is installed

#### 4. Configuration File Errors

**Error**: `SyntaxError` or `NameError` in config.py

**Solutions**:
- Copy from `config_sample.py` again
- Check for missing quotes around strings
- Verify proper Python dictionary syntax
- Use raw strings for file paths: `r'C:\path\to\file'`

### Connection Issues

#### 1. MT5 Terminal Connection Failed

**Error**: `Failed to initialize MT5` or `Login failed`

**Diagnostic Steps**:
```bash
# Test manual connection first
1. Open MT5 terminal manually
2. Try logging in with your credentials
3. Verify server name exactly matches
```

**Solutions**:
- **Check Credentials**: Verify login, password, and server name
- **Enable Algo Trading**: Tools → Options → Expert Advisors → Allow algorithmic trading
- **Check Terminal Path**: Verify the path to terminal64.exe is correct
- **Close Other Connections**: Ensure MT5 isn't already connected elsewhere
- **Firewall/Antivirus**: Add MT5 and Python to firewall exceptions

#### 2. Multiple Terminal Issues

**Error**: `Terminal already in use` or `Connection timeout`

**Solutions**:
- Use different MT5 installations for different accounts
- Install MT5 in separate folders:
  ```
  C:\MT5_Source\terminal64.exe
  C:\MT5_Target1\terminal64.exe
  C:\MT5_Target2\terminal64.exe
  ```
- Increase timeout values in configuration
- Stagger connection attempts

### Order Copying Issues

#### 1. Orders Not Being Copied

**Diagnostic Steps**:
1. Check if source has pending orders:
   ```bash
   python -c "from mt5_connector import MT5Connector; print('Testing source connection')"
   ```
2. Verify symbol mappings are correct
3. Check order type filters
4. Review lot size constraints

**Solutions**:
- **Symbol Mapping**: Ensure source symbols map to valid target symbols
- **Order Types**: Verify allowed_order_types includes the order types you want
- **Lot Sizes**: Check min_lot_size and max_lot_size constraints
- **Account Permissions**: Verify target account allows pending orders

#### 2. Symbol Mapping Errors

**Error**: `Symbol not found` or `Invalid symbol`

**Solutions**:
```python
# Check available symbols on target terminal
'symbol_mapping': {
    'EURUSD.m': 'EURUSD',     # Suffix mapping
    'EUR/USD': 'EURUSD',      # Format conversion
    'GOLD': 'XAUUSD'          # Different naming
}
```

#### 3. Lot Size Issues

**Error**: `Invalid lot size` or `Lot size out of range`

**Solutions**:
```python
# Adjust lot size settings
'lot_multiplier': 0.1,        # Reduce position size
'min_lot_size': 0.01,         # Broker minimum
'max_lot_size': 1.0,          # Conservative maximum
```

### Performance Issues

#### 1. Slow Execution

**Solutions**:
- Increase execution intervals
- Reduce log verbosity to INFO or WARNING
- Monitor system resources
- Check network latency to broker servers

#### 2. Memory Usage

**Solutions**:
- Limit number of target terminals
- Reduce log file retention
- Monitor with Task Manager
- Restart system periodically

### Advanced Troubleshooting

#### Enable Debug Logging

Edit `config.py`:
```python
LOGGING_CONFIG = {
    'level': 'DEBUG',  # Change from INFO to DEBUG
    'console_output': True
}
```

#### Manual Testing

Test individual components:
```bash
# Test MT5 connection only
python -c "from mt5_connector import MT5Connector; c = MT5Connector(); print(c.connect(SOURCE_TERMINAL, 'Test'))"

# Test configuration loading
python -c "from config import load_config; print(load_config())"

# Test order retrieval
python -c "from order_manager import OrderManager; om = OrderManager(config); print(len(om._get_source_orders()))"
```

### Frequently Asked Questions (FAQ)

### General Questions

**Q: Can I copy orders from one broker to multiple brokers?**
A: Yes, you can configure multiple target terminals in the `TARGET_TERMINALS` dictionary. Each target can have different settings, lot multipliers, and symbol mappings.

**Q: Does this work with live accounts?**
A: Yes, but we strongly recommend testing thoroughly with demo accounts first. Start with small lot sizes and conservative settings when moving to live accounts.

**Q: Can I copy orders between different MT5 installations?**
A: Yes, you can specify different MT5 installation paths for each terminal in the configuration.

**Q: What happens if my internet connection is lost?**
A: The system will attempt to reconnect based on the timeout settings. Pending orders that were already placed will remain, but new orders won't be copied until connection is restored.

### Technical Questions

**Q: Why are my orders not being copied?**
A: Common causes:
- Source terminal not connected
- Target terminal login issues
- Symbol not available on target broker
- Order type not in `allowed_order_types`
- Lot size outside min/max limits
- Maximum pending orders limit reached

**Q: Can I modify the lot size of copied orders?**
A: Yes, use the `lot_multiplier` setting. For example, `0.5` will copy orders at half the original size, `2.0` will double them.

**Q: How do I handle different symbol names between brokers?**
A: Use the `symbol_mapping` configuration:
```python
'symbol_mapping': {
    'EURUSD': 'EURUSD.m',    # Source: Target
    'GOLD': 'XAUUSD'         # Map GOLD to XAUUSD
}
```

**Q: What are orphaned orders and positions?**
A: Orphans are orders or positions that exist on target terminals but no longer have corresponding orders/positions on the source terminal. This can happen when:
- Source pending orders are manually cancelled
- Source positions are manually closed
- Connection issues cause synchronization problems
The system can automatically remove these if `kill_orphaned_orders` is enabled.

**Q: Can I filter which order types to copy?**
A: Yes, use the `allowed_order_types` setting to specify which order types should be copied (e.g., only limit orders for safety). This only applies to pending orders - active positions are managed regardless of their original order type.

**Q: Does the system copy existing active positions?**
A: No, the system only copies new pending orders. However, it will track and manage active positions that result from previously copied pending orders getting triggered.

**Q: What happens when a copied pending order gets triggered?**
A: When a pending order becomes an active position, the system automatically starts tracking that position. It will monitor the position until it's closed on the source terminal, and can manage orphaned positions if they're closed on source but remain open on targets.

**Q: Can I copy stop-loss and take-profit levels?**
A: The system copies the original pending order with its SL/TP levels. However, if you manually modify SL/TP levels after the order is placed, those modifications are not automatically copied to target terminals.

### Safety Questions

**Q: Is it safe to run this on live accounts?**
A: The system is designed with safety in mind, but you should:
- Test thoroughly on demo accounts
- Start with small lot sizes
- Use conservative risk management settings
- Monitor the system closely
- Have stop-loss and take-profit levels set

**Q: What if the system places too many orders?**
A: Use the `max_pending_orders` setting to limit the number of pending orders. The system will stop copying new orders when this limit is reached.

**Q: Can I stop the system immediately?**
A: Yes, press `Ctrl+C` to stop the system gracefully. It will finish processing current operations and save state before exiting.

### Performance Questions

**Q: How often does the system check for new orders?**
A: This depends on the execution mode:
- `once`: Runs once and exits
- `scheduled`: Runs at specified intervals (configurable)
- `continuous`: Runs continuously with minimal delay (configurable)

**Q: Does the system use a lot of system resources?**
A: No, the system is lightweight and designed for minimal resource usage. It only connects to MT5 when needed and uses efficient polling.

**Q: Can I run multiple instances?**
A: Yes, but ensure each instance uses different configuration files and log files to avoid conflicts.

### Troubleshooting Questions

**Q: I get "Terminal not found" errors. What should I do?**
A: Check that:
- MT5 is installed and the path in config is correct
- MT5 terminal is not already running
- You have proper permissions to access the MT5 installation

**Q: Orders are copied but with wrong lot sizes. Why?**
A: Check:
- `lot_multiplier` setting
- `min_lot_size` and `max_lot_size` limits
- Broker's minimum lot size requirements
- Account type (micro, mini, standard)

**Q: The system stops working after some time. What's wrong?**
A: Common causes:
- MT5 terminal disconnected from broker
- Network connectivity issues
- Broker server maintenance
- System running out of memory (check logs)

Check the log files for specific error messages.

### Getting Help

If you encounter issues:

1. **Check the FAQ section above** - Most common questions are answered there
2. **Review the troubleshooting section** - Step-by-step solutions for common problems
3. **Check log files** - Look at `logs/mt5_order_copier.log` for error messages
4. **Ensure all prerequisites are met** - Verify Python, MT5, and dependencies
5. **Test with demo accounts first** - Always validate your setup safely
6. **Contact support with**:
   - Error messages from logs
   - Configuration file (remove sensitive data)
   - System specifications
   - Steps to reproduce the issue

## Additional Resources

### Useful Commands Reference

```bash
# Quick system test
python main.py --test-mode

# Run with verbose logging
python main.py --verbose

# Check Python and dependencies
python --version
pip list | findstr MetaTrader5

# View recent logs
type logs\mt5_order_copier.log | more

# Check if MT5 is running
tasklist | findstr terminal64
```

### File Structure Reference

```
order-copier/
├── main.py                 # Main application entry point
├── config.py              # Your configuration file
├── config_sample.py       # Sample configuration template
├── requirements.txt       # Python dependencies
├── test_system.py         # System testing script
├── order_manager.py       # Core order management logic
├── mt5_connector.py       # MT5 connection handling
├── order_tracker.py       # Order state tracking
├── utils.py              # Utility functions
├── logs/                 # Log files directory
│   └── mt5_order_copier.log
├── data/                 # System state files
│   └── order_tracker_state.json
└── README.md             # This documentation
```

### Configuration Quick Reference

#### Order and Position Management Settings

| Setting | Purpose | Example | Applies To |
|---------|---------|----------|------------|
| `lot_multiplier` | Scale position sizes | `0.5` (half size), `2.0` (double) | Both orders & positions |
| `min_lot_size` | Minimum lot size limit | `0.01` | Both orders & positions |
| `max_lot_size` | Maximum lot size limit | `100.0` | Both orders & positions |
| `allowed_order_types` | Filter which order types to copy | `['BUY_LIMIT', 'SELL_LIMIT']` | Pending orders only |
| `symbol_mapping` | Map symbol names between brokers | `{'GOLD': 'XAUUSD'}` | Both orders & positions |
| `max_pending_orders` | Limit total pending orders | `{'enabled': True, 'max_orders': 10}` | Pending orders only |
| `kill_orphaned_orders` | Auto-close orphaned orders/positions | `True` or `False` | Both orders & positions |
| `max_orphan_checks` | Verification cycles before orphan action | `3` | Both orders & positions |

#### Key Configuration Concepts

**Pending Order Settings:**
- `allowed_order_types`: Controls which types of pending orders are copied from source
- `max_pending_orders`: Prevents excessive pending orders on target terminals

**Position Management Settings:**
- `lot_multiplier`: Applied when copying pending orders, affects resulting position size
- `min_lot_size`/`max_lot_size`: Enforced for both initial orders and resulting positions

**Orphan Management (Critical for Both):**
- `kill_orphaned_orders`: When `True`, automatically closes orders/positions that exist on target but not source
- `max_orphan_checks`: Number of verification cycles before taking orphan cleanup action

**Symbol Mapping (Universal):**
- Maps symbol names between different brokers for both pending orders and active positions
- Essential when brokers use different symbol naming conventions

## Summary for New Users

This MT5 Order Copier system automatically copies pending orders from one MetaTrader 5 terminal to one or more target terminals, and then manages the resulting active positions when those orders get triggered. Here's what you need to know to get started:

### ✅ **What You Need**
- Windows computer with Python 3.7+
- MetaTrader 5 installed
- MT5 accounts (demo recommended for testing)
- Basic understanding of trading concepts

### 🚀 **Quick Start Steps**
1. **Install Python** and required packages
2. **Download** this order copier system
3. **Copy** `config_sample.py` to `config.py`
4. **Edit** `config.py` with your MT5 account details
5. **Test** the system: `python main.py --test-mode`
6. **Run** the system: `python main.py`

### ⚠️ **Important Safety Notes**
- **Always test with demo accounts first**
- **Start with small lot sizes** (`lot_multiplier: 0.1`)
- **Use conservative settings** initially
- **Monitor the system** closely when running
- **Have proper risk management** in place

### 🔧 **Key Features**
- Copy orders between multiple brokers
- Automatic lot size scaling
- Symbol name mapping for different brokers
- Order type filtering for safety
- Orphaned order management
- Comprehensive logging and monitoring
- Flexible execution modes (once, scheduled, continuous)

### 📚 **Where to Get Help**
- Read the **FAQ section** for common questions
- Check the **Troubleshooting section** for problems
- Review **log files** for error details
- Test with the **built-in test mode**

Remember: This system is a powerful tool that can significantly impact your trading. Take time to understand all settings and test thoroughly before using with live accounts.

### Statistics and Monitoring

The system provides comprehensive statistics:

```python
# Access statistics programmatically
stats = order_manager.get_statistics()
print(f"Orders copied: {stats['processing_stats']['orders_copied']}")
print(f"Orders updated: {stats['processing_stats']['orders_updated']}")
print(f"Orders cancelled: {stats['processing_stats']['orders_cancelled']}")
```

## Advanced Configuration

### Custom Symbol Mapping

```python
'symbol_mapping': {
    # Forex pairs
    'EURUSD.m': 'EURUSD',
    'GBPUSD.m': 'GBPUSD',
    
    # Indices
    'US30.cash': 'US30',
    'SPX500.cash': 'SPX500',
    
    # Commodities
    'GOLD.spot': 'XAUUSD',
    'SILVER.spot': 'XAGUSD'
}
```

### Risk Management

```python
# Lot size constraints
'lot_multiplier': 0.1,      # Risk 10% of source position
'min_lot_size': 0.01,       # Minimum position size
'max_lot_size': 1.0,        # Maximum position size

# Order limits
'max_pending_orders': {
    'enabled': True,
    'max_orders': 20        # Limit total pending orders
}
```

### Terminal-Specific Settings

```python
'Terminal1': {
    # Conservative settings
    'lot_multiplier': 0.5,
    'allowed_order_types': ['BUY_LIMIT', 'SELL_LIMIT'],
    'orphan_management': {
        'kill_orphaned_orders': False  # Keep orphans
    }
},
'Terminal2': {
    # Aggressive settings
    'lot_multiplier': 2.0,
    'allowed_order_types': ['BUY_STOP', 'SELL_STOP'],
    'orphan_management': {
        'kill_orphaned_orders': True,
        'max_orphan_checks': 1  # Quick orphan removal
    }
}
```

## Security Considerations

1. **Credential Protection**: Store passwords securely, consider environment variables
2. **Access Control**: Limit system access to authorized users
3. **Log Security**: Protect log files from unauthorized access
4. **Network Security**: Use secure connections when possible
5. **Backup Strategy**: Regular backups of configuration and state files

## Performance Optimization

1. **Execution Intervals**: Balance between responsiveness and resource usage
2. **Log Levels**: Use appropriate log levels for production
3. **Terminal Limits**: Set reasonable maximum order limits
4. **Resource Monitoring**: Monitor CPU and memory usage
5. **Network Optimization**: Minimize connection overhead

## Support and Maintenance

### Regular Maintenance
- Monitor log files for errors
- Review system statistics
- Update configuration as needed
- Backup state files regularly
- Test with demo accounts first

### Troubleshooting Steps
1. Check log files for error messages
2. Verify MT5 terminal connections
3. Test with minimal configuration
4. Review recent configuration changes
5. Check system resources and permissions

## License

This system is provided as-is for educational and development purposes. Use at your own risk in live trading environments.

## Disclaimer

Trading financial instruments involves substantial risk of loss and is not suitable for all investors. This software is provided for educational purposes only and should be thoroughly tested before use in live trading environments. The authors are not responsible for any financial losses incurred through the use of this software.