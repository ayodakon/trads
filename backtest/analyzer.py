# backtest/analyzer.py - ADD MISSING METHOD
"""
Analyze backtest results
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os

# Import settings
try:
    from config.settings import settings
except ImportError:
    # Fallback
    class SimpleSettings:
        RESULTS_DIR = "results"
    
    settings = SimpleSettings()

class ResultAnalyzer:
    def __init__(self, results):
        self.results = results
        self.trades_df = pd.DataFrame(results['trades'])
        self.equity_df = pd.DataFrame(results['equity_curve'])
    
    def generate_report(self):  # ✅ TAMBAH METHOD INI!
        """Generate comprehensive report"""
        report = {}
        
        # Basic metrics
        report['initial_capital'] = self.results['initial_capital']
        report['final_equity'] = self.results['final_equity']
        report['total_return_pct'] = self.results['total_return_pct']
        report['total_return_usd'] = self.results['total_return_usd']
        report['win_rate'] = self.results['win_rate']
        report['max_drawdown'] = self.results['max_drawdown']
        report['sharpe_ratio'] = self.results['sharpe_ratio']
        report['profit_factor'] = self.results['profit_factor']
        
        # Trade analysis
        if not self.trades_df.empty:
            sell_trades = self.trades_df[self.trades_df['type'].str.contains('SELL')]
            
            if not sell_trades.empty:
                report['avg_profit_pct'] = sell_trades['profit_pct'].mean()
                report['best_trade_pct'] = sell_trades['profit_pct'].max()
                report['worst_trade_pct'] = sell_trades['profit_pct'].min()
                report['avg_trade_duration'] = self._calculate_avg_trade_duration()
                report['total_commission'] = self.trades_df['commission'].sum()
        
        return report
    
    def _calculate_avg_trade_duration(self):
        """Calculate average trade duration"""
        if self.trades_df.empty:
            return 0
        
        # Group buy-sell pairs
        durations = []
        buy_time = None
        
        for _, trade in self.trades_df.iterrows():
            if trade['type'] == 'BUY':
                buy_time = trade['timestamp']
            elif 'SELL' in trade['type'] and buy_time:
                sell_time = trade['timestamp']
                duration = (sell_time - buy_time).total_seconds() / 3600  # hours
                durations.append(duration)
                buy_time = None
        
        return np.mean(durations) if durations else 0
    
    def plot_equity_curve(self, save=False):
        """Plot equity curve"""
        if self.equity_df.empty:
            print("No equity data to plot")
            return
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), 
                                      gridspec_kw={'height_ratios': [2, 1]})
        
        # Equity curve
        ax1.plot(self.equity_df['timestamp'], self.equity_df['equity'], 
                linewidth=2, color='blue', label='Equity')
        ax1.axhline(y=self.results['initial_capital'], color='red', 
                   linestyle='--', alpha=0.5, label='Initial Capital')
        
        ax1.set_title('Equity Curve')
        ax1.set_ylabel('Equity (USD)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Drawdown
        equity_series = pd.Series(self.equity_df['equity'].values, 
                                 index=self.equity_df['timestamp'])
        rolling_max = equity_series.expanding().max()
        drawdown = (rolling_max - equity_series) / rolling_max * 100
        
        ax2.fill_between(self.equity_df['timestamp'], 0, drawdown, 
                        color='red', alpha=0.3)
        ax2.plot(self.equity_df['timestamp'], drawdown, 
                color='red', linewidth=1)
        ax2.set_title(f'Drawdown (Max: {self.results["max_drawdown"]:.2f}%)')
        ax2.set_ylabel('Drawdown (%)')
        ax2.set_xlabel('Date')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            os.makedirs(settings.RESULTS_DIR, exist_ok=True)
            filename = f"equity_curve_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(settings.RESULTS_DIR, filename)
            plt.savefig(filepath, dpi=150)
            print(f"📊 Chart saved: {filepath}")
        
        plt.show()
    
    def plot_trade_distribution(self):
        """Plot trade profit distribution"""
        if self.trades_df.empty:
            print("No trade data to plot")
            return
        
        sell_trades = self.trades_df[self.trades_df['type'].str.contains('SELL')]
        
        if sell_trades.empty:
            print("No sell trades to analyze")
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Histogram of returns
        ax1.hist(sell_trades['profit_pct'], bins=20, edgecolor='black', 
                alpha=0.7, color='skyblue')
        ax1.axvline(x=0, color='red', linestyle='--', alpha=0.5)
        ax1.set_title('Trade Return Distribution')
        ax1.set_xlabel('Return (%)')
        ax1.set_ylabel('Frequency')
        ax1.grid(True, alpha=0.3)
        
        # Win/Loss pie chart
        wins = len(sell_trades[sell_trades['profit_pct'] > 0])
        losses = len(sell_trades[sell_trades['profit_pct'] <= 0])
        
        if wins + losses > 0:
            labels = ['Winning Trades', 'Losing Trades']
            sizes = [wins, losses]
            colors = ['lightgreen', 'lightcoral']
            
            ax2.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                   startangle=90, explode=(0.1, 0))
            ax2.set_title(f'Win/Loss Ratio ({wins}W/{losses}L)')
        
        plt.tight_layout()
        plt.show()
    
    def save_results(self, strategy_name="sma_crossover"):
        """Save all results to files"""
        os.makedirs(settings.RESULTS_DIR, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        prefix = f"{strategy_name}_{timestamp}"
        
        # Save trades
        if not self.trades_df.empty:
            trades_file = os.path.join(settings.RESULTS_DIR, f"{prefix}_trades.csv")
            self.trades_df.to_csv(trades_file, index=False)
            print(f"💾 Trades saved: {trades_file}")
        
        # Save equity curve
        if not self.equity_df.empty:
            equity_file = os.path.join(settings.RESULTS_DIR, f"{prefix}_equity.csv")
            self.equity_df.to_csv(equity_file, index=False)
            print(f"💾 Equity curve saved: {equity_file}")
        
        # Save report
        report = self.generate_report()
        report_df = pd.DataFrame([report])
        report_file = os.path.join(settings.RESULTS_DIR, f"{prefix}_report.csv")
        report_df.to_csv(report_file, index=False)
        print(f"💾 Report saved: {report_file}")
        
        return prefix

if __name__ == "__main__":
    # Test analyzer
    print("Testing ResultAnalyzer...")
    
    # Create dummy results
    dummy_results = {
        'initial_capital': 1000,
        'final_equity': 1100,
        'total_return_pct': 10.0,
        'total_return_usd': 100,
        'win_rate': 60.0,
        'max_drawdown': 5.0,
        'sharpe_ratio': 1.5,
        'profit_factor': 2.0,
        'trades': [
            {'timestamp': pd.Timestamp('2024-01-01'), 'type': 'BUY', 'price': 100, 'profit_pct': None},
            {'timestamp': pd.Timestamp('2024-01-02'), 'type': 'SELL', 'price': 110, 'profit_pct': 10.0}
        ],
        'equity_curve': [
            {'timestamp': pd.Timestamp('2024-01-01'), 'equity': 1000},
            {'timestamp': pd.Timestamp('2024-01-02'), 'equity': 1100}
        ]
    }
    
    analyzer = ResultAnalyzer(dummy_results)
    report = analyzer.generate_report()
    print(f"✅ Report generated: {report.keys()}")