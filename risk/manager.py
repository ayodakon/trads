# risk/manager.py
"""
Risk management system
"""
import numpy as np
from config import settings

class RiskManager:
    def __init__(self, initial_capital=None):
        self.initial_capital = initial_capital or settings.INITIAL_CAPITAL
        self.current_capital = self.initial_capital
        self.positions = []
        self.max_drawdown = 0
        self.consecutive_losses = 0
        
    def calculate_position_size(self, risk_per_trade=None, stop_loss=None):
        """
        Calculate position size based on risk
        """
        risk_per_trade = risk_per_trade or settings.MAX_POSITION_SIZE
        stop_loss = stop_loss or settings.DEFAULT_STOP_LOSS
        
        # Kelly Criterion simplified
        max_position = self.current_capital * risk_per_trade
        
        # Adjust for consecutive losses
        if self.consecutive_losses > 0:
            reduction = 0.5 ** min(self.consecutive_losses, 3)  # Max 87.5% reduction
            max_position *= reduction
        
        return max_position
    
    def update_after_trade(self, trade_result):
        """
        Update risk metrics after a trade
        """
        if trade_result < 0:  # Loss
            self.consecutive_losses += 1
        else:  # Profit
            self.consecutive_losses = 0
        
        # Update capital
        self.current_capital += trade_result
        
        # Calculate drawdown
        drawdown = (self.initial_capital - self.current_capital) / self.initial_capital
        self.max_drawdown = max(self.max_drawdown, drawdown)
    
    def should_stop_trading(self):
        """
        Check if should stop trading due to risk limits
        """
        # Max drawdown exceeded
        if self.max_drawdown > settings.MAX_DRAWDOWN:
            return True, f"Max drawdown exceeded: {self.max_drawdown*100:.1f}%"
        
        # Too many consecutive losses
        if self.consecutive_losses >= 5:
            return True, f"Too many consecutive losses: {self.consecutive_losses}"
        
        # Capital too low
        if self.current_capital < self.initial_capital * 0.5:
            return True, f"Capital below 50%: ${self.current_capital:.2f}"
        
        return False, ""
    
    def get_risk_status(self):
        """Get current risk status"""
        status = {
            'current_capital': self.current_capital,
            'max_drawdown': self.max_drawdown * 100,  # as percentage
            'consecutive_losses': self.consecutive_losses,
            'capital_usage': (self.current_capital / self.initial_capital) * 100
        }
        
        should_stop, reason = self.should_stop_trading()
        status['should_stop'] = should_stop
        status['stop_reason'] = reason
        
        return status
    
    def reset(self):
        """Reset risk manager"""
        self.current_capital = self.initial_capital
        self.positions = []
        self.max_drawdown = 0
        self.consecutive_losses = 0