# MT5 Pending Order Copier System - Order Tracking and Orphan Management
# This module handles orphaned order detection, tracking, and management

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Any

from utils import (
    setup_logging, format_error_message, get_current_timestamp,
    ensure_directory_exists, safe_dict_get
)

class OrderTracker:
    """Manages order tracking and orphan detection across system runs"""
    
    def __init__(self, state_file: str = "order_tracker_state.json", logger: Optional[logging.Logger] = None):
        self.logger = logger or setup_logging()
        self.state_file = state_file
        self.state = {
            'orphan_checks': {},  # terminal_name -> {ticket: check_count}
            'last_run': None,
            'source_orders': {},  # ticket -> order_data
            'target_orders': {},   # terminal_name -> {ticket: order_data}
            'source_positions': {},  # ticket -> position_data
            'target_positions': {}   # terminal_name -> {ticket: position_data}
        }
        self.load_state()
    
    def load_state(self) -> bool:
        """Load tracking state from file"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    loaded_state = json.load(f)
                    self.state.update(loaded_state)
                    self.logger.info(f"Loaded tracking state from {self.state_file}")
                    return True
            else:
                self.logger.info("No existing state file found, starting with clean state")
                return True
        except Exception as e:
            self.logger.error(f"Error loading state: {format_error_message(e)}")
            return False
    
    def save_state(self) -> bool:
        """Save tracking state to file"""
        try:
            # Ensure directory exists
            state_dir = os.path.dirname(self.state_file)
            if state_dir and not ensure_directory_exists(state_dir):
                self.logger.error(f"Failed to create state directory: {state_dir}")
                return False
            
            # Update last run timestamp
            self.state['last_run'] = get_current_timestamp()
            
            # Save to file
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2, default=str)
            
            self.logger.debug(f"Saved tracking state to {self.state_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving state: {format_error_message(e)}")
            return False
    
    def update_source_orders(self, orders: List[Dict[str, Any]]) -> None:
        """Update source orders in tracking state"""
        self.state['source_orders'] = {}
        for order in orders:
            ticket = order['ticket']
            self.state['source_orders'][str(ticket)] = {
                'ticket': ticket,
                'symbol': order['symbol'],
                'type_name': order['type_name'],
                'volume': order['volume_initial'],
                'price_open': order['price_open'],
                'sl': order['sl'],
                'tp': order['tp'],
                'time_setup': str(order['time_setup']),
                'time_expiration': str(order['time_expiration']) if order['time_expiration'] else None,
                'last_seen': get_current_timestamp()
            }
        
        self.logger.debug(f"Updated {len(orders)} source orders in tracking state")
    
    def update_source_positions(self, positions: List[Dict[str, Any]]) -> None:
        """Update source positions in tracking state"""
        self.state['source_positions'] = {}
        for position in positions:
            ticket = position['ticket']
            self.state['source_positions'][str(ticket)] = {
                'ticket': ticket,
                'symbol': position['symbol'],
                'type_name': position['type_name'],
                'volume': position['volume'],
                'price_open': position['price_open'],
                'sl': position['sl'],
                'tp': position['tp'],
                'magic': position['magic'],
                'time': str(position['time']),
                'last_seen': get_current_timestamp()
            }
        
        self.logger.debug(f"Updated {len(positions)} source positions in tracking state")
    
    def update_target_orders(self, terminal_name: str, orders: List[Dict[str, Any]]) -> None:
        """Update target orders for a specific terminal"""
        if terminal_name not in self.state['target_orders']:
            self.state['target_orders'][terminal_name] = {}
        
        self.state['target_orders'][terminal_name] = {}
        for order in orders:
            ticket = order['ticket']
            self.state['target_orders'][terminal_name][str(ticket)] = {
                'ticket': ticket,
                'magic': order['magic'],
                'symbol': order['symbol'],
                'type_name': order['type_name'],
                'volume': order['volume_initial'],
                'price_open': order['price_open'],
                'sl': order['sl'],
                'tp': order['tp'],
                'time_setup': str(order['time_setup']),
                'time_expiration': str(order['time_expiration']) if order['time_expiration'] else None,
                'last_seen': get_current_timestamp()
            }
        
        self.logger.debug(f"Updated {len(orders)} target orders for {terminal_name}")
    
    def update_target_positions(self, terminal_name: str, positions: List[Dict[str, Any]]) -> None:
        """Update target positions for a specific terminal"""
        if terminal_name not in self.state['target_positions']:
            self.state['target_positions'][terminal_name] = {}
        
        self.state['target_positions'][terminal_name] = {}
        for position in positions:
            ticket = position['ticket']
            self.state['target_positions'][terminal_name][str(ticket)] = {
                'ticket': ticket,
                'magic': position['magic'],
                'symbol': position['symbol'],
                'type_name': position['type_name'],
                'volume': position['volume'],
                'price_open': position['price_open'],
                'sl': position['sl'],
                'tp': position['tp'],
                'time': str(position['time']),
                'last_seen': get_current_timestamp()
            }
        
        self.logger.debug(f"Updated {len(positions)} target positions for {terminal_name}")
    
    def detect_orphaned_orders(self, terminal_name: str) -> List[Dict[str, Any]]:
        """Detect orphaned orders for a specific terminal"""
        orphaned_orders = []
        
        # Get current source order tickets
        source_tickets = set(self.state['source_orders'].keys())
        
        # Get target orders for this terminal
        target_orders = self.state['target_orders'].get(terminal_name, {})
        
        for ticket_str, order_data in target_orders.items():
            magic = order_data.get('magic')
            
            # Check if magic number (source ticket) exists in current source orders
            if str(magic) not in source_tickets:
                orphaned_orders.append(order_data)
                self.logger.debug(f"Detected orphaned order {ticket_str} with magic {magic} on {terminal_name}")
        
        self.logger.info(f"Detected {len(orphaned_orders)} orphaned orders on {terminal_name}")
        return orphaned_orders
    
    def detect_orphaned_positions(self, terminal_name: str) -> List[Dict[str, Any]]:
        """Detect orphaned positions for a specific terminal"""
        orphaned_positions = []
        
        # Get current source position tickets
        source_tickets = set(self.state['source_positions'].keys())
        
        # Get target positions for this terminal
        target_positions = self.state['target_positions'].get(terminal_name, {})
        
        for ticket_str, position_data in target_positions.items():
            magic = position_data.get('magic')
            
            # Check if magic number (source ticket) exists in current source positions
            if str(magic) not in source_tickets:
                orphaned_positions.append(position_data)
                self.logger.debug(f"Detected orphaned position {ticket_str} with magic {magic} on {terminal_name}")
        
        self.logger.info(f"Detected {len(orphaned_positions)} orphaned positions on {terminal_name}")
        return orphaned_positions
    
    def increment_orphan_check(self, terminal_name: str, ticket: int) -> int:
        """Increment orphan check counter for a specific order"""
        if terminal_name not in self.state['orphan_checks']:
            self.state['orphan_checks'][terminal_name] = {}
        
        ticket_str = str(ticket)
        current_count = self.state['orphan_checks'][terminal_name].get(ticket_str, 0)
        new_count = current_count + 1
        self.state['orphan_checks'][terminal_name][ticket_str] = new_count
        
        self.logger.debug(f"Incremented orphan check for {terminal_name} order {ticket}: {new_count}")
        return new_count
    
    def get_orphan_check_count(self, terminal_name: str, ticket: int) -> int:
        """Get current orphan check count for a specific order"""
        if terminal_name not in self.state['orphan_checks']:
            return 0
        
        ticket_str = str(ticket)
        return self.state['orphan_checks'][terminal_name].get(ticket_str, 0)
    
    def reset_orphan_check(self, terminal_name: str, ticket: int) -> None:
        """Reset orphan check counter for a specific order"""
        if terminal_name not in self.state['orphan_checks']:
            return
        
        ticket_str = str(ticket)
        if ticket_str in self.state['orphan_checks'][terminal_name]:
            del self.state['orphan_checks'][terminal_name][ticket_str]
            self.logger.debug(f"Reset orphan check for {terminal_name} order {ticket}")
    
    def cleanup_orphan_checks(self, terminal_name: str, active_tickets: Set[int]) -> None:
        """Clean up orphan check counters for orders that no longer exist"""
        if terminal_name not in self.state['orphan_checks']:
            return
        
        active_ticket_strs = {str(ticket) for ticket in active_tickets}
        orphan_checks = self.state['orphan_checks'][terminal_name]
        
        # Remove counters for tickets that no longer exist
        tickets_to_remove = []
        for ticket_str in orphan_checks.keys():
            if ticket_str not in active_ticket_strs:
                tickets_to_remove.append(ticket_str)
        
        for ticket_str in tickets_to_remove:
            del orphan_checks[ticket_str]
            self.logger.debug(f"Cleaned up orphan check for non-existent order {ticket_str} on {terminal_name}")
        
        if tickets_to_remove:
            self.logger.info(f"Cleaned up {len(tickets_to_remove)} orphan check counters on {terminal_name}")
    
    def should_kill_orphan(self, terminal_name: str, ticket: int, max_checks: int) -> bool:
        """Determine if an orphaned order should be killed based on check count"""
        current_count = self.get_orphan_check_count(terminal_name, ticket)
        return current_count >= max_checks
    
    def get_orphan_statistics(self, terminal_name: str) -> Dict[str, Any]:
        """Get orphan statistics for a terminal"""
        orphan_checks = self.state['orphan_checks'].get(terminal_name, {})
        
        if not orphan_checks:
            return {
                'total_orphans': 0,
                'max_check_count': 0,
                'avg_check_count': 0,
                'orphan_tickets': []
            }
        
        check_counts = list(orphan_checks.values())
        
        return {
            'total_orphans': len(orphan_checks),
            'max_check_count': max(check_counts),
            'avg_check_count': sum(check_counts) / len(check_counts),
            'orphan_tickets': list(orphan_checks.keys())
        }
    
    def get_order_changes(self, terminal_name: str, current_orders: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Detect changes in orders since last run"""
        changes = {
            'new_orders': [],
            'modified_orders': [],
            'removed_orders': []
        }
        
        # Get previous orders for this terminal
        previous_orders = self.state['target_orders'].get(terminal_name, {})
        current_orders_dict = {str(order['ticket']): order for order in current_orders}
        
        # Find new orders
        for ticket_str, order in current_orders_dict.items():
            if ticket_str not in previous_orders:
                changes['new_orders'].append(order)
        
        # Find modified and removed orders
        for ticket_str, prev_order in previous_orders.items():
            if ticket_str in current_orders_dict:
                current_order = current_orders_dict[ticket_str]
                
                # Check for modifications
                if self._order_modified(prev_order, current_order):
                    changes['modified_orders'].append({
                        'previous': prev_order,
                        'current': current_order
                    })
            else:
                changes['removed_orders'].append(prev_order)
        
        return changes
    
    def _order_modified(self, prev_order: Dict[str, Any], current_order: Dict[str, Any]) -> bool:
        """Check if an order has been modified"""
        # Compare key fields that indicate modification
        fields_to_compare = ['price_open', 'sl', 'tp', 'volume', 'time_expiration']
        
        for field in fields_to_compare:
            prev_value = prev_order.get(field)
            current_value = current_order.get(field)
            
            # Handle None values and string comparisons
            if str(prev_value) != str(current_value):
                return True
        
        return False
    
    def get_source_order_changes(self, current_orders: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Detect changes in source orders since last run"""
        changes = {
            'new_orders': [],
            'modified_orders': [],
            'removed_orders': []
        }
        
        # Get previous source orders
        previous_orders = self.state['source_orders']
        current_orders_dict = {str(order['ticket']): order for order in current_orders}
        
        # Find new orders
        for ticket_str, order in current_orders_dict.items():
            if ticket_str not in previous_orders:
                changes['new_orders'].append(order)
        
        # Find modified and removed orders
        for ticket_str, prev_order in previous_orders.items():
            if ticket_str in current_orders_dict:
                current_order = current_orders_dict[ticket_str]
                
                # Check for modifications
                if self._order_modified(prev_order, current_order):
                    changes['modified_orders'].append({
                        'previous': prev_order,
                        'current': current_order
                    })
            else:
                changes['removed_orders'].append(prev_order)
        
        return changes
    
    def get_matching_target_orders(self, source_ticket: int, terminal_name: str) -> List[Dict[str, Any]]:
        """Get target orders that match a source ticket (by magic number)"""
        matching_orders = []
        target_orders = self.state['target_orders'].get(terminal_name, {})
        
        for ticket_str, order in target_orders.items():
            if order.get('magic') == source_ticket:
                matching_orders.append(order)
        
        return matching_orders
    
    def cleanup_state(self, active_terminals: List[str]) -> None:
        """Clean up state for terminals that are no longer active"""
        # Clean up target orders
        terminals_to_remove = []
        for terminal_name in self.state['target_orders'].keys():
            if terminal_name not in active_terminals:
                terminals_to_remove.append(terminal_name)
        
        for terminal_name in terminals_to_remove:
            del self.state['target_orders'][terminal_name]
            self.logger.info(f"Cleaned up target orders for inactive terminal: {terminal_name}")
        
        # Clean up orphan checks
        terminals_to_remove = []
        for terminal_name in self.state['orphan_checks'].keys():
            if terminal_name not in active_terminals:
                terminals_to_remove.append(terminal_name)
        
        for terminal_name in terminals_to_remove:
            del self.state['orphan_checks'][terminal_name]
            self.logger.info(f"Cleaned up orphan checks for inactive terminal: {terminal_name}")
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get overall system statistics"""
        stats = {
            'last_run': self.state.get('last_run'),
            'total_source_orders': len(self.state['source_orders']),
            'terminals': {},
            'total_orphan_checks': 0
        }
        
        for terminal_name in self.state['target_orders'].keys():
            terminal_stats = {
                'target_orders': len(self.state['target_orders'].get(terminal_name, {})),
                'orphan_checks': len(self.state['orphan_checks'].get(terminal_name, {})),
                'orphan_stats': self.get_orphan_statistics(terminal_name)
            }
            stats['terminals'][terminal_name] = terminal_stats
            stats['total_orphan_checks'] += terminal_stats['orphan_checks']
        
        return stats
    
    def export_state(self, export_file: str) -> bool:
        """Export current state to a different file"""
        try:
            with open(export_file, 'w') as f:
                json.dump(self.state, f, indent=2, default=str)
            self.logger.info(f"Exported state to {export_file}")
            return True
        except Exception as e:
            self.logger.error(f"Error exporting state: {format_error_message(e)}")
            return False
    
    def import_state(self, import_file: str) -> bool:
        """Import state from a different file"""
        try:
            if not os.path.exists(import_file):
                self.logger.error(f"Import file does not exist: {import_file}")
                return False
            
            with open(import_file, 'r') as f:
                imported_state = json.load(f)
                self.state.update(imported_state)
            
            self.logger.info(f"Imported state from {import_file}")
            return True
        except Exception as e:
            self.logger.error(f"Error importing state: {format_error_message(e)}")
            return False