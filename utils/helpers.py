# utils/helpers.py
"""
Helper functions
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

def format_price(price):
    """Format price with commas"""
    return f"${price:,.2f}"

def format_percentage(value):
    """Format percentage"""
    return f"{value:+.2f}%"

def format_time(timestamp):
    """Format timestamp"""
    if isinstance(timestamp, pd.Timestamp):
        return timestamp.strftime('%Y-%m-%d %H:%M')
    return timestamp

def calculate_time_elapsed(start_time):
    """Calculate elapsed time"""
    elapsed = time.time() - start_time
    hours = int(elapsed // 3600)
    minutes = int((elapsed % 3600) // 60)
    seconds = int(elapsed % 60)
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def safe_divide(a, b):
    """Safe division with zero check"""
    return a / b if b != 0 else 0

def calculate_cagr(initial, final, days):
    """Calculate Compound Annual Growth Rate"""
    if initial <= 0 or days <= 0:
        return 0
    
    years = days / 365
    cagr = ((final / initial) ** (1 / years) - 1) * 100
    
    return cagr

def generate_timestamp():
    """Generate timestamp string"""
    return datetime.now().strftime('%Y%m%d_%H%M%S')

def create_dataframe_summary(df, name="DataFrame"):
    """Create summary of DataFrame"""
    summary = {
        'name': name,
        'rows': len(df),
        'columns': len(df.columns),
        'date_range': f"{df.index[0]} to {df.index[-1]}" if len(df) > 0 else "Empty",
        'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB"
    }
    
    return summary