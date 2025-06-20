@echo off
REM MT5 Pending Order Copier - Windows Batch Script
REM This script provides easy execution and management of the order copier system

setlocal enabledelayedexpansion

REM Set script directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Set window title
title MT5 Pending Order Copier

REM Colors for output
set GREEN=[92m
set RED=[91m
set YELLOW=[93m
set BLUE=[94m
set RESET=[0m

REM Main menu
:MAIN_MENU
cls
echo %BLUE%========================================%RESET%
echo %BLUE%    MT5 Pending Order Copier System    %RESET%
echo %BLUE%========================================%RESET%
echo.
echo %GREEN%1.%RESET% Run Order Copier (Normal Mode)
echo %GREEN%2.%RESET% Run Order Copier (Once Mode)
echo %GREEN%3.%RESET% Test System
echo %GREEN%4.%RESET% Install Dependencies
echo %GREEN%5.%RESET% Setup Configuration
echo %GREEN%6.%RESET% View Logs
echo %GREEN%7.%RESET% Check System Status
echo %GREEN%8.%RESET% Help
echo %GREEN%9.%RESET% Exit
echo.
set /p choice=%YELLOW%Enter your choice (1-9): %RESET%

if "%choice%"=="1" goto RUN_NORMAL
if "%choice%"=="2" goto RUN_ONCE
if "%choice%"=="3" goto TEST_SYSTEM
if "%choice%"=="4" goto INSTALL_DEPS
if "%choice%"=="5" goto SETUP_CONFIG
if "%choice%"=="6" goto VIEW_LOGS
if "%choice%"=="7" goto CHECK_STATUS
if "%choice%"=="8" goto SHOW_HELP
if "%choice%"=="9" goto EXIT

echo %RED%Invalid choice. Please try again.%RESET%
pause
goto MAIN_MENU

:RUN_NORMAL
cls
echo %BLUE%Running MT5 Order Copier (Normal Mode)...%RESET%
echo.
echo %YELLOW%Press Ctrl+C to stop the copier%RESET%
echo.

REM Check if config exists
if not exist "config.py" (
    echo %RED%Error: config.py not found!%RESET%
    echo %YELLOW%Please run 'Setup Configuration' first.%RESET%
    pause
    goto MAIN_MENU
)

REM Run the copier
python main.py
if errorlevel 1 (
    echo.
    echo %RED%Order copier exited with errors.%RESET%
    echo %YELLOW%Check the logs for more information.%RESET%
) else (
    echo.
    echo %GREEN%Order copier completed successfully.%RESET%
)
pause
goto MAIN_MENU

:RUN_ONCE
cls
echo %BLUE%Running MT5 Order Copier (Once Mode)...%RESET%
echo.

REM Check if config exists
if not exist "config.py" (
    echo %RED%Error: config.py not found!%RESET%
    echo %YELLOW%Please run 'Setup Configuration' first.%RESET%
    pause
    goto MAIN_MENU
)

REM Create temporary config for once mode
echo Creating temporary configuration for once mode...
python -c "import config; c = config.__dict__.copy(); c['EXECUTION_MODE'] = 'once'; exec(open('temp_config.py', 'w').write('\n'.join([f'{k} = {repr(v)}' for k, v in c.items() if not k.startswith('__')])))"

REM Run once
python main.py temp_config.py
if errorlevel 1 (
    echo.
    echo %RED%Order copier exited with errors.%RESET%
) else (
    echo.
    echo %GREEN%Order copier completed successfully.%RESET%
)

REM Clean up temporary config
if exist "temp_config.py" del "temp_config.py"
pause
goto MAIN_MENU

:TEST_SYSTEM
cls
echo %BLUE%Testing MT5 Order Copier System...%RESET%
echo.

python test_system.py
if errorlevel 1 (
    echo.
    echo %RED%System tests failed.%RESET%
    echo %YELLOW%Please review the errors above and fix any issues.%RESET%
) else (
    echo.
    echo %GREEN%All system tests passed!%RESET%
)
pause
goto MAIN_MENU

:INSTALL_DEPS
cls
echo %BLUE%Installing Dependencies...%RESET%
echo.

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo %RED%Error: pip is not available.%RESET%
    echo %YELLOW%Please install Python with pip first.%RESET%
    pause
    goto MAIN_MENU
)

REM Check if requirements.txt exists
if not exist "requirements.txt" (
    echo %RED%Error: requirements.txt not found!%RESET%
    pause
    goto MAIN_MENU
)

echo Installing packages from requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo %RED%Failed to install some dependencies.%RESET%
    echo %YELLOW%Please check the error messages above.%RESET%
) else (
    echo.
    echo %GREEN%All dependencies installed successfully!%RESET%
)
pause
goto MAIN_MENU

:SETUP_CONFIG
cls
echo %BLUE%Setting Up Configuration...%RESET%
echo.

if exist "config.py" (
    echo %YELLOW%config.py already exists.%RESET%
    set /p overwrite="Do you want to overwrite it? (y/n): "
    if /i not "!overwrite!"=="y" goto MAIN_MENU
)

if exist "config_sample.py" (
    echo Copying config_sample.py to config.py...
    copy "config_sample.py" "config.py" >nul
    echo %GREEN%Configuration file created successfully!%RESET%
    echo.
    echo %YELLOW%IMPORTANT: Please edit config.py with your MT5 terminal details:%RESET%
    echo %YELLOW%- Update SOURCE_TERMINAL with your source account details%RESET%
    echo %YELLOW%- Update TARGET_TERMINALS with your target account details%RESET%
    echo %YELLOW%- Configure symbol mappings if needed%RESET%
    echo %YELLOW%- Set appropriate lot multipliers and risk settings%RESET%
    echo.
    set /p edit="Do you want to open config.py for editing now? (y/n): "
    if /i "!edit!"=="y" (
        notepad config.py
    )
) else (
    echo %RED%Error: config_sample.py not found!%RESET%
    echo %YELLOW%Please ensure all system files are present.%RESET%
)
pause
goto MAIN_MENU

:VIEW_LOGS
cls
echo %BLUE%Viewing Log Files...%RESET%
echo.

REM Check for log files
if exist "logs\*.log" (
    echo Available log files:
    dir /b logs\*.log
    echo.
    set /p logfile="Enter log file name (or press Enter for latest): "
    
    if "!logfile!"=="" (
        REM Find the latest log file
        for /f "delims=" %%i in ('dir /b /o-d logs\*.log 2^>nul') do (
            set logfile=%%i
            goto SHOW_LOG
        )
    )
    
    :SHOW_LOG
    if exist "logs\!logfile!" (
        echo.
        echo %YELLOW%Showing last 50 lines of logs\!logfile!:%RESET%
        echo.
        powershell "Get-Content 'logs\!logfile!' | Select-Object -Last 50"
    ) else (
        echo %RED%Log file not found: !logfile!%RESET%
    )
) else (
    echo %YELLOW%No log files found.%RESET%
    echo %YELLOW%Log files will be created when you run the order copier.%RESET%
)
pause
goto MAIN_MENU

:CHECK_STATUS
cls
echo %BLUE%Checking System Status...%RESET%
echo.

REM Check Python
echo Checking Python installation...
python --version 2>nul
if errorlevel 1 (
    echo %RED%✗ Python not found%RESET%
) else (
    echo %GREEN%✓ Python installed%RESET%
)

REM Check dependencies
echo.
echo Checking dependencies...
python -c "import MetaTrader5; print('✓ MetaTrader5')" 2>nul || echo %RED%✗ MetaTrader5%RESET%
python -c "import pandas; print('✓ pandas')" 2>nul || echo %RED%✗ pandas%RESET%
python -c "import numpy; print('✓ numpy')" 2>nul || echo %RED%✗ numpy%RESET%
python -c "import yaml; print('✓ yaml')" 2>nul || echo %RED%✗ yaml%RESET%

REM Check configuration
echo.
echo Checking configuration...
if exist "config.py" (
    echo %GREEN%✓ config.py exists%RESET%
    python -c "import config; print('✓ config.py loads successfully')" 2>nul || echo %RED%✗ config.py has errors%RESET%
) else (
    echo %RED%✗ config.py not found%RESET%
)

REM Check system files
echo.
echo Checking system files...
if exist "main.py" (echo %GREEN%✓ main.py%RESET%) else (echo %RED%✗ main.py%RESET%)
if exist "order_manager.py" (echo %GREEN%✓ order_manager.py%RESET%) else (echo %RED%✗ order_manager.py%RESET%)
if exist "mt5_connector.py" (echo %GREEN%✓ mt5_connector.py%RESET%) else (echo %RED%✗ mt5_connector.py%RESET%)
if exist "order_tracker.py" (echo %GREEN%✓ order_tracker.py%RESET%) else (echo %RED%✗ order_tracker.py%RESET%)
if exist "utils.py" (echo %GREEN%✓ utils.py%RESET%) else (echo %RED%✗ utils.py%RESET%)

REM Check directories
echo.
echo Checking directories...
if exist "logs" (echo %GREEN%✓ logs directory%RESET%) else (echo %YELLOW%! logs directory (will be created)%RESET%)
if exist "data" (echo %GREEN%✓ data directory%RESET%) else (echo %YELLOW%! data directory (will be created)%RESET%)

pause
goto MAIN_MENU

:SHOW_HELP
cls
echo %BLUE%MT5 Pending Order Copier - Help%RESET%
echo %BLUE%================================%RESET%
echo.
echo %GREEN%Quick Start:%RESET%
echo 1. Install Dependencies (option 4)
echo 2. Setup Configuration (option 5)
echo 3. Edit config.py with your MT5 account details
echo 4. Test System (option 3)
echo 5. Run Order Copier (option 1)
echo.
echo %GREEN%Important Files:%RESET%
echo - config.py: Main configuration file
echo - main.py: Main application
echo - logs/: Log files directory
echo - data/: System state files
echo.
echo %GREEN%Execution Modes:%RESET%
echo - Normal: Runs according to config (scheduled/continuous)
echo - Once: Runs one iteration and exits
echo.
echo %GREEN%Safety Tips:%RESET%
echo - Always test with demo accounts first
echo - Start with small lot multipliers
echo - Monitor logs regularly
echo - Keep backups of working configurations
echo.
echo %GREEN%Troubleshooting:%RESET%
echo - Check system status (option 7)
echo - Review log files (option 6)
echo - Run system tests (option 3)
echo - Verify MT5 terminal settings
echo.
echo %YELLOW%For detailed documentation, see README.md%RESET%
echo.
pause
goto MAIN_MENU

:EXIT
echo.
echo %GREEN%Thank you for using MT5 Pending Order Copier!%RESET%
echo.
exit /b 0

REM Error handling
:ERROR
echo.
echo %RED%An error occurred. Please check the above messages.%RESET%
pause
goto MAIN_MENU