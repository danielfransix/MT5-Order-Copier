# MT5 Pending Order Copier System - MT5 Connection Handler
# This module handles all MT5 terminal connections and basic operations

import MetaTrader5 as mt5
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from utils import (
    setup_logging, retry_operation, format_error_message,
    get_order_type_name, convert_mt5_time, validate_file_path
)

class MT5Connector:
    """Handles MT5 terminal connections and operations"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or setup_logging()
        self.is_connected = False
        self.current_terminal = None
        self.connection_timeout = 30
        self.max_retries = 3
        self.retry_delay = 5
    
    def connect(self, terminal_config: Dict[str, Any], terminal_name: str = "Unknown") -> bool:
        """Connect to MT5 terminal with given configuration"""
        try:
            self.logger.info(f"Attempting to connect to terminal: {terminal_name}")
            
            # Validate terminal path
            terminal_path = terminal_config.get('MT5_TERMINAL_PATH')
            if terminal_path and not validate_file_path(terminal_path):
                self.logger.warning(f"Terminal executable not found: {terminal_path}")
            
            # Initialize MT5 connection
            if terminal_path:
                if not mt5.initialize(path=terminal_path):
                    self.logger.error(f"Failed to initialize MT5 with path: {terminal_path}")
                    return False
            else:
                if not mt5.initialize():
                    self.logger.error("Failed to initialize MT5")
                    return False
            
            # Login to account
            account = terminal_config['MT5_ACCOUNT']
            password = terminal_config['MT5_PASSWORD']
            server = terminal_config['MT5_SERVER']
            
            login_result = mt5.login(account, password, server)
            if not login_result:
                error_code = mt5.last_error()
                self.logger.error(f"Failed to login to account {account} on {server}: {error_code}")
                mt5.shutdown()
                return False
            
            # Verify connection
            account_info = mt5.account_info()
            if account_info is None:
                self.logger.error("Failed to get account info after login")
                mt5.shutdown()
                return False
            
            self.is_connected = True
            self.current_terminal = terminal_name
            
            self.logger.info(f"Successfully connected to {terminal_name} - Account: {account_info.login}")
            self.logger.info(f"Account balance: {account_info.balance}, Server: {account_info.server}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Exception during connection to {terminal_name}: {format_error_message(e)}")
            self.disconnect()
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from current MT5 terminal"""
        try:
            if self.is_connected:
                self.logger.info(f"Disconnecting from terminal: {self.current_terminal}")
                mt5.shutdown()
                self.is_connected = False
                self.current_terminal = None
                self.logger.info("Successfully disconnected from MT5")
            return True
        except Exception as e:
            self.logger.error(f"Error during disconnect: {format_error_message(e)}")
            return False
    
    def get_pending_orders(self) -> List[Dict[str, Any]]:
        """Retrieve all pending orders from connected terminal"""
        if not self.is_connected:
            raise ConnectionError("Not connected to MT5 terminal")
        
        try:
            # Get all pending orders
            orders = mt5.orders_get()
            if orders is None:
                self.logger.warning("No pending orders found or failed to retrieve orders")
                return []
            
            order_list = []
            for order in orders:
                order_dict = {
                    'ticket': order.ticket,
                    'time_setup': convert_mt5_time(order.time_setup),
                    'time_expiration': convert_mt5_time(order.time_expiration) if order.time_expiration > 0 else None,
                    'type': order.type,
                    'type_name': get_order_type_name(order.type),
                    'state': order.state,
                    'volume_initial': order.volume_initial,
                    'volume_current': order.volume_current,
                    'price_open': order.price_open,
                    'sl': order.sl,
                    'tp': order.tp,
                    'symbol': order.symbol,
                    'comment': order.comment,
                    'magic': order.magic,
                    'position_id': order.position_id
                }
                order_list.append(order_dict)
            
            self.logger.info(f"Retrieved {len(order_list)} pending orders")
            return order_list
            
        except Exception as e:
            self.logger.error(f"Error retrieving pending orders: {format_error_message(e)}")
            raise
    
    def place_order(self, order_request: Dict[str, Any]) -> Tuple[bool, Optional[int], str]:
        """Place a new pending order"""
        if not self.is_connected:
            raise ConnectionError("Not connected to MT5 terminal")
        
        try:
            # Prepare order request
            request = {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": order_request['symbol'],
                "volume": order_request['volume'],
                "type": order_request['type'],
                "price": order_request['price'],
                "magic": order_request.get('magic', 0),
                "comment": order_request.get('comment', "Copied order"),
                "type_time": mt5.ORDER_TIME_GTC,  # Good till cancelled
                "type_filling": self.get_symbol_filling_mode(order_request['symbol'])
            }
            
            # Add optional parameters
            if 'sl' in order_request and order_request['sl'] > 0:
                request['sl'] = order_request['sl']
            
            if 'tp' in order_request and order_request['tp'] > 0:
                request['tp'] = order_request['tp']
            
            if 'expiration' in order_request and order_request['expiration']:
                request['expiration'] = int(order_request['expiration'].timestamp())
                request['type_time'] = mt5.ORDER_TIME_SPECIFIED
            
            # Send order
            result = mt5.order_send(request)
            
            if result is None:
                error_code = mt5.last_error()
                error_msg = f"Failed to send order: {error_code}"
                self.logger.error(error_msg)
                return False, None, error_msg
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                error_msg = f"Order failed with retcode: {result.retcode}, comment: {result.comment}"
                self.logger.error(error_msg)
                return False, None, error_msg
            
            self.logger.info(f"Order placed successfully - Ticket: {result.order}")
            return True, result.order, "Order placed successfully"
            
        except Exception as e:
            error_msg = f"Exception placing order: {format_error_message(e)}"
            self.logger.error(error_msg)
            return False, None, error_msg
    
    def modify_order(self, ticket: int, modifications: Dict[str, Any]) -> Tuple[bool, str]:
        """Modify an existing pending order"""
        if not self.is_connected:
            raise ConnectionError("Not connected to MT5 terminal")
        
        try:
            # Get current order info
            orders = mt5.orders_get(ticket=ticket)
            if not orders:
                error_msg = f"Order {ticket} not found"
                self.logger.error(error_msg)
                return False, error_msg
            
            current_order = orders[0]
            
            # Prepare modification request
            request = {
                "action": mt5.TRADE_ACTION_MODIFY,
                "order": ticket,
                "symbol": current_order.symbol,
                "volume": modifications.get('volume', current_order.volume_initial),
                "price": modifications.get('price', current_order.price_open),
                "sl": modifications.get('sl', current_order.sl),
                "tp": modifications.get('tp', current_order.tp),
                "type_time": current_order.type_time,
                "type_filling": self.get_symbol_filling_mode(current_order.symbol)
            }
            
            # Handle expiration time
            if 'expiration' in modifications:
                if modifications['expiration']:
                    request['expiration'] = int(modifications['expiration'].timestamp())
                    request['type_time'] = mt5.ORDER_TIME_SPECIFIED
                else:
                    request['type_time'] = mt5.ORDER_TIME_GTC
            elif current_order.time_expiration > 0:
                request['expiration'] = current_order.time_expiration
                request['type_time'] = mt5.ORDER_TIME_SPECIFIED
            
            # Send modification
            result = mt5.order_send(request)
            
            if result is None:
                error_code = mt5.last_error()
                error_msg = f"Failed to modify order {ticket}: {error_code}"
                self.logger.error(error_msg)
                return False, error_msg
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                error_msg = f"Order modification failed with retcode: {result.retcode}, comment: {result.comment}"
                self.logger.error(error_msg)
                return False, error_msg
            
            self.logger.info(f"Order {ticket} modified successfully")
            return True, "Order modified successfully"
            
        except Exception as e:
            error_msg = f"Exception modifying order {ticket}: {format_error_message(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def cancel_order(self, ticket: int) -> Tuple[bool, str]:
        """Cancel a pending order"""
        if not self.is_connected:
            raise ConnectionError("Not connected to MT5 terminal")
        
        try:
            # Get order info to determine symbol for filling mode
            order_info = mt5.orders_get(ticket=ticket)
            if not order_info:
                error_msg = f"Order {ticket} not found for cancellation"
                self.logger.error(error_msg)
                return False, error_msg
            
            # Prepare cancellation request
            request = {
                "action": mt5.TRADE_ACTION_REMOVE,
                "order": ticket,
                "type_filling": self.get_symbol_filling_mode(order_info[0].symbol)
            }
            
            # Send cancellation
            result = mt5.order_send(request)
            
            if result is None:
                error_code = mt5.last_error()
                error_msg = f"Failed to cancel order {ticket}: {error_code}"
                self.logger.error(error_msg)
                return False, error_msg
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                error_msg = f"Order cancellation failed with retcode: {result.retcode}, comment: {result.comment}"
                self.logger.error(error_msg)
                return False, error_msg
            
            self.logger.info(f"Order {ticket} cancelled successfully")
            return True, "Order cancelled successfully"
            
        except Exception as e:
            error_msg = f"Exception cancelling order {ticket}: {format_error_message(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get symbol information"""
        if not self.is_connected:
            raise ConnectionError("Not connected to MT5 terminal")
        
        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                self.logger.warning(f"Symbol {symbol} not found")
                return None
            
            return {
                'name': symbol_info.name,
                'digits': symbol_info.digits,
                'point': symbol_info.point,
                'spread': symbol_info.spread,
                'volume_min': symbol_info.volume_min,
                'volume_max': symbol_info.volume_max,
                'volume_step': symbol_info.volume_step,
                'trade_mode': symbol_info.trade_mode,
                'trade_allowed': symbol_info.trade_mode in [0, 2, 4]  # 0=Full, 2=Long only, 4=Full (different broker)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting symbol info for {symbol}: {format_error_message(e)}")
            return None
    
    def get_symbol_filling_mode(self, symbol: str) -> int:
        """Dynamically determine the appropriate filling mode for a symbol"""
        if not self.is_connected:
            raise ConnectionError("Not connected to MT5 terminal")
        
        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                self.logger.warning(f"Could not retrieve symbol info for {symbol}, using default ORDER_FILLING_RETURN")
                return mt5.ORDER_FILLING_RETURN
            
            filling_mode = symbol_info.filling_mode
            
            # Priority: FOK > IOC > RETURN
            if filling_mode & 2:  # ORDER_FILLING_FOK supported
                return mt5.ORDER_FILLING_FOK
            elif filling_mode & 1:  # ORDER_FILLING_IOC supported  
                return mt5.ORDER_FILLING_IOC
            else:  # Default to RETURN
                return mt5.ORDER_FILLING_RETURN
                
        except Exception as e:
            self.logger.error(f"Error determining filling mode for {symbol}: {format_error_message(e)}")
            return mt5.ORDER_FILLING_RETURN
    
    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """Get current account information"""
        if not self.is_connected:
            raise ConnectionError("Not connected to MT5 terminal")
        
        try:
            account_info = mt5.account_info()
            if account_info is None:
                self.logger.error("Failed to get account info")
                return None
            
            return {
                'login': account_info.login,
                'trade_mode': account_info.trade_mode,
                'leverage': account_info.leverage,
                'limit_orders': account_info.limit_orders,
                'margin_so_mode': account_info.margin_so_mode,
                'trade_allowed': account_info.trade_allowed,
                'trade_expert': account_info.trade_expert,
                'margin_mode': account_info.margin_mode,
                'currency_digits': account_info.currency_digits,
                'balance': account_info.balance,
                'credit': account_info.credit,
                'profit': account_info.profit,
                'equity': account_info.equity,
                'margin': account_info.margin,
                'margin_free': account_info.margin_free,
                'margin_level': account_info.margin_level,
                'margin_so_call': account_info.margin_so_call,
                'margin_so_so': account_info.margin_so_so,
                'margin_initial': account_info.margin_initial,
                'margin_maintenance': account_info.margin_maintenance,
                'assets': account_info.assets,
                'liabilities': account_info.liabilities,
                'commission_blocked': account_info.commission_blocked,
                'name': account_info.name,
                'server': account_info.server,
                'currency': account_info.currency,
                'company': account_info.company
            }
            
        except Exception as e:
            self.logger.error(f"Error getting account info: {format_error_message(e)}")
            return None
    
    def check_connection(self) -> bool:
        """Check if connection is still active"""
        try:
            if not self.is_connected:
                return False
            
            # Try to get account info as a connection test
            account_info = mt5.account_info()
            return account_info is not None
            
        except Exception:
            return False
    
    def get_terminal_info(self) -> Optional[Dict[str, Any]]:
        """Get MT5 terminal information"""
        if not self.is_connected:
            raise ConnectionError("Not connected to MT5 terminal")
        
        try:
            terminal_info = mt5.terminal_info()
            if terminal_info is None:
                return None
            
            return {
                'community_account': terminal_info.community_account,
                'community_connection': terminal_info.community_connection,
                'connected': terminal_info.connected,
                'dlls_allowed': terminal_info.dlls_allowed,
                'trade_allowed': terminal_info.trade_allowed,
                'tradeapi_disabled': terminal_info.tradeapi_disabled,
                'email_enabled': terminal_info.email_enabled,
                'ftp_enabled': terminal_info.ftp_enabled,
                'notifications_enabled': terminal_info.notifications_enabled,
                'mqid': terminal_info.mqid,
                'build': terminal_info.build,
                'maxbars': terminal_info.maxbars,
                'codepage': terminal_info.codepage,
                'ping_last': terminal_info.ping_last,
                'community_balance': terminal_info.community_balance,
                'retransmission': terminal_info.retransmission,
                'company': terminal_info.company,
                'name': terminal_info.name,
                'language': terminal_info.language,
                'path': terminal_info.path
            }
            
        except Exception as e:
            self.logger.error(f"Error getting terminal info: {format_error_message(e)}")
            return None
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Retrieve all active positions from connected terminal"""
        if not self.is_connected:
            raise ConnectionError("Not connected to MT5 terminal")
        
        try:
            # Get all positions
            positions = mt5.positions_get()
            if positions is None:
                self.logger.warning("No positions found or failed to retrieve positions")
                return []
            
            position_list = []
            for position in positions:
                position_dict = {
                    'ticket': position.ticket,
                    'time': convert_mt5_time(position.time),
                    'time_update': convert_mt5_time(position.time_update),
                    'type': position.type,
                    'type_name': 'BUY' if position.type == 0 else 'SELL',
                    'volume': position.volume,
                    'price_open': position.price_open,
                    'price_current': position.price_current,
                    'sl': position.sl,
                    'tp': position.tp,
                    'symbol': position.symbol,
                    'comment': position.comment,
                    'magic': position.magic,
                    'identifier': position.identifier,
                    'profit': position.profit,
                    'swap': position.swap
                }
                position_list.append(position_dict)
            
            self.logger.info(f"Retrieved {len(position_list)} active positions")
            return position_list
            
        except Exception as e:
            self.logger.error(f"Error retrieving positions: {format_error_message(e)}")
            raise
    
    def modify_position(self, ticket: int, sl: float = None, tp: float = None) -> Tuple[bool, str]:
        """Modify position TP/SL using TRADE_ACTION_SLTP"""
        if not self.is_connected:
            raise ConnectionError("Not connected to MT5 terminal")
        
        try:
            # Get current position info
            positions = mt5.positions_get(ticket=ticket)
            if not positions:
                error_msg = f"Position {ticket} not found"
                self.logger.error(error_msg)
                return False, error_msg
            
            current_position = positions[0]
            
            # Prepare modification request
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "position": ticket,
                "symbol": current_position.symbol,
                "sl": sl if sl is not None else current_position.sl,
                "tp": tp if tp is not None else current_position.tp,
                "type_filling": self.get_symbol_filling_mode(current_position.symbol)
            }
            
            # Send modification
            result = mt5.order_send(request)
            
            if result is None:
                error_code = mt5.last_error()
                error_msg = f"Failed to modify position {ticket}: {error_code}"
                self.logger.error(error_msg)
                return False, error_msg
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                error_msg = f"Position modification failed with retcode: {result.retcode}, comment: {result.comment}"
                self.logger.error(error_msg)
                return False, error_msg
            
            self.logger.info(f"Position {ticket} modified successfully")
            return True, "Position modified successfully"
            
        except Exception as e:
            error_msg = f"Exception modifying position {ticket}: {format_error_message(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def close_position(self, ticket: int) -> Tuple[bool, str]:
        """Close a position by ticket number"""
        if not self.is_connected:
            raise ConnectionError("Not connected to MT5 terminal")
        
        try:
            # Get current position info
            positions = mt5.positions_get(ticket=ticket)
            if not positions:
                error_msg = f"Position {ticket} not found"
                self.logger.error(error_msg)
                return False, error_msg
            
            position = positions[0]
            
            # Determine opposite order type for closing
            if position.type == 0:  # BUY position
                order_type = mt5.ORDER_TYPE_SELL
            else:  # SELL position
                order_type = mt5.ORDER_TYPE_BUY
            
            # Prepare close request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "position": ticket,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": order_type,
                "type_filling": self.get_symbol_filling_mode(position.symbol),
                "comment": "Orphaned position closure"
            }
            
            # Send close order
            result = mt5.order_send(request)
            
            if result is None:
                error_code = mt5.last_error()
                error_msg = f"Failed to close position {ticket}: {error_code}"
                self.logger.error(error_msg)
                return False, error_msg
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                error_msg = f"Position closure failed with retcode: {result.retcode}, comment: {result.comment}"
                self.logger.error(error_msg)
                return False, error_msg
            
            self.logger.info(f"Position {ticket} closed successfully")
            return True, "Position closed successfully"
            
        except Exception as e:
            error_msg = f"Exception closing position {ticket}: {format_error_message(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure disconnection"""
        self.disconnect()