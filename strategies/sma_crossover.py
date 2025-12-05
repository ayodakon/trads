# strategies/sma_crossover.py - FIXED
"""
Simple Moving Average Crossover Strategy
"""
import pandas as pd
from .base_strategy import BaseStrategy

# Import settings
try:
    from config.settings import settings
except ImportError:
    # Fallback
    class SimpleSettings:
        SMA_FAST = 20
        SMA_SLOW = 50
    
    settings = SimpleSettings()

class SMACrossover(BaseStrategy):
    def __init__(self, fast_period=None, slow_period=None):
        # Akses sebagai OBJECT
        fast = fast_period or settings.SMA_FAST
        slow = slow_period or settings.SMA_SLOW
        
        if slow <= fast:
            slow = fast + 10  # Ensure slow > fast
        
        super().__init__(name=f"SMA_Crossover_{fast}_{slow}")
        
        self.fast_period = fast
        self.slow_period = slow
        
        self.parameters = {
            'fast_period': self.fast_period,
            'slow_period': self.slow_period,
            'strategy_type': 'trend_following'
        }
    
    def generate_signals(self, df):
        """
        Generate buy/sell signals using SMA crossover
        """
        df = df.copy()
        
        # Calculate SMAs
        df['SMA_fast'] = df['close'].rolling(window=self.fast_period).mean()
        df['SMA_slow'] = df['close'].rolling(window=self.slow_period).mean()
        
        # Initialize signal column
        df['signal'] = 0  # 0 = hold, 1 = buy, -1 = sell
        
        # Buy when fast SMA crosses above slow SMA
        df.loc[(df['SMA_fast'] > df['SMA_slow']) & 
               (df['SMA_fast'].shift(1) <= df['SMA_slow'].shift(1)), 'signal'] = 1
        
        # Sell when fast SMA crosses below slow SMA
        df.loc[(df['SMA_fast'] < df['SMA_slow']) & 
               (df['SMA_fast'].shift(1) >= df['SMA_slow'].shift(1)), 'signal'] = -1
        
        # Remove early signals (warmup period)
        df.iloc[:self.slow_period, df.columns.get_loc('signal')] = 0
        
        return df
    
    def plot_signals(self, df, num_candles=200):
        """Plot price, SMAs, and signals"""
        try:
            import matplotlib.pyplot as plt
            
            plot_df = df.tail(num_candles) if len(df) > num_candles else df
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), 
                                          gridspec_kw={'height_ratios': [3, 1]})
            
            # Plot price and SMAs
            ax1.plot(plot_df.index, plot_df['close'], label='Price', 
                    alpha=0.5, linewidth=1, color='black')
            
            if 'SMA_fast' in plot_df.columns:
                ax1.plot(plot_df.index, plot_df['SMA_fast'], 
                        label=f'SMA {self.fast_period}', linewidth=2, color='blue')
            
            if 'SMA_slow' in plot_df.columns:
                ax1.plot(plot_df.index, plot_df['SMA_slow'], 
                        label=f'SMA {self.slow_period}', linewidth=2, color='red')
            
            # Plot buy signals
            buy_signals = plot_df[plot_df['signal'] == 1]
            if not buy_signals.empty:
                ax1.scatter(buy_signals.index, buy_signals['close'],
                          color='green', marker='^', s=100, label='Buy', zorder=5)
            
            # Plot sell signals
            sell_signals = plot_df[plot_df['signal'] == -1]
            if not sell_signals.empty:
                ax1.scatter(sell_signals.index, sell_signals['close'],
                          color='red', marker='v', s=100, label='Sell', zorder=5)
            
            ax1.set_title(f'SMA Crossover Strategy ({self.fast_period}/{self.slow_period})')
            ax1.set_ylabel('Price (USD)')
            ax1.legend(loc='upper left')
            ax1.grid(True, alpha=0.3)
            
            # Plot signal line
            if 'signal' in plot_df.columns:
                ax2.plot(plot_df.index, plot_df['signal'], 
                        drawstyle='steps', linewidth=2, color='purple')
                ax2.set_ylabel('Signal')
                ax2.set_yticks([-1, 0, 1])
                ax2.set_yticklabels(['SELL', 'HOLD', 'BUY'])
                ax2.set_ylim(-1.5, 1.5)
                ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            print(f"⚠️  Could not plot: {e}")