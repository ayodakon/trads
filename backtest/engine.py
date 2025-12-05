# backtest/engine.py - COMPLETE VERSION
"""
Backtesting engine
"""
import pandas as pd
import numpy as np
from datetime import datetime
import os

# Import settings
try:
    from config.settings import settings
except ImportError:
    # Fallback
    class SimpleSettings:
        INITIAL_CAPITAL = 1000.0
        COMMISSION = 0.001
        DEFAULT_STOP_LOSS = 0.05
        RESULTS_DIR = "results"
    
    settings = SimpleSettings()

class BacktestEngine:
    def __init__(self, initial_capital=None, commission=None, stop_loss=None):
        # Akses sebagai OBJECT
        self.initial_capital = initial_capital or settings.INITIAL_CAPITAL
        self.commission = commission or settings.COMMISSION
        self.stop_loss = stop_loss or settings.DEFAULT_STOP_LOSS
        
        self.reset()
    
    def reset(self):
        """Reset engine state"""
        self.capital = self.initial_capital
        self.position = 0.0
        self.position_entry_price = 0.0
        self.trades = []
        self.equity_curve = []
        self.current_price = 0.0
    
    def run(self, df, strategy):
        """
        Run backtest with given strategy
        """
        self.reset()
        
        # Get signals from strategy
        df_with_signals = strategy.generate_signals(df)
        
        print(f"📊 Running backtest with {len(df_with_signals)} candles...")
        print(f"💰 Initial Capital: ${self.initial_capital:,.2f}")
        print(f"📉 Stop Loss: {self.stop_loss*100}%")
        
        for idx in range(len(df_with_signals)):
            row = df_with_signals.iloc[idx]
            timestamp = df_with_signals.index[idx]
            self.current_price = row['close']
            
            # Record equity
            current_equity = self.calculate_current_equity()
            self.equity_curve.append({
                'timestamp': timestamp,
                'equity': current_equity,
                'price': self.current_price
            })
            
            # Check stop loss
            stop_loss_triggered = self.check_stop_loss(timestamp)
            
            # Get signal
            signal = -1 if stop_loss_triggered else row['signal']
            
            # Execute trade
            if signal == 1 and self.position == 0:
                self.execute_buy(timestamp, row)
            
            elif signal == -1 and self.position > 0:
                self.execute_sell(timestamp, row, stop_loss_triggered)
        
        # Final results
        return self.calculate_results()
    
    def calculate_current_equity(self):
        """Calculate current total equity"""
        return self.capital + (self.position * self.current_price)
    
    def check_stop_loss(self, timestamp):
        """Check if stop loss is triggered"""
        if self.position > 0 and self.position_entry_price > 0:
            loss_pct = (self.current_price - self.position_entry_price) / self.position_entry_price
            
            if loss_pct <= -self.stop_loss:
                print(f"[{timestamp.strftime('%Y-%m-%d %H:%M')}] "
                      f"⚠️  STOP LOSS at {loss_pct*100:.2f}% loss")
                return True
        
        return False
    
    def execute_buy(self, timestamp, row):
        """Execute buy order"""
        # Calculate position size (use 95% of capital)
        trade_amount = self.capital * 0.95
        self.position = (trade_amount * (1 - self.commission)) / self.current_price
        self.capital -= trade_amount
        self.position_entry_price = self.current_price
        
        trade_record = {
            'timestamp': timestamp,
            'type': 'BUY',
            'price': self.current_price,
            'position': self.position,
            'amount': trade_amount,
            'commission': trade_amount * self.commission,
            'note': 'Regular buy'
        }
        
        self.trades.append(trade_record)
        
        print(f"[{timestamp.strftime('%Y-%m-%d %H:%M')}] "
              f"✅ BUY {self.position:.6f} @ ${self.current_price:,.2f}")
    
    def execute_sell(self, timestamp, row, stop_loss=False):
        """Execute sell order"""
        trade_value = self.position * self.current_price
        proceeds = trade_value * (1 - self.commission)
        self.capital += proceeds
        
        # Calculate profit/loss
        profit_pct = ((self.current_price / self.position_entry_price) - 1) * 100
        profit_usd = (self.current_price - self.position_entry_price) * self.position
        
        trade_type = 'SELL_STOP_LOSS' if stop_loss else 'SELL'
        
        trade_record = {
            'timestamp': timestamp,
            'type': trade_type,
            'price': self.current_price,
            'position': self.position,
            'profit_pct': profit_pct,
            'profit_usd': profit_usd,
            'commission': trade_value * self.commission,
            'note': 'Stop loss' if stop_loss else 'Regular sell'
        }
        
        self.trades.append(trade_record)
        
        action = "STOP LOSS" if stop_loss else "SELL"
        profit_text = f"Loss: {profit_pct:.2f}%" if profit_pct < 0 else f"Profit: {profit_pct:.2f}%"
        
        print(f"[{timestamp.strftime('%Y-%m-%d %H:%M')}] "
              f"{action} {self.position:.6f} @ ${self.current_price:,.2f} "
              f"({profit_text})")
        
        # Reset position
        self.position = 0.0
        self.position_entry_price = 0.0
    
    def calculate_results(self):
        """Calculate performance metrics"""
        final_equity = self.calculate_current_equity()
        
        # Basic metrics
        total_return_pct = ((final_equity / self.initial_capital) - 1) * 100
        total_return_usd = final_equity - self.initial_capital
        
        # Separate trades
        buy_trades = [t for t in self.trades if t['type'] == 'BUY']
        sell_trades = [t for t in self.trades if 'SELL' in t['type']]
        
        # Win rate
        winning_trades = len([t for t in sell_trades if t.get('profit_pct', 0) > 0])
        total_sell_trades = len(sell_trades)
        win_rate = (winning_trades / total_sell_trades * 100) if total_sell_trades > 0 else 0
        
        # Max drawdown
        max_dd = self.calculate_max_drawdown()
        
        # Sharpe ratio (simplified)
        sharpe = self.calculate_sharpe_ratio()
        
        # Profit factor
        profit_factor = self.calculate_profit_factor()
        
        results = {
            'initial_capital': self.initial_capital,
            'final_equity': final_equity,
            'total_return_pct': total_return_pct,
            'total_return_usd': total_return_usd,
            'total_trades': len(self.trades),
            'buy_trades': len(buy_trades),
            'sell_trades': len(sell_trades),
            'win_rate': win_rate,
            'winning_trades': winning_trades,
            'losing_trades': total_sell_trades - winning_trades,
            'max_drawdown': max_dd,
            'sharpe_ratio': sharpe,
            'profit_factor': profit_factor,
            'trades': self.trades,
            'equity_curve': self.equity_curve
        }
        
        return results
    
    def calculate_max_drawdown(self):
        """Calculate maximum drawdown"""
        if not self.equity_curve:
            return 0
        
        equities = [e['equity'] for e in self.equity_curve]
        peak = equities[0]
        max_dd = 0
        
        for equity in equities:
            if equity > peak:
                peak = equity
            
            drawdown = (peak - equity) / peak * 100
            if drawdown > max_dd:
                max_dd = drawdown
        
        return max_dd
    
    def calculate_sharpe_ratio(self):
        """Calculate Sharpe ratio (annualized)"""
        if len(self.equity_curve) < 2:
            return 0
        
        equities = pd.Series([e['equity'] for e in self.equity_curve])
        returns = equities.pct_change().dropna()
        
        if len(returns) < 2 or returns.std() == 0:
            return 0
        
        # Assuming hourly data, annualize with √(365*24)
        sharpe = (returns.mean() / returns.std()) * np.sqrt(365 * 24)
        return sharpe
    
    def calculate_profit_factor(self):
        """Calculate profit factor (gross profit / gross loss)"""
        sell_trades = [t for t in self.trades if 'SELL' in t['type']]
        
        if not sell_trades:
            return 0
        
        total_profit = sum(t.get('profit_usd', 0) for t in sell_trades if t.get('profit_usd', 0) > 0)
        total_loss = abs(sum(t.get('profit_usd', 0) for t in sell_trades if t.get('profit_usd', 0) < 0))
        
        if total_loss == 0:
            return float('inf') if total_profit > 0 else 0
        
        return total_profit / total_loss
    
    def print_results(self, results):
        """Print formatted results"""
        print("\n" + "="*60)
        print("BACKTEST RESULTS")
        print("="*60)
        print(f"Initial Capital: ${results['initial_capital']:,.2f}")
        print(f"Final Equity:    ${results['final_equity']:,.2f}")
        print(f"Total Return:    {results['total_return_pct']:+.2f}% "
              f"(${results['total_return_usd']:+,.2f})")
        print(f"Total Trades:    {results['total_trades']} "
              f"({results['buy_trades']} buys, {results['sell_trades']} sells)")
        print(f"Win Rate:        {results['win_rate']:.1f}% "
              f"({results['winning_trades']}W/{results['losing_trades']}L)")
        print(f"Max Drawdown:    {results['max_drawdown']:.2f}%")
        print(f"Sharpe Ratio:    {results['sharpe_ratio']:.2f}")
        
        pf = results['profit_factor']
        pf_text = f"{pf:.2f}" if pf != float('inf') else "Infinite"
        print(f"Profit Factor:   {pf_text}")
        print("="*60)
        
        # Show recent trades
        if results['trades']:
            print("\nRecent Trades:")
            for trade in results['trades'][-5:]:
                time_str = trade['timestamp'].strftime('%m-%d %H:%M')
                action = trade['type']
                price = trade['price']
                
                if 'SELL' in action:
                    profit = trade.get('profit_pct', 0)
                    color = "🟢" if profit > 0 else "🔴"
                    print(f"  {time_str} - {action:12} @ ${price:,.2f} "
                          f"{color} {profit:+.2f}%")
                else:
                    print(f"  {time_str} - {action:12} @ ${price:,.2f}")

if __name__ == "__main__":
    # Test the engine
    print("Testing Backtest Engine...")
    
    # Create dummy data
    dates = pd.date_range(start='2024-01-01', periods=100, freq='H')
    data = {
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 105,
        'low': np.random.randn(100).cumsum() + 95,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.rand(100) * 1000
    }
    
    df = pd.DataFrame(data, index=dates)
    
    # Create dummy strategy
    class DummyStrategy:
        def generate_signals(self, df):
            df = df.copy()
            df['signal'] = 0
            df.iloc[10, df.columns.get_loc('signal')] = 1  # Buy at index 10
            df.iloc[50, df.columns.get_loc('signal')] = -1  # Sell at index 50
            return df
    
    # Run backtest
    engine = BacktestEngine(initial_capital=1000)
    strategy = DummyStrategy()
    results = engine.run(df, strategy)
    
    engine.print_results(results)
    print("\n✅ Backtest engine test successful!")