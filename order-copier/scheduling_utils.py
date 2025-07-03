# Scheduling utilities for MT5 Order Copier
# Ported from Claude system for unified scheduling approach

import logging
from datetime import datetime, timedelta

def calculate_next_execution_time(timeframe_str, offset_seconds=0):
    """
    Calculate the next execution time based on a given timeframe.
    Ported from Claude system for unified scheduling.
    
    Args:
        timeframe_str (str): Timeframe string, e.g., "M1", "M5", "H1", etc.
        offset_seconds (int): Offset in seconds from the start of the timeframe
        
    Returns:
        datetime: Next execution time
    """
    # Use system time for scheduling calculations
    now = datetime.now()
    
    if timeframe_str.startswith("M"):
        # Minutes-based timeframe
        minutes = int(timeframe_str[1:])
        current_minute = now.minute
        current_second = now.second
        current_microsecond = now.microsecond
        
        # Calculate minutes until next interval
        minutes_until_next = minutes - (current_minute % minutes)
        if minutes_until_next == minutes and current_second == 0 and current_microsecond == 0:
            minutes_until_next = 0  # We're exactly at an interval
            
        # Calculate target time
        next_time = now + timedelta(minutes=minutes_until_next, seconds=-current_second, microseconds=-current_microsecond)
        next_time = next_time + timedelta(seconds=offset_seconds)
        
    elif timeframe_str.startswith("H"):
        # Hours-based timeframe
        hours = int(timeframe_str[1:])
        current_hour = now.hour
        current_minute = now.minute
        current_second = now.second
        current_microsecond = now.microsecond
        
        # Calculate hours until next interval
        hours_until_next = hours - (current_hour % hours)
        if hours_until_next == hours and current_minute == 0 and current_second == 0 and current_microsecond == 0:
            hours_until_next = 0  # We're exactly at an interval
            
        # Calculate target time
        next_time = now + timedelta(hours=hours_until_next, minutes=-current_minute, seconds=-current_second, microseconds=-current_microsecond)
        next_time = next_time + timedelta(seconds=offset_seconds)
        
    elif timeframe_str.startswith("D"):
        # Days-based timeframe
        days = int(timeframe_str[1:])
        # Reset to start of next day
        next_day = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        next_time = next_day + timedelta(seconds=offset_seconds)
        
    else:
        # Default to 5 minutes if unknown timeframe
        logging.warning(f"Unknown timeframe '{timeframe_str}', defaulting to M5")
        minutes_until_next = 5 - (now.minute % 5)
        next_time = now + timedelta(minutes=minutes_until_next, seconds=-now.second, microseconds=-now.microsecond)
        next_time = next_time + timedelta(seconds=offset_seconds)
    
    return next_time

def get_time_until_next_execution(timeframe_str, offset_seconds=0):
    """
    Get the time remaining until the next scheduled execution.
    
    Args:
        timeframe_str (str): Timeframe string
        offset_seconds (int): Offset in seconds
        
    Returns:
        float: Seconds until next execution
    """
    next_time = calculate_next_execution_time(timeframe_str, offset_seconds)
    now = datetime.now()
    time_diff = (next_time - now).total_seconds()
    return max(0, time_diff)  # Ensure non-negative

def format_next_execution_time(timeframe_str, offset_seconds=0):
    """
    Format the next execution time as a readable string.
    
    Args:
        timeframe_str (str): Timeframe string
        offset_seconds (int): Offset in seconds
        
    Returns:
        str: Formatted next execution time
    """
    next_time = calculate_next_execution_time(timeframe_str, offset_seconds)
    return next_time.strftime("%Y-%m-%d %H:%M:%S")