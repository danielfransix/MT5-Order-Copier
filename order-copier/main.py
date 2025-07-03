#!/usr/bin/env python3
# MT5 Pending Order Copier System - Main Application Entry Point
# This is the main entry point that orchestrates the entire system

import sys
import os
import time
import signal
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import load_config, validate_config
from order_manager import OrderManager
from scheduling_utils import calculate_next_execution_time, get_time_until_next_execution
from utils import (
    setup_logging, format_error_message, get_current_timestamp,
    ensure_directory_exists
)

class MT5OrderCopierApp:
    """Main application class for MT5 Order Copier"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or 'config.py'
        self.config = None
        self.logger = None
        self.order_manager = None
        self.running = False
        self.shutdown_requested = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def initialize(self) -> bool:
        """Initialize the application"""
        try:
            print(f"MT5 Pending Order Copier - Starting initialization at {get_current_timestamp()}")
            
            # Step 1: Load and validate configuration
            if not self._load_configuration():
                return False
            
            # Step 2: Setup logging
            if not self._setup_logging():
                return False
            
            # Step 3: Create necessary directories
            if not self._create_directories():
                return False
            
            # Step 4: Initialize order manager
            if not self._initialize_order_manager():
                return False
            
            self.logger.info("Application initialization completed successfully")
            return True
            
        except Exception as e:
            error_msg = f"Critical error during initialization: {format_error_message(e)}"
            if self.logger:
                self.logger.error(error_msg)
            else:
                print(error_msg)
            return False
    
    def run(self) -> int:
        """Main application run loop"""
        if not self.initialize():
            print("Failed to initialize application")
            return 1
        
        try:
            self.running = True
            self.logger.info("Starting MT5 Pending Order Copier main loop")
            
            # Get execution configuration (Claude-style)
            enable_scheduling = self.config.get('ENABLE_SCHEDULING', False)
            enable_continuous_mode = self.config.get('ENABLE_CONTINUOUS_MODE', True)
            
            # Determine execution mode based on configuration
            if enable_continuous_mode and enable_scheduling:
                # Both enabled - prioritize continuous mode as per plan
                self.logger.info("Both scheduling and continuous mode enabled - running in continuous mode")
                return self._run_continuous_mode()
            elif enable_continuous_mode:
                return self._run_continuous_mode()
            elif enable_scheduling:
                return self._run_scheduled_mode()
            else:
                # Neither enabled - run once and exit
                self.logger.info("No execution mode enabled - running once and exiting")
                return self._run_once()
            
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt, shutting down gracefully")
            return 0
        except Exception as e:
            self.logger.error(f"Critical error in main loop: {format_error_message(e)}")
            return 1
        finally:
            self._cleanup()
    
    def _run_once(self) -> int:
        """Run the order copying process once and exit"""
        try:
            self.logger.info("Running in 'once' mode - single execution")
            
            success = self.order_manager.process_all_terminals()
            
            if success:
                self.logger.info("Single execution completed successfully")
                return 0
            else:
                self.logger.error("Single execution failed")
                return 1
            
        except Exception as e:
            self.logger.error(f"Error in single execution mode: {format_error_message(e)}")
            return 1
    
    def _run_scheduled_mode(self) -> int:
        """Run the order copying process on a Claude-style schedule"""
        try:
            schedule_timeframe = self.config.get('SCHEDULE_TIMEFRAME', 'M5')
            schedule_offset_seconds = self.config.get('SCHEDULE_OFFSET_SECONDS', 60)
            
            self.logger.info(f"Running in scheduled mode - timeframe: {schedule_timeframe}, offset: {schedule_offset_seconds}s")
            
            iteration_count = 0
            
            while self.running and not self.shutdown_requested:
                try:
                    iteration_count += 1
                    
                    # Calculate next execution time
                    next_execution_time = calculate_next_execution_time(schedule_timeframe, schedule_offset_seconds)
                    wait_seconds = get_time_until_next_execution(schedule_timeframe, schedule_offset_seconds)
                    
                    self.logger.info(f"Iteration {iteration_count} - Next execution at: {next_execution_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    self.logger.info(f"Waiting {wait_seconds:.1f} seconds until next execution")
                    
                    # Wait until next execution time
                    if wait_seconds > 0 and self.running and not self.shutdown_requested:
                        self._wait_for_next_iteration(wait_seconds)
                    
                    # Check if we should still run after waiting
                    if not self.running or self.shutdown_requested:
                        break
                    
                    # Process all terminals
                    start_time = time.time()
                    self.logger.info(f"Starting scheduled execution {iteration_count}")
                    success = self.order_manager.process_all_terminals()
                    end_time = time.time()
                    
                    processing_time = end_time - start_time
                    self.logger.info(f"Scheduled execution {iteration_count} completed in {processing_time:.2f}s")
                    
                    if not success:
                        self.logger.warning(f"Scheduled execution {iteration_count} completed with errors")
                    
                except Exception as e:
                    self.logger.error(f"Error in scheduled execution {iteration_count}: {format_error_message(e)}")
                    
                    # Wait before retrying (use a shorter interval for error recovery)
                    if self.running and not self.shutdown_requested:
                        self.logger.info("Waiting 30 seconds before retry due to error")
                        self._wait_for_next_iteration(30)
            
            self.logger.info(f"Scheduled execution completed after {iteration_count} iterations")
            return 0
            
        except Exception as e:
            self.logger.error(f"Error in scheduled execution mode: {format_error_message(e)}")
            return 1
    
    def _run_continuous_mode(self) -> int:
        """Run the order copying process continuously with Claude-style parameters"""
        try:
            delay_seconds = self.config.get('CONTINUOUS_DELAY_SECONDS', 5)
            max_runtime_hours = self.config.get('CONTINUOUS_MAX_RUNTIME_HOURS', 0)  # 0 = unlimited
            
            self.logger.info(f"Running in continuous mode - delay: {delay_seconds}s")
            if max_runtime_hours > 0:
                self.logger.info(f"Maximum runtime: {max_runtime_hours} hours")
            
            start_time = datetime.now()
            iteration_count = 0
            
            while self.running and not self.shutdown_requested:
                try:
                    iteration_count += 1
                    
                    # Check runtime limit
                    if max_runtime_hours > 0:
                        runtime = datetime.now() - start_time
                        if runtime > timedelta(hours=max_runtime_hours):
                            self.logger.info(f"Reached maximum runtime ({max_runtime_hours} hours), stopping")
                            break
                    
                    # Process all terminals immediately with no delay between terminals
                    start_iteration_time = time.time()
                    success = self.order_manager.process_all_terminals()
                    end_iteration_time = time.time()
                    
                    processing_time = end_iteration_time - start_iteration_time
                    self.logger.debug(f"Continuous iteration {iteration_count} completed in {processing_time:.2f}s")
                    
                    if not success:
                        self.logger.warning(f"Continuous iteration {iteration_count} completed with errors")
                    
                    # Delay before next iteration (but no delay between terminals)
                    if self.running and not self.shutdown_requested:
                        self._wait_for_next_iteration(delay_seconds)
                    
                except Exception as e:
                    self.logger.error(f"Error in continuous iteration {iteration_count}: {format_error_message(e)}")
                    
                    # Wait before retrying (use double delay or max 30s for error recovery)
                    if self.running and not self.shutdown_requested:
                        error_delay = min(delay_seconds * 2, 30)
                        self.logger.info(f"Waiting {error_delay} seconds before retry due to error")
                        self._wait_for_next_iteration(error_delay)
            
            runtime = datetime.now() - start_time
            self.logger.info(f"Continuous execution completed after {iteration_count} iterations in {runtime}")
            return 0
            
        except Exception as e:
            self.logger.error(f"Error in continuous execution mode: {format_error_message(e)}")
            return 1
    
    def _wait_for_next_iteration(self, interval_seconds: int) -> None:
        """Wait for the next iteration with graceful shutdown support"""
        sleep_time = 0
        while sleep_time < interval_seconds and self.running and not self.shutdown_requested:
            time.sleep(min(1, interval_seconds - sleep_time))
            sleep_time += 1
    
    def _load_configuration(self) -> bool:
        """Load and validate configuration"""
        try:
            print(f"Loading configuration from: {self.config_path}")
            
            self.config = load_config(self.config_path)
            if self.config is None:
                print("Failed to load configuration")
                return False
            
            # Validate configuration
            is_valid, errors = validate_config(self.config)
            if not is_valid:
                print("Configuration validation failed:")
                for error in errors:
                    print(f"  - {error}")
                return False
            
            print("Configuration loaded and validated successfully")
            return True
            
        except Exception as e:
            print(f"Error loading configuration: {format_error_message(e)}")
            return False
    
    def _setup_logging(self) -> bool:
        """Setup application logging"""
        try:
            logging_config = self.config.get('LOGGING_CONFIG', {})
            
            self.logger = setup_logging(
                log_level=logging_config.get('level', 'INFO'),
                log_file=logging_config.get('file_path')
            )
            
            self.logger.info("Logging system initialized")
            self.logger.info(f"Application started at {get_current_timestamp()}")
            return True
            
        except Exception as e:
            print(f"Error setting up logging: {format_error_message(e)}")
            return False
    
    def _create_directories(self) -> bool:
        """Create necessary directories"""
        try:
            # Create logs directory if specified
            logging_config = self.config.get('LOGGING_CONFIG', {})
            log_file = logging_config.get('file_path')
            if log_file:
                log_dir = os.path.dirname(log_file)
                if not ensure_directory_exists(log_dir):
                    self.logger.error(f"Failed to create log directory: {log_dir}")
                    return False
            
            # Create data directory for tracking state
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
            if not ensure_directory_exists(data_dir):
                self.logger.error(f"Failed to create data directory: {data_dir}")
                return False
            
            self.logger.info("Required directories created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating directories: {format_error_message(e)}")
            return False
    
    def _initialize_order_manager(self) -> bool:
        """Initialize the order manager"""
        try:
            self.order_manager = OrderManager(self.config, self.logger)
            self.logger.info("Order manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing order manager: {format_error_message(e)}")
            return False
    
    def _signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals"""
        signal_name = signal.Signals(signum).name
        if self.logger:
            self.logger.info(f"Received {signal_name} signal, initiating graceful shutdown")
        else:
            print(f"Received {signal_name} signal, initiating graceful shutdown")
        
        self.shutdown_requested = True
        self.running = False
    
    def _cleanup(self) -> None:
        """Clean up resources"""
        try:
            if self.logger:
                self.logger.info("Starting application cleanup")
            
            if self.order_manager:
                self.order_manager.cleanup()
            
            if self.logger:
                self.logger.info("Application cleanup completed")
                self.logger.info(f"Application stopped at {get_current_timestamp()}")
            
        except Exception as e:
            error_msg = f"Error during cleanup: {format_error_message(e)}"
            if self.logger:
                self.logger.error(error_msg)
            else:
                print(error_msg)

def print_usage():
    """Print usage information"""
    print("MT5 Pending Order Copier System")
    print("Usage: python main.py [config_file]")
    print("")
    print("Arguments:")
    print("  config_file    Optional path to configuration file (default: config.py)")
    print("")
    print("Examples:")
    print("  python main.py")
    print("  python main.py custom_config.py")
    print("")
    print("Execution modes (configured in config file):")
    print("  once         - Run once and exit")
    print("  scheduled    - Run on a schedule with intervals")
    print("  continuous   - Run continuously with minimal delay")

def main() -> int:
    """Main entry point"""
    try:
        # Parse command line arguments
        if len(sys.argv) > 2:
            print_usage()
            return 1
        
        if len(sys.argv) == 2:
            if sys.argv[1] in ['-h', '--help', 'help']:
                print_usage()
                return 0
            config_path = sys.argv[1]
        else:
            config_path = None
        
        # Create and run application
        app = MT5OrderCopierApp(config_path)
        return app.run()
        
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt, exiting...")
        return 0
    except Exception as e:
        print(f"Critical error: {format_error_message(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main())