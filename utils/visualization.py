# utils/visualization.py - FIX PIE CHART ERROR
"""
Visualization utilities
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime
from config import settings

class ChartBuilder:
    @staticmethod
    def plot_candlestick(df, title="Price Chart", num_candles=100):
        """Create candlestick chart"""
        plot_df = df.tail(num_candles) if len(df) > num_candles else df
        
        fig = go.Figure(data=[go.Candlestick(
            x=plot_df.index,
            open=plot_df['open'],
            high=plot_df['high'],
            low=plot_df['low'],
            close=plot_df['close'],
            name='Price'
        )])
        
        fig.update_layout(
            title=title,
            yaxis_title='Price (USD)',
            xaxis_title='Date',
            template='plotly_dark'
        )
        
        fig.show()
    
    @staticmethod
    def plot_strategy_comparison(strategies_results, benchmark_return=0):
        """Compare multiple strategies"""
        fig = go.Figure()
        
        for strategy_name, results in strategies_results.items():
            if 'equity_curve' in results:
                equity_df = pd.DataFrame(results['equity_curve'])
                
                # Calculate cumulative return
                initial = results.get('initial_capital', 1000)
                equity_df['cumulative_return'] = (equity_df['equity'] / initial - 1) * 100
                
                fig.add_trace(go.Scatter(
                    x=equity_df['timestamp'],
                    y=equity_df['cumulative_return'],
                    mode='lines',
                    name=strategy_name
                ))
        
        # Add benchmark
        if benchmark_return != 0:
            # Simple straight line for benchmark
            fig.add_hline(y=benchmark_return, 
                         line_dash="dash", 
                         line_color="gray",
                         annotation_text=f"Benchmark: {benchmark_return:.1f}%")
        
        fig.update_layout(
            title='Strategy Comparison',
            yaxis_title='Cumulative Return (%)',
            xaxis_title='Date',
            template='plotly_dark',
            hovermode='x unified'
        )
        
        fig.show()
    
    @staticmethod
    def plot_performance_metrics(metrics_dict):
        """Plot performance metrics as bar chart"""
        metrics = list(metrics_dict.keys())
        values = list(metrics_dict.values())
        
        colors = ['green' if v > 0 else 'red' for v in values]
        
        fig = go.Figure(data=[go.Bar(
            x=metrics,
            y=values,
            marker_color=colors,
            text=[f"{v:.2f}" for v in values],
            textposition='auto'
        )])
        
        fig.update_layout(
            title='Performance Metrics',
            yaxis_title='Value',
            template='plotly_dark'
        )
        
        fig.show()
    
    @staticmethod
    def create_dashboard(results, strategy_name="Strategy"):
        """Create comprehensive dashboard - FIXED VERSION"""
        if 'equity_curve' not in results or not results['equity_curve']:
            print("No data for dashboard")
            return
        
        equity_df = pd.DataFrame(results['equity_curve'])
        trades_df = pd.DataFrame(results['trades'])
        
        # FIX: Gunakan 2x3 grid dengan tipe plot yang compatible
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('Equity Curve', 'Drawdown',
                          'Trade Returns Distribution', 'Monthly Returns',
                          'Risk Metrics', 'Trade Summary'),
            specs=[
                [{"type": "xy"}, {"type": "xy"}],
                [{"type": "xy"}, {"type": "xy"}],
                [{"type": "xy"}, {"type": "domain"}]  # Last row: xy + pie
            ],
            vertical_spacing=0.1,
            horizontal_spacing=0.1
        )
        
        # 1. Equity Curve (row 1, col 1)
        fig.add_trace(
            go.Scatter(x=equity_df['timestamp'], y=equity_df['equity'],
                      mode='lines', name='Equity', line=dict(color='blue')),
            row=1, col=1
        )
        fig.add_hline(y=results['initial_capital'], line_dash="dash",
                     line_color="red", row=1, col=1)
        
        # 2. Drawdown (row 1, col 2)
        equity_series = pd.Series(equity_df['equity'].values, index=equity_df['timestamp'])
        rolling_max = equity_series.expanding().max()
        drawdown = (rolling_max - equity_series) / rolling_max * 100
        
        fig.add_trace(
            go.Scatter(x=equity_df['timestamp'], y=drawdown,
                      mode='lines', name='Drawdown', 
                      fill='tozeroy', line=dict(color='red')),
            row=1, col=2
        )
        
        # 3. Trade Returns Distribution (row 2, col 1)
        if not trades_df.empty and 'profit_pct' in trades_df.columns:
            sell_trades = trades_df[trades_df['type'].str.contains('SELL')]
            
            if not sell_trades.empty and len(sell_trades) > 1:
                fig.add_trace(
                    go.Histogram(x=sell_trades['profit_pct'],
                                nbinsx=min(20, len(sell_trades)),
                                name='Returns', marker_color='skyblue'),
                    row=2, col=1
                )
                fig.add_vline(x=0, line_dash="dash", line_color="red", row=2, col=1)
        
        # 4. Monthly Returns (row 2, col 2) - jika data cukup
        if len(equity_df) > 30:
            try:
                equity_df_copy = equity_df.copy()
                equity_df_copy['month'] = equity_df_copy['timestamp'].dt.to_period('M')
                monthly = equity_df_copy.groupby('month')['equity'].agg(['first', 'last'])
                monthly['return'] = (monthly['last'] / monthly['first'] - 1) * 100
                
                fig.add_trace(
                    go.Bar(x=monthly.index.astype(str), y=monthly['return'],
                          name='Monthly Returns', marker_color='green'),
                    row=2, col=2
                )
            except:
                pass
        
        # 5. Risk Metrics (text - row 3, col 1)
        risk_text = f"""
        <b>Performance Metrics:</b><br>
        Total Return: {results.get('total_return_pct', 0):+.2f}%<br>
        Win Rate: {results.get('win_rate', 0):.1f}%<br>
        Max Drawdown: {results.get('max_drawdown', 0):.2f}%<br>
        Sharpe Ratio: {results.get('sharpe_ratio', 0):.2f}<br>
        Profit Factor: {results.get('profit_factor', 0):.2f}<br>
        Total Trades: {results.get('total_trades', 0)}
        """
        
        fig.add_trace(
            go.Scatter(x=[0.5], y=[0.5], text=[risk_text],
                      mode='text', name='Metrics', textfont=dict(size=12)),
            row=3, col=1
        )
        fig.update_xaxes(visible=False, range=[0, 1], row=3, col=1)
        fig.update_yaxes(visible=False, range=[0, 1], row=3, col=1)
        
        # 6. Win/Loss Pie Chart (row 3, col 2) - HANYA jika ada trades
        if not trades_df.empty:
            sell_trades = trades_df[trades_df['type'].str.contains('SELL')]
            if len(sell_trades) > 0:
                wins = len(sell_trades[sell_trades['profit_pct'] > 0])
                losses = len(sell_trades) - wins
                
                if wins + losses > 0:
                    fig.add_trace(
                        go.Pie(labels=['Wins', 'Losses'],
                              values=[wins, losses],
                              name='Win/Loss',
                              marker=dict(colors=['lightgreen', 'lightcoral'])),
                        row=3, col=2
                    )
        
        # Update layout
        fig.update_layout(
            height=1000,
            title_text=f"{strategy_name} - Performance Dashboard",
            template='plotly_dark',
            showlegend=True
        )
        
        # Update axis labels
        fig.update_yaxes(title_text="Equity ($)", row=1, col=1)
        fig.update_yaxes(title_text="Drawdown (%)", row=1, col=2)
        fig.update_xaxes(title_text="Return (%)", row=2, col=1)
        fig.update_yaxes(title_text="Frequency", row=2, col=1)
        fig.update_xaxes(title_text="Month", row=2, col=2)
        fig.update_yaxes(title_text="Return (%)", row=2, col=2)
        
        fig.show()
        
        # Save dashboard
        os.makedirs(settings.RESULTS_DIR, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"dashboard_{strategy_name}_{timestamp}.html"
        filepath = os.path.join(settings.RESULTS_DIR, filename)
        
        fig.write_html(filepath)
        print(f"📊 Dashboard saved: {filepath}")

if __name__ == "__main__":
    # Test visualization
    print("ChartBuilder class ready for use")