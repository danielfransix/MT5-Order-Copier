# MT5 Pending Order Copier System - Order Management Core
# This module handles order copying, synchronization, and management logic

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from mt5_connector import MT5Connector
from order_tracker import OrderTracker
from utils import (
    setup_logging, format_error_message, calculate_lot_size,
    validate_lot_size, is_valid_order_type, get_order_type_code,
    validate_symbol_mapping, safe_float_compare, create_order_summary,
    format_price, get_current_timestamp
)

class OrderManager:
    """Manages order copying, synchronization, and lifecycle"""
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        self.logger = logger or setup_logging()
        self.config = config
        self.source_config = config['SOURCE_TERMINAL']
        self.target_configs = config['TARGET_TERMINALS']
        self.system_config = config.get('SYSTEM_CONFIG', {})
        
        # Initialize components
        self.connector = MT5Connector(logger=self.logger)
        self.tracker = OrderTracker(logger=self.logger)
        
        # Statistics
        self.stats = {
            'orders_copied': 0,
            'orders_updated': 0,
            'orders_cancelled': 0,
            'positions_updated': 0,
            'errors': 0,
            'terminals_processed': 0
        }
    
    def process_all_terminals(self) -> bool:
        """Main processing function - handles all terminals sequentially"""
        try:
            self.logger.info("Starting order copying process for all terminals")
            
            # Step 1: Get source orders and positions
            source_orders = self._get_source_orders()
            if source_orders is None:
                self.logger.error("Failed to retrieve source orders")
                return False
            
            source_positions = self._get_source_positions()
            if source_positions is None:
                self.logger.error("Failed to retrieve source positions")
                return False
            
            # Update tracker with source data
            self.tracker.update_source_orders(source_orders)
            self.tracker.update_source_positions(source_positions)
            
            # Step 2: Process each target terminal
            success = True
            for terminal_name, terminal_config in self.target_configs.items():
                try:
                    self.logger.info(f"Processing terminal: {terminal_name}")
                    
                    if not self._process_terminal(terminal_name, terminal_config, source_orders, source_positions):
                        self.logger.error(f"Failed to process terminal: {terminal_name}")
                        success = False
                        break
                    
                    self.stats['terminals_processed'] += 1
                    
                except Exception as e:
                    self.logger.error(f"Exception processing terminal {terminal_name}: {format_error_message(e)}")
                    success = False
                    break
            
            # Step 3: Save tracking state
            if not self.tracker.save_state():
                self.logger.warning("Failed to save tracking state")
            
            # Step 4: Log final statistics
            self._log_statistics()
            
            if success:
                self.logger.info(f"Order copying process completed successfully. Orders copied: {self.stats['orders_copied']}, "
                               f"Orders updated: {self.stats['orders_updated']}, "
                               f"Orders cancelled: {self.stats['orders_cancelled']}, "
                               f"Positions updated: {self.stats['positions_updated']}")
            else:
                self.logger.error("Order copying process completed with errors")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Critical error in process_all_terminals: {format_error_message(e)}")
            return False
    
    def _get_source_orders(self) -> Optional[List[Dict[str, Any]]]:
        """Retrieve orders from source terminal"""
        try:
            self.logger.info("Connecting to source terminal")
            
            if not self.connector.connect(self.source_config, "Source"):
                self.logger.error("Failed to connect to source terminal")
                return None
            
            # Get pending orders
            orders = self.connector.get_pending_orders()
            self.logger.info(f"Retrieved {len(orders)} orders from source terminal")
            
            # Disconnect from source
            self.connector.disconnect()
            
            return orders
            
        except Exception as e:
            self.logger.error(f"Error getting source orders: {format_error_message(e)}")
            self.connector.disconnect()
            return None
    
    def _get_source_positions(self) -> Optional[List[Dict[str, Any]]]:
        """Retrieve positions from source terminal"""
        try:
            self.logger.info("Connecting to source terminal for positions")
            
            if not self.connector.connect(self.source_config, "Source"):
                self.logger.error("Failed to connect to source terminal")
                return None
            
            # Get positions
            positions = self.connector.get_positions()
            self.logger.info(f"Retrieved {len(positions)} positions from source terminal")
            
            # Disconnect from source
            self.connector.disconnect()
            
            return positions
            
        except Exception as e:
            self.logger.error(f"Error getting source positions: {format_error_message(e)}")
            self.connector.disconnect()
            return None
    
    def _process_terminal(self, terminal_name: str, terminal_config: Dict[str, Any], 
                        source_orders: List[Dict[str, Any]], source_positions: List[Dict[str, Any]]) -> bool:
        """Process a single target terminal"""
        try:
            # Connect to target terminal
            if not self.connector.connect(terminal_config, terminal_name):
                self.logger.error(f"Failed to connect to {terminal_name}")
                return False
            
            # Get current target orders and positions
            target_orders = self.connector.get_pending_orders()
            self.logger.info(f"Retrieved {len(target_orders)} orders from {terminal_name}")
            
            target_positions = self.connector.get_positions()
            self.logger.info(f"Retrieved {len(target_positions)} positions from {terminal_name}")
            
            # Update tracker with target data
            self.tracker.update_target_orders(terminal_name, target_orders)
            self.tracker.update_target_positions(terminal_name, target_positions)
            
            # Process orders
            success = True
            
            # Step 1: Copy new orders
            if not self._copy_new_orders(terminal_name, terminal_config, source_orders, target_orders):
                success = False
            
            # Step 2: Update modified orders
            if success and not self._update_modified_orders(terminal_name, terminal_config, source_orders, target_orders):
                success = False
            
            # Step 3: Handle orphaned orders
            if success and not self._handle_orphaned_orders(terminal_name, terminal_config, target_orders):
                success = False
            
            # Step 4: Handle orphaned positions
            if success and not self._handle_orphaned_positions(terminal_name, terminal_config, target_positions):
                success = False
            
            # Step 5: Synchronize positions
            if success and not self._synchronize_positions(terminal_name, source_positions, target_positions):
                success = False
            
            # Disconnect from target terminal
            self.connector.disconnect()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error processing terminal {terminal_name}: {format_error_message(e)}")
            self.connector.disconnect()
            return False
    
    def _synchronize_positions(self, terminal_name: str, source_positions: List[Dict[str, Any]], 
                             target_positions: List[Dict[str, Any]]) -> bool:
        """Synchronize positions between source and target terminals"""
        try:
            self.logger.info(f"Synchronizing positions for {terminal_name}")
            
            # Create mapping of source positions by magic number (source ticket)
            source_pos_map = {pos['magic']: pos for pos in source_positions}
            
            # Check each target position for updates needed
            for target_pos in target_positions:
                magic_number = target_pos.get('magic')
                
                # Find corresponding source position
                if magic_number in source_pos_map:
                    source_pos = source_pos_map[magic_number]
                    
                    # Check if position needs update
                    if self._position_needs_update(source_pos, target_pos):
                        if self._update_single_position(target_pos, source_pos):
                            self.stats['positions_updated'] += 1
                            self.logger.info(f"Updated position {target_pos['ticket']} on {terminal_name}")
                        else:
                            self.logger.error(f"Failed to update position {target_pos['ticket']} on {terminal_name}")
                            return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error synchronizing positions for {terminal_name}: {format_error_message(e)}")
            return False
    
    def _position_needs_update(self, source_pos: Dict[str, Any], target_pos: Dict[str, Any]) -> bool:
        """Check if a position needs to be updated based on source position"""
        try:
            # Check Stop Loss
            source_sl = source_pos.get('sl', 0.0)
            target_sl = target_pos.get('sl', 0.0)
            
            # Check Take Profit
            source_tp = source_pos.get('tp', 0.0)
            target_tp = target_pos.get('tp', 0.0)
            
            # Compare with small tolerance for floating point precision
            tolerance = 1e-5
            
            sl_different = abs(source_sl - target_sl) > tolerance
            tp_different = abs(source_tp - target_tp) > tolerance
            
            if sl_different or tp_different:
                self.logger.debug(f"Position {target_pos['ticket']} needs update: "
                                f"SL {target_sl} -> {source_sl}, TP {target_tp} -> {source_tp}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking if position needs update: {format_error_message(e)}")
            return False
    
    def _update_single_position(self, target_pos: Dict[str, Any], source_pos: Dict[str, Any]) -> bool:
        """Update a single position's SL/TP based on source position"""
        try:
            ticket = target_pos['ticket']
            
            # Prepare modifications based on source position
            modifications = {
                'sl': source_pos.get('sl', 0.0),
                'tp': source_pos.get('tp', 0.0)
            }
            
            self.logger.info(f"Updating position {ticket} with SL: {modifications['sl']}, TP: {modifications['tp']}")
            
            # Use the connector to modify the position
            success = self.connector.modify_position(ticket, modifications)
            
            if success:
                self.logger.info(f"Successfully updated position {ticket}")
            else:
                self.logger.error(f"Failed to update position {ticket}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error updating position {target_pos.get('ticket', 'unknown')}: {format_error_message(e)}")
            return False
    
    def _copy_new_orders(self, terminal_name: str, terminal_config: Dict[str, Any],
                        source_orders: List[Dict[str, Any]], target_orders: List[Dict[str, Any]]) -> bool:
        """Copy new orders from source to target terminal"""
        try:
            # Get existing magic numbers (source tickets) on target
            existing_magics = {order['magic'] for order in target_orders}
            
            # Find new source orders to copy
            new_orders = []
            for source_order in source_orders:
                source_ticket = source_order['ticket']
                if source_ticket not in existing_magics:
                    new_orders.append(source_order)
            
            if not new_orders:
                self.logger.info(f"No new orders to copy to {terminal_name}")
                return True
            
            self.logger.info(f"Found {len(new_orders)} new orders to copy to {terminal_name}")
            
            # Check terminal constraints
            if not self._check_terminal_constraints(terminal_name, terminal_config, len(target_orders), len(new_orders)):
                return True  # Not an error, just constraint violation
            
            # Copy each new order
            for source_order in new_orders:
                if not self._copy_single_order(terminal_name, terminal_config, source_order):
                    self.logger.error(f"Failed to copy order {source_order['ticket']} to {terminal_name}")
                    return False
                
                self.stats['orders_copied'] += 1
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error copying new orders to {terminal_name}: {format_error_message(e)}")
            return False
    
    def _copy_single_order(self, terminal_name: str, terminal_config: Dict[str, Any],
                          source_order: Dict[str, Any]) -> bool:
        """Copy a single order to target terminal"""
        try:
            # Check order type filter
            allowed_types = terminal_config.get('allowed_order_types', [])
            if not is_valid_order_type(source_order['type_name'], allowed_types):
                self.logger.info(f"Order type {source_order['type_name']} not allowed on {terminal_name}")
                return True  # Not an error, just filtered out
            
            # Map symbol
            symbol_mapping = terminal_config.get('symbol_mapping', {})
            target_symbol = validate_symbol_mapping(source_order['symbol'], symbol_mapping)
            
            # Check symbol availability
            symbol_info = self.connector.get_symbol_info(target_symbol)
            if symbol_info is None:
                self.logger.warning(f"Symbol {target_symbol} not available on {terminal_name}")
                return True  # Not an error, symbol not available
            
            # Calculate lot size
            source_lot = source_order['volume_initial']
            multiplier = terminal_config.get('lot_multiplier', 1.0)
            min_lot = terminal_config.get('min_lot_size', 0.01)
            max_lot = terminal_config.get('max_lot_size', 100.0)
            
            target_lot = calculate_lot_size(source_lot, multiplier, min_lot, max_lot)
            
            # Validate lot size
            if not validate_lot_size(target_lot, min_lot, max_lot):
                self.logger.warning(f"Calculated lot size {target_lot} outside constraints for {terminal_name}")
                return True  # Not an error, just constraint violation
            
            # Prepare order request
            order_request = {
                'symbol': target_symbol,
                'volume': target_lot,
                'type': source_order['type'],
                'price': format_price(source_order['price_open'], symbol_info['digits']),
                'magic': source_order['ticket'],  # Use source ticket as magic
                'comment': f"Copied from {source_order['ticket']}"
            }
            
            # Add optional parameters
            if source_order['sl'] > 0:
                order_request['sl'] = format_price(source_order['sl'], symbol_info['digits'])
            
            if source_order['tp'] > 0:
                order_request['tp'] = format_price(source_order['tp'], symbol_info['digits'])
            
            if source_order['time_expiration']:
                order_request['expiration'] = source_order['time_expiration']
            
            # Place order
            success, ticket, message = self.connector.place_order(order_request)
            
            if success:
                self.logger.info(f"Successfully copied order {source_order['ticket']} to {terminal_name} as {ticket}")
                return True
            else:
                self.logger.error(f"Failed to copy order {source_order['ticket']} to {terminal_name}: {message}")
                return False
            
        except Exception as e:
            self.logger.error(f"Error copying single order: {format_error_message(e)}")
            return False
    
    def _update_modified_orders(self, terminal_name: str, terminal_config: Dict[str, Any],
                               source_orders: List[Dict[str, Any]], target_orders: List[Dict[str, Any]]) -> bool:
        """Update modified orders on target terminal"""
        try:
            # Create lookup dictionaries
            source_dict = {order['ticket']: order for order in source_orders}
            target_by_magic = {}
            
            for target_order in target_orders:
                magic = target_order['magic']
                if magic not in target_by_magic:
                    target_by_magic[magic] = []
                target_by_magic[magic].append(target_order)
            
            # Find orders that need updates
            updates_needed = []
            
            for source_ticket, source_order in source_dict.items():
                if source_ticket in target_by_magic:
                    target_orders_list = target_by_magic[source_ticket]
                    
                    for target_order in target_orders_list:
                        if self._order_needs_update(source_order, target_order, terminal_config):
                            updates_needed.append((source_order, target_order))
            
            if not updates_needed:
                self.logger.info(f"No order updates needed for {terminal_name}")
                return True
            
            self.logger.info(f"Found {len(updates_needed)} orders to update on {terminal_name}")
            
            # Apply updates
            for source_order, target_order in updates_needed:
                if not self._update_single_order(terminal_name, terminal_config, source_order, target_order):
                    self.logger.error(f"Failed to update order {target_order['ticket']} on {terminal_name}")
                    return False
                
                self.stats['orders_updated'] += 1
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating modified orders on {terminal_name}: {format_error_message(e)}")
            return False
    
    def _order_needs_update(self, source_order: Dict[str, Any], target_order: Dict[str, Any],
                           terminal_config: Dict[str, Any]) -> bool:
        """Check if target order needs to be updated based on source order changes"""
        # Calculate expected target values
        multiplier = terminal_config.get('lot_multiplier', 1.0)
        min_lot = terminal_config.get('min_lot_size', 0.01)
        max_lot = terminal_config.get('max_lot_size', 100.0)
        
        expected_lot = calculate_lot_size(source_order['volume_initial'], multiplier, min_lot, max_lot)
        
        # Check for differences
        tolerance = 1e-5
        
        # Price difference
        if not safe_float_compare(source_order['price_open'], target_order['price_open'], tolerance):
            return True
        
        # Volume difference
        if not safe_float_compare(expected_lot, target_order['volume_initial'], tolerance):
            return True
        
        # Stop loss difference
        source_sl = source_order.get('sl', 0)
        target_sl = target_order.get('sl', 0)
        if not safe_float_compare(source_sl, target_sl, tolerance):
            return True
        
        # Take profit difference
        source_tp = source_order.get('tp', 0)
        target_tp = target_order.get('tp', 0)
        if not safe_float_compare(source_tp, target_tp, tolerance):
            return True
        
        # Expiration time difference
        source_exp = source_order.get('time_expiration')
        target_exp = target_order.get('time_expiration')
        if str(source_exp) != str(target_exp):
            return True
        
        return False
    
    def _update_single_order(self, terminal_name: str, terminal_config: Dict[str, Any],
                            source_order: Dict[str, Any], target_order: Dict[str, Any]) -> bool:
        """Update a single order on target terminal"""
        try:
            # Get symbol info for price formatting
            symbol_info = self.connector.get_symbol_info(target_order['symbol'])
            if symbol_info is None:
                self.logger.error(f"Cannot get symbol info for {target_order['symbol']}")
                return False
            
            # Calculate new lot size
            multiplier = terminal_config.get('lot_multiplier', 1.0)
            min_lot = terminal_config.get('min_lot_size', 0.01)
            max_lot = terminal_config.get('max_lot_size', 100.0)
            
            new_lot = calculate_lot_size(source_order['volume_initial'], multiplier, min_lot, max_lot)
            
            # Prepare modifications
            modifications = {
                'volume': new_lot,
                'price': format_price(source_order['price_open'], symbol_info['digits'])
            }
            
            # Add stop loss if present
            if source_order.get('sl', 0) > 0:
                modifications['sl'] = format_price(source_order['sl'], symbol_info['digits'])
            else:
                modifications['sl'] = 0
            
            # Add take profit if present
            if source_order.get('tp', 0) > 0:
                modifications['tp'] = format_price(source_order['tp'], symbol_info['digits'])
            else:
                modifications['tp'] = 0
            
            # Add expiration time
            modifications['expiration'] = source_order.get('time_expiration')
            
            # Apply modification
            success, message = self.connector.modify_order(target_order['ticket'], modifications)
            
            if success:
                self.logger.info(f"Successfully updated order {target_order['ticket']} on {terminal_name}")
                return True
            else:
                self.logger.error(f"Failed to update order {target_order['ticket']} on {terminal_name}: {message}")
                return False
            
        except Exception as e:
            self.logger.error(f"Error updating single order: {format_error_message(e)}")
            return False
    
    def _handle_orphaned_orders(self, terminal_name: str, terminal_config: Dict[str, Any],
                               target_orders: List[Dict[str, Any]]) -> bool:
        """Handle orphaned orders according to terminal policy"""
        try:
            # Get orphan management configuration
            orphan_config = terminal_config.get('orphan_management', {})
            kill_orphans = orphan_config.get('kill_orphaned_orders', False)
            max_checks = orphan_config.get('max_orphan_checks', 3)
            
            if not kill_orphans:
                self.logger.info(f"Orphan killing disabled for {terminal_name}")
                return True
            
            # Detect orphaned orders
            orphaned_orders = self.tracker.detect_orphaned_orders(terminal_name)
            
            if not orphaned_orders:
                self.logger.info(f"No orphaned orders found on {terminal_name}")
                return True
            
            self.logger.info(f"Found {len(orphaned_orders)} orphaned orders on {terminal_name}")
            
            # Process each orphaned order
            for orphan_order in orphaned_orders:
                ticket = orphan_order['ticket']
                
                # Increment check counter
                check_count = self.tracker.increment_orphan_check(terminal_name, ticket)
                
                # Check if should kill
                if self.tracker.should_kill_orphan(terminal_name, ticket, max_checks):
                    if not self._cancel_orphaned_order(terminal_name, orphan_order):
                        self.logger.error(f"Failed to cancel orphaned order {ticket} on {terminal_name}")
                        return False
                    
                    # Reset check counter after successful cancellation
                    self.tracker.reset_orphan_check(terminal_name, ticket)
                    self.stats['orders_cancelled'] += 1
                else:
                    self.logger.info(f"Orphaned order {ticket} on {terminal_name} check count: {check_count}/{max_checks}")
            
            # Clean up orphan checks for orders that no longer exist
            active_tickets = {order['ticket'] for order in target_orders}
            self.tracker.cleanup_orphan_checks(terminal_name, active_tickets)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error handling orphaned orders on {terminal_name}: {format_error_message(e)}")
            return False
    
    def _cancel_orphaned_order(self, terminal_name: str, orphan_order: Dict[str, Any]) -> bool:
        """Cancel a single orphaned order"""
        try:
            ticket = orphan_order['ticket']
            
            self.logger.info(f"Cancelling orphaned order {ticket} on {terminal_name}")
            
            success, message = self.connector.cancel_order(ticket)
            
            if success:
                self.logger.info(f"Successfully cancelled orphaned order {ticket} on {terminal_name}")
                return True
            else:
                self.logger.error(f"Failed to cancel orphaned order {ticket} on {terminal_name}: {message}")
                return False
            
        except Exception as e:
            self.logger.error(f"Error cancelling orphaned order: {format_error_message(e)}")
            return False
    
    def _handle_orphaned_positions(self, terminal_name: str, terminal_config: Dict[str, Any],
                                  target_positions: List[Dict[str, Any]]) -> bool:
        """Handle orphaned positions according to terminal policy"""
        try:
            # Get orphan management configuration
            orphan_config = terminal_config.get('orphan_management', {})
            kill_orphans = orphan_config.get('kill_orphaned_positions', False)
            max_checks = orphan_config.get('max_orphan_checks', 3)
            
            if not kill_orphans:
                self.logger.info(f"Orphaned position killing disabled for {terminal_name}")
                return True
            
            # Detect orphaned positions
            orphaned_positions = self.tracker.detect_orphaned_positions(terminal_name)
            
            if not orphaned_positions:
                self.logger.info(f"No orphaned positions found on {terminal_name}")
                return True
            
            self.logger.info(f"Found {len(orphaned_positions)} orphaned positions on {terminal_name}")
            
            # Process each orphaned position
            for orphan_position in orphaned_positions:
                ticket = orphan_position['ticket']
                
                # Increment check counter (reusing the same counter as orders)
                check_count = self.tracker.increment_orphan_check(terminal_name, ticket)
                
                # Check if should kill
                if self.tracker.should_kill_orphan(terminal_name, ticket, max_checks):
                    if not self._close_orphaned_position(terminal_name, orphan_position):
                        self.logger.error(f"Failed to close orphaned position {ticket} on {terminal_name}")
                        return False
                    
                    # Reset check counter after successful closure
                    self.tracker.reset_orphan_check(terminal_name, ticket)
                    self.stats['positions_updated'] += 1  # Reusing this stat for closed positions
                else:
                    self.logger.info(f"Orphaned position {ticket} on {terminal_name} check count: {check_count}/{max_checks}")
            
            # Clean up orphan checks for positions that no longer exist
            active_tickets = {position['ticket'] for position in target_positions}
            self.tracker.cleanup_orphan_checks(terminal_name, active_tickets)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error handling orphaned positions on {terminal_name}: {format_error_message(e)}")
            return False
    
    def _close_orphaned_position(self, terminal_name: str, orphan_position: Dict[str, Any]) -> bool:
        """Close a single orphaned position"""
        try:
            ticket = orphan_position['ticket']
            
            self.logger.info(f"Closing orphaned position {ticket} on {terminal_name}")
            
            success, message = self.connector.close_position(ticket)
            
            if success:
                self.logger.info(f"Successfully closed orphaned position {ticket} on {terminal_name}")
                return True
            else:
                self.logger.error(f"Failed to close orphaned position {ticket} on {terminal_name}: {message}")
                return False
            
        except Exception as e:
            self.logger.error(f"Error closing orphaned position: {format_error_message(e)}")
            return False
    
    def _check_terminal_constraints(self, terminal_name: str, terminal_config: Dict[str, Any],
                                   current_order_count: int, new_order_count: int) -> bool:
        """Check if terminal constraints allow new orders"""
        # Check maximum pending orders limit
        max_orders_config = terminal_config.get('max_pending_orders', {})
        if max_orders_config.get('enabled', False):
            max_orders = max_orders_config.get('max_orders', 50)
            
            if current_order_count + new_order_count > max_orders:
                self.logger.warning(
                    f"Terminal {terminal_name} would exceed max orders limit: "
                    f"{current_order_count + new_order_count} > {max_orders}"
                )
                return False
        
        return True
    
    def _log_statistics(self) -> None:
        """Log processing statistics"""
        self.logger.info("=== Processing Statistics ===")
        self.logger.info(f"Terminals processed: {self.stats['terminals_processed']}")
        self.logger.info(f"Orders copied: {self.stats['orders_copied']}")
        self.logger.info(f"Orders updated: {self.stats['orders_updated']}")
        self.logger.info(f"Orders cancelled: {self.stats['orders_cancelled']}")
        self.logger.info(f"Errors encountered: {self.stats['errors']}")
        
        # Get tracker statistics
        tracker_stats = self.tracker.get_system_statistics()
        self.logger.info(f"Total source orders: {tracker_stats['total_source_orders']}")
        self.logger.info(f"Total orphan checks: {tracker_stats['total_orphan_checks']}")
        
        for terminal_name, terminal_stats in tracker_stats['terminals'].items():
            self.logger.info(
                f"Terminal {terminal_name}: {terminal_stats['target_orders']} orders, "
                f"{terminal_stats['orphan_checks']} orphan checks"
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current processing statistics"""
        return {
            'processing_stats': self.stats.copy(),
            'tracker_stats': self.tracker.get_system_statistics()
        }
    
    def cleanup(self) -> None:
        """Clean up resources"""
        try:
            self.connector.disconnect()
            self.tracker.save_state()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {format_error_message(e)}")