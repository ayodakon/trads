from config.settings import settings
# backtest/optimizer.py
"""
Strategy parameter optimization
"""
import pandas as pd
import numpy as np
from itertools import product
import warnings
warnings.filterwarnings('ignore')

from config import settings
from data.fetcher import DataFetcher
from strategies.sma_crossover import SMACrossover
from backtest.engine import BacktestEngine

class StrategyOptimizer:
    def __init__(self, data_fetcher=None):
        self.fetcher = data_fetcher or DataFetcher()
        self.results = []
    
    def optimize_sma(self, df=None, fast_range=None, slow_range=None):
        """
        Optimize SMA parameters
        """
        print("🔍 OPTIMIZING SMA PARAMETERS")
        print("="*50)
        
        # Load data if not provided
        if df is None:
            df = self.fetcher.fetch_historical_data(
                days_back=60,
                save_csv=False
            )
        
        if df.empty:
            print("❌ No data available for optimization")
            return pd.DataFrame()
        
        # Parameter ranges
        fast_range = fast_range or range(5, 51, 5)  # 5 to 50 step 5
        slow_range = slow_range or range(20, 101, 10)  # 20 to 100 step 10
        
        self.results = []
        
        total_combinations = len(fast_range) * len(slow_range)
        current = 0
        
        for fast, slow in product(fast_range, slow_range):
            if slow <= fast:  # Skip invalid combinations
                continue
            
            current += 1
            print(f"Testing SMA({fast:2}/{slow:3}) "
                  f"[{current}/{total_combinations}]", end="\r")
            
            try:
                # Create strategy and backtest
                strategy = SMACrossover(fast_period=fast, slow_period=slow)
                backtester = BacktestEngine()
                
                result = backtester.run(df, strategy)
                
                # Collect metrics
                self.results.append({
                    'fast_period': fast,
                    'slow_period': slow,
                    'total_return': result['total_return_pct'],
                    'total_trades': result['total_trades'],
                    'win_rate': result['win_rate'],
                    'max_drawdown': result['max_drawdown'],
                    'sharpe_ratio': result['sharpe_ratio'],
                    'profit_factor': result['profit_factor'],
                    'final_equity': result['final_equity']
                })
                
            except Exception as e:
                print(f"\n⚠️  Error with SMA({fast}/{slow}): {e}")
                continue
        
        print("\n" + "="*50)
        
        if not self.results:
            print("❌ No valid results!")
            return pd.DataFrame()
        
        # Convert to DataFrame
        results_df = pd.DataFrame(self.results)
        
        # Display top results
        self.display_top_results(results_df)
        
        # Save results
        self.save_optimization_results(results_df)
        
        return results_df
    
    def display_top_results(self, results_df, top_n=10):
        """Display top N results"""
        print(f"\n🏆 TOP {top_n} PARAMETER COMBINATIONS:")
        print("="*60)
        
        # Sort by return (descending)
        sorted_df = results_df.sort_values('total_return', ascending=False)
        
        print(f"{'Fast':>5} {'Slow':>5} {'Return':>8} {'WinRate':>8} "
              f"{'Drawdown':>10} {'Sharpe':>8} {'Trades':>8}")
        print("-" * 60)
        
        for i, row in sorted_df.head(top_n).iterrows():
            print(f"{row['fast_period']:5} {row['slow_period']:5} "
                  f"{row['total_return']:8.2f}% {row['win_rate']:8.1f}% "
                  f"{row['max_drawdown']:10.2f}% {row['sharpe_ratio']:8.2f} "
                  f"{row['total_trades']:8}")
        
        # Best parameters
        best = sorted_df.iloc[0]
        print("\n" + "="*60)
        print("🎯 RECOMMENDED PARAMETERS:")
        print(f"   SMA({best['fast_period']}/{best['slow_period']})")
        print(f"   Expected Return: {best['total_return']:.2f}%")
        print(f"   Win Rate: {best['win_rate']:.1f}%")
        print(f"   Max Drawdown: {best['max_drawdown']:.2f}%")
        print("="*60)
    
    def save_optimization_results(self, results_df):
        """Save optimization results to file"""
        import os
        from datetime import datetime
        
        os.makedirs(settings.RESULTS_DIR, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"optimization_results_{timestamp}.csv"
        filepath = os.path.join(settings.RESULTS_DIR, filename)
        
        results_df.to_csv(filepath, index=False)
        print(f"\n💾 Optimization results saved: {filepath}")
    
    def plot_optimization_heatmap(self, results_df):
        """Create heatmap of optimization results"""
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            # Pivot data for heatmap
            pivot_data = results_df.pivot_table(
                index='fast_period',
                columns='slow_period',
                values='total_return',
                aggfunc='mean'
            )
            
            plt.figure(figsize=(12, 8))
            sns.heatmap(pivot_data, annot=True, fmt=".1f", cmap="RdYlGn",
                       center=0, cbar_kws={'label': 'Return (%)'})
            
            plt.title('SMA Parameter Optimization Heatmap')
            plt.xlabel('Slow Period')
            plt.ylabel('Fast Period')
            plt.tight_layout()
            
            # Save plot
            import os
            from datetime import datetime
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"optimization_heatmap_{timestamp}.png"
            filepath = os.path.join(settings.RESULTS_DIR, filename)
            
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            print(f"📊 Heatmap saved: {filepath}")
            
            plt.show()
            
        except Exception as e:
            print(f"⚠️  Could not create heatmap: {e}")

if __name__ == "__main__":
    # Test optimizer
    optimizer = StrategyOptimizer()
    df = optimizer.fetcher.fetch_historical_data(days_back=30, save_csv=False)
    
    if not df.empty:
        results = optimizer.optimize_sma(df)
        
        if not results.empty:
            optimizer.plot_optimization_heatmap(results)