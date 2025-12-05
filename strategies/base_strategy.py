# strategies/base_strategy.py
"""
Base class for all trading strategies
"""
from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    """Abstract base class for strategies"""
    
    def __init__(self, name="BaseStrategy"):
        self.name = name
        self.parameters = {}
    
    @abstractmethod
    def generate_signals(self, df):
        """
        Generate trading signals from data
        Returns: DataFrame with 'signal' column
        """
        pass
    
    def calculate_indicators(self, df):
        """Calculate technical indicators (optional)"""
        return df
    
    def plot_signals(self, df):
        """Plot strategy signals (optional)"""
        pass
    
    def get_parameters(self):
        """Get strategy parameters"""
        return self.parameters.copy()
    
    def set_parameters(self, **kwargs):
        """Update strategy parameters"""
        self.parameters.update(kwargs)
        return self