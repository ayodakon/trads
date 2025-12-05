# strategies/sma_rsi_combo.py
"""
SMA + RSI Combo Strategy
Buy: SMA Golden Cross AND RSI < 65 (not overbought)
Sell: SMA Death Cross AND RSI > 35 (not oversold)
"""
import pandas as pd
import ta
from .base_strategy import BaseStrategy

class SMA_RSI_Combo(BaseStrategy):
    def __init__(self, sma_fast=50, sma_slow=80, rsi_period=14, 
                 rsi_overbought=65, rsi_oversold=35):
        super().__init__(name=f"SMA{str(sma_fast)}_{str(sma_slow)}_RSI{str(rsi_period)}")
        
        self.sma_fast = sma_fast
        self.sma_slow = sma_slow
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
    
    def generate_signals(self, df):
        df = df.copy()
        
        # SMA
        df['SMA_fast'] = df['close'].rolling(window=self.sma_fast).mean()
        df['SMA_slow'] = df['close'].rolling(window=self.sma_slow).mean()
        
        # RSI
        df['RSI'] = ta.momentum.RSIIndicator(
            close=df['close'], 
            window=self.rsi_period
        ).rsi()
        
        # Base SMA signals
        df['sma_signal'] = 0
        df.loc[df['SMA_fast'] > df['SMA_slow'], 'sma_signal'] = 1
        df.loc[df['SMA_fast'] < df['SMA_slow'], 'sma_signal'] = -1
        
        # Final signals dengan RSI filter
        df['signal'] = 0
        
        # Buy: SMA bullish DAN RSI tidak overbought
        buy_condition = (
            (df['sma_signal'] == 1) & 
            (df['sma_signal'].shift(1) != 1) &  # New signal
            (df['RSI'] < self.rsi_overbought)
        )
        
        # Sell: SMA bearish DAN RSI tidak oversold  
        sell_condition = (
            (df['sma_signal'] == -1) & 
            (df['sma_signal'].shift(1) != -1) &  # New signal
            (df['RSI'] > self.rsi_oversold)
        )
        
        df.loc[buy_condition, 'signal'] = 1
        df.loc[sell_condition, 'signal'] = -1
        
        # Warmup period
        warmup = max(self.sma_slow, self.rsi_period)
        df.iloc[:warmup, df.columns.get_loc('signal')] = 0
        
        return df