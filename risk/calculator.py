# risk/calculator.py
"""
Risk calculation utilities
"""
import numpy as np
import pandas as pd

class RiskCalculator:
    @staticmethod
    def calculate_var(returns, confidence_level=0.95):
        """
        Calculate Value at Risk (VaR)
        """
        if len(returns) == 0:
            return 0
        
        return np.percentile(returns, (1 - confidence_level) * 100)
    
    @staticmethod
    def calculate_cvar(returns, confidence_level=0.95):
        """
        Calculate Conditional Value at Risk (CVaR)
        """
        if len(returns) == 0:
            return 0
        
        var = RiskCalculator.calculate_var(returns, confidence_level)
        cvar = returns[returns <= var].mean()
        
        return cvar if not np.isnan(cvar) else 0
    
    @staticmethod
    def calculate_volatility(returns, annualize=True):
        """
        Calculate volatility
        """
        if len(returns) == 0:
            return 0
        
        volatility = np.std(returns)
        
        if annualize:
            # Assuming daily data, annualize with √252
            volatility *= np.sqrt(252)
        
        return volatility
    
    @staticmethod
    def calculate_max_drawdown(equity_curve):
        """
        Calculate maximum drawdown
        """
        if len(equity_curve) == 0:
            return 0
        
        equity = pd.Series(equity_curve)
        rolling_max = equity.expanding().max()
        drawdowns = (rolling_max - equity) / rolling_max
        max_drawdown = drawdowns.max()
        
        return max_drawdown * 100  # as percentage
    
    @staticmethod
    def calculate_sharpe_ratio(returns, risk_free_rate=0.02, annualize=True):
        """
        Calculate Sharpe ratio
        """
        if len(returns) == 0 or np.std(returns) == 0:
            return 0
        
        excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free
        sharpe = np.mean(excess_returns) / np.std(excess_returns)
        
        if annualize:
            sharpe *= np.sqrt(252)
        
        return sharpe
    
    @staticmethod
    def calculate_sortino_ratio(returns, risk_free_rate=0.02, annualize=True):
        """
        Calculate Sortino ratio (downside risk only)
        """
        if len(returns) == 0:
            return 0
        
        excess_returns = returns - (risk_free_rate / 252)
        
        # Downside deviation
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0:
            return np.inf if np.mean(excess_returns) > 0 else 0
        
        downside_std = np.std(downside_returns)
        
        if downside_std == 0:
            return np.inf if np.mean(excess_returns) > 0 else 0
        
        sortino = np.mean(excess_returns) / downside_std
        
        if annualize:
            sortino *= np.sqrt(252)
        
        return sortino