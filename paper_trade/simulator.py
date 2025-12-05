# paper_trade/simulator.py - COMPOUNDING & SMALL CAPITAL VERSION
import ccxt
import pandas as pd
import time
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from config.api_config import api_config


class PaperTradingSimulator:
    def __init__(self, strategy, initial_balance=None, compounding=True):
        """
        Initialize Paper Trading Simulator dengan support compounding
        
        Args:
            strategy: Trading strategy instance
            initial_balance: Starting balance (default from settings)
            compounding: True untuk reinvest semua profit (compounding mode)
        """
        self.strategy = strategy
        self.compounding = compounding
        
        if initial_balance is None:
            self.initial_balance = settings.PAPER_INITIAL_BALANCE
        else:
            self.initial_balance = initial_balance
            
        self.balance = self.initial_balance
        self.position = 0
        self.position_entry = 0
        self.trade_count = 0
        self.stop_loss_pct = settings.DEFAULT_STOP_LOSS * 100
        self.symbol_base = None
        self.trades = []
        self._trade_logs = []
        self.total_profit_loss = 0
        self.winning_trades = 0
        self.losing_trades = 0
        
        # Setup exchange
        try:
            self.exchange = ccxt.bitget({
                'apiKey': api_config.BITGET_API_KEY,
                'secret': api_config.BITGET_SECRET,
                'password': api_config.BITGET_PASSPHRASE,
                'options': {'defaultType': 'spot'},
                'enableRateLimit': True,
                'timeout': 15000
            })
            
            if api_config.USE_TESTNET:
                print("📡 Connected to Bitget TESTNET")
            else:
                print("⚠️  LIVE TRADING MODE - BE CAREFUL!")
                
        except Exception as e:
            print(f"⚠️  Exchange connection error: {e}")
            self.exchange = None
    
    def run(self, symbol='NXPC/USDT', timeframe='1h', days=7):
        """Run paper trading simulation dengan support compounding"""
        print(f"\n📝 PAPER TRADING: {symbol} {timeframe}")
        print(f"💰 Initial Balance: ${self.balance:.2f}")
        print(f"🤖 Strategy: {self.strategy.name}")
        print(f"📉 Stop Loss: {self.stop_loss_pct:.1f}%")
        print(f"🔄 Compounding: {'ENABLED ✅' if self.compounding else 'DISABLED'}")
        print("-" * 50)
        
        # Reset
        self.position = 0
        self.position_entry = 0
        self.trade_count = 0
        self.total_profit_loss = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.trades = []
        self._trade_logs = []
        
        # 1. Fetch historical data
        print(f"\n📥 Downloading {days} days of data...")
        
        download_start = time.time()
        
        try:
            print("   Download [", end="", flush=True)
            
            if self.exchange:
                self.exchange.timeout = 20000
                ohlcv = self.exchange.fetch_ohlcv(
                    symbol, 
                    timeframe, 
                    limit=days * 24
                )
                
                for i in range(10):
                    time.sleep(0.05)
                    print("=", end="", flush=True)
                
                print(f"] ✅ ({time.time() - download_start:.1f}s)")
                
                if ohlcv and len(ohlcv) > 50:
                    print(f"   Downloaded {len(ohlcv)} candles")
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    df.set_index('timestamp', inplace=True)
                else:
                    print(f"   ⚠️  Insufficient data: {len(ohlcv) if ohlcv else 0} candles")
                    df = self._generate_fallback_data(days)
            
            else:
                df = self._generate_fallback_data(days)
                
        except Exception as e:
            print(f"] ❌ ERROR: {type(e).__name__}")
            df = self._generate_fallback_data(days)
        
        print(f"✅ Ready: {len(df)} candles for simulation")
        
        # 2. Accelerated simulation
        print(f"\n🚀 Starting accelerated simulation...")
        
        total_candles = len(df)
        start_idx = max(settings.SMA_SLOW, 50)  # Pastikan cukup data untuk SMA slow
        
        if total_candles <= start_idx:
            print(f"⚠️  Not enough data (need {start_idx}, have {total_candles})")
            self._print_results()
            return
        
        candles_to_process = total_candles - start_idx
        print(f"   Processing {candles_to_process} candles")
        
        # Progress bar
        print("   Simulation: [", end="", flush=True)
        
        progress_markers = 20
        progress_interval = max(1, candles_to_process // progress_markers)
        next_progress_marker = start_idx + progress_interval
        
        for i in range(start_idx, total_candles):
            current_data = df.iloc[:i+1]
            current_price = current_data['close'].iloc[-1]
            
            # Check stop loss
            if self.position > 0:
                current_profit_pct = ((current_price / self.position_entry) - 1) * 100
                
                # Stop Loss Condition
                if current_profit_pct <= -self.stop_loss_pct:
                    self._execute_sell(current_price, reason="STOP_LOSS", add_to_trade_list=False)
                    # Update progress
                    if i >= next_progress_marker:
                        print("=", end="", flush=True)
                        next_progress_marker += progress_interval
                    continue
            
            try:
                df_with_signals = self.strategy.generate_signals(current_data)
                latest_signal = df_with_signals['signal'].iloc[-1]
                
                # Execute based on signal
                if latest_signal == 1 and self.position == 0:
                    self._execute_buy(current_price, symbol.split('/')[0], add_to_trade_list=False)
                elif latest_signal == -1 and self.position > 0:
                    self._execute_sell(current_price, reason="SIGNAL", add_to_trade_list=False)
                    
            except Exception as e:
                pass
            
            # Update progress bar
            if i >= next_progress_marker:
                print("=", end="", flush=True)
                next_progress_marker += progress_interval
        
        print("] 100%", flush=True)
        
        # Tampilkan semua trades
        if self._trade_logs:
            print("\n📊 TRADE EXECUTIONS:")
            for log in self._trade_logs:
                print(log)
        
        # Final sell jika masih ada position
        if self.position > 0:
            final_price = df['close'].iloc[-1]
            self._execute_sell(final_price, reason="END_SIMULATION", add_to_trade_list=True)
        
        # Final results
        self._print_results()
    
    def _generate_fallback_data(self, days):
        """Generate fallback data yang lebih realistic untuk small capital"""
        import numpy as np
        
        n_candles = days * 24
        base_price = 0.45
        
        # Generate returns yang lebih volatile untuk crypto small cap
        returns = np.random.normal(0.002, 0.03, n_candles)  # Lebih volatile
        prices = base_price * np.exp(np.cumsum(returns))
        
        fallback_data = []
        current_time = int(time.time() * 1000) - (n_candles * 3600000)
        
        for i in range(n_candles):
            timestamp = current_time + (i * 3600000)
            close_price = prices[i]
            open_price = close_price * (1 + np.random.normal(0, 0.015))  # Spread lebih besar
            high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, 0.02)))
            low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, 0.02)))
            volume = 5000 + np.random.normal(0, 3000)  # Volume lebih kecil untuk small cap
            
            fallback_data.append([
                timestamp,
                open_price,
                high_price,
                low_price,
                close_price,
                abs(volume)
            ])
        
        df = pd.DataFrame(fallback_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        print(f"   Generated {len(fallback_data)} fallback candles (small cap simulation)")
        return df
    
    def _execute_buy(self, price, symbol_base, add_to_trade_list=True):
        """Execute buy order dengan support compounding & small capital"""
        # Calculate position size berdasarkan compounding mode
        if self.compounding:
            # Compounding mode: pakai persentase dari CURRENT balance
            position_size_pct = settings.MAX_POSITION_SIZE  # 95% dari current balance
            trade_amount = self.balance * position_size_pct
        else:
            # Non-compounding: pakai persentase dari INITIAL balance
            position_size_pct = 0.95  # 95% dari initial balance (untuk backward compatibility)
            trade_amount = self.initial_balance * position_size_pct
        
        # Hitung amount
        amount = trade_amount / price
        
        # Check minimum trade size
        if amount * price < settings.MIN_TRADE_SIZE:
            if add_to_trade_list:
                print(f"⚠️  Trade too small: ${amount * price:.2f} < ${settings.MIN_TRADE_SIZE} minimum")
            return False
            
        self.position = amount
        self.position_entry = price
        self.balance -= amount * price
        self.symbol_base = symbol_base
        self.trade_count += 1
        
        trade_msg = f"[{datetime.now().strftime('%H:%M:%S')}] " \
                   f"📈 BUY {amount:.4f} {self.symbol_base} @ ${price:.4f} " \
                   f"(Cost: ${amount * price:.2f}, Balance: ${self.balance:.2f})"
        
        if add_to_trade_list:
            print(trade_msg)
        else:
            self._trade_logs.append(trade_msg)
        
        # Record trade
        trade_record = {
            'timestamp': datetime.now(),
            'action': 'BUY',
            'price': price,
            'amount': amount,
            'cost': amount * price,
            'balance': self.balance,
            'entry_price': price,
            'symbol': self.symbol_base
        }
        self.trades.append(trade_record)
        
        return True
    
    def _execute_sell(self, price, reason="SIGNAL", add_to_trade_list=True):
        """Execute sell order dengan tracking profit/loss"""
        if self.position == 0:
            return False
            
        # Calculate profit/loss
        profit_pct = ((price / self.position_entry) - 1) * 100
        revenue = self.position * price
        cost = self.position * self.position_entry
        profit_loss_amount = revenue - cost
        
        # Update balance
        self.balance += revenue
        
        # Update statistics
        self.total_profit_loss += profit_loss_amount
        if profit_loss_amount > 0:
            self.winning_trades += 1
        elif profit_loss_amount < 0:
            self.losing_trades += 1
        
        self.trade_count += 1
        
        reason_emoji = ""
        if reason == "STOP_LOSS":
            reason_emoji = "⛔ "
        elif reason == "END_SIMULATION":
            reason_emoji = "🏁 "
        elif reason == "SIGNAL":
            reason_emoji = "📊 "
        
        color = "🟢" if profit_pct >= 0 else "🔴"
        
        trade_msg = f"[{datetime.now().strftime('%H:%M:%S')}] " \
                   f"📉 {reason_emoji}SELL {self.position:.4f} " \
                   f"{getattr(self, 'symbol_base', '')} @ ${price:.4f} " \
                   f"{color} {profit_pct:+.2f}% " \
                   f"(Balance: ${self.balance:.2f})"
        
        if add_to_trade_list:
            print(trade_msg)
        else:
            self._trade_logs.append(trade_msg)
        
        # Record trade
        trade_record = {
            'timestamp': datetime.now(),
            'action': 'SELL',
            'price': price,
            'amount': self.position,
            'revenue': revenue,
            'profit_pct': profit_pct,
            'profit_loss': profit_loss_amount,
            'reason': reason,
            'balance': self.balance,
            'entry_price': self.position_entry,
            'symbol': self.symbol_base
        }
        self.trades.append(trade_record)
        
        # Reset position
        self.position = 0
        self.position_entry = 0
        
        return True
    
    def _print_results(self):
        """Print paper trading results dengan detail compounding"""
        current_value = self.balance + (self.position * getattr(self, 'position_entry', 0))
        total_return_pct = ((current_value / self.initial_balance) - 1) * 100
        
        print("\n" + "="*60)
        print("📊 PAPER TRADING RESULTS - COMPOUNDING MODE")
        print("="*60)
        print(f"💰 Initial Balance:    ${self.initial_balance:.2f}")
        print(f"💰 Final Balance:      ${current_value:.2f}")
        
        result_emoji = "🟢" if total_return_pct >= 0 else "🔴"
        print(f"📈 Total Return:       {result_emoji} {total_return_pct:+.2f}%")
        
        # Compounding metrics
        if self.compounding:
            print(f"🔄 Compounding:        ENABLED ✅")
            print(f"   Position Size:      {settings.MAX_POSITION_SIZE*100:.0f}% of balance")
        
        print(f"🔢 Total Trades:       {self.trade_count}")
        
        # Win/Loss stats
        if self.trade_count > 0:
            win_rate = (self.winning_trades / self.trade_count) * 100
            loss_rate = (self.losing_trades / self.trade_count) * 100
            
            print(f"\n📊 TRADE STATISTICS:")
            print(f"   Winning Trades:     {self.winning_trades} ({win_rate:.1f}%)")
            print(f"   Losing Trades:      {self.losing_trades} ({loss_rate:.1f}%)")
            print(f"   Total P&L:          ${self.total_profit_loss:+.2f}")
            
            # Average win/loss
            if self.winning_trades > 0:
                avg_win = (self.total_profit_loss / self.winning_trades) if self.total_profit_loss > 0 else 0
                print(f"   Avg Win:            ${avg_win:+.2f}")
            
            # Risk metrics
            print(f"\n⚖️  RISK METRICS:")
            print(f"   Stop Loss:          {self.stop_loss_pct:.1f}%")
            print(f"   Min Trade Size:     ${settings.MIN_TRADE_SIZE}")
        
        print(f"🤖 Strategy:           {self.strategy.name}")
        print("="*60)
        
        # Additional compounding projection
        if self.compounding and total_return_pct > 0:
            self._print_compounding_projection(total_return_pct)
    
    def _print_compounding_projection(self, daily_return_pct):
        """Print compounding projection"""
        print(f"\n📈 COMPOUNDING PROJECTION (based on this run):")
        print("-" * 45)
        
        # Estimate daily return (asumsi run ini adalah 1 hari)
        estimated_daily_return = daily_return_pct / 30  # Asumsi 30 hari
        
        initial_nxpc = self.initial_balance / 0.45  # Asumsi harga $0.45
        current_nxpc = self.balance / 0.45
        
        print(f"   Initial:            {initial_nxpc:.1f} NXPC")
        print(f"   Current:            {current_nxpc:.1f} NXPC")
        print(f"   Est. Daily Return:  {estimated_daily_return:+.2f}%")
        
        # 7-day projection
        if estimated_daily_return > 0:
            for days in [7, 15, 30]:
                projected = initial_nxpc * ((1 + estimated_daily_return/100) ** days)
                growth_pct = ((projected / initial_nxpc) - 1) * 100
                print(f"   {days} days:           {projected:.1f} NXPC ({growth_pct:+.1f}%)")
    
    def get_performance_summary(self):
        """Get performance summary untuk reporting"""
        current_value = self.balance + (self.position * getattr(self, 'position_entry', 0))
        total_return_pct = ((current_value / self.initial_balance) - 1) * 100
        
        return {
            'initial_balance': self.initial_balance,
            'final_balance': current_value,
            'total_return_pct': total_return_pct,
            'trade_count': self.trade_count,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'total_profit_loss': self.total_profit_loss,
            'stop_loss_pct': self.stop_loss_pct,
            'compounding_enabled': self.compounding,
            'strategy': self.strategy.name,
            'win_rate': (self.winning_trades / self.trade_count * 100) if self.trade_count > 0 else 0
        }


# Export the class
__all__ = ['PaperTradingSimulator']