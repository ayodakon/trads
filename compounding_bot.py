# compounding_bot.py
"""
COMPOUNDING AUTO-TRADER BOT
Bot akan trade otomatis setiap jam dengan compounding (reinvest semua profit)
Start dengan 15 NXPC (≈$7), target growth compounding 1-2% per hari
"""
import schedule
import time
import json
from datetime import datetime, timedelta
import pandas as pd
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings
from config.api_config import api_config
from strategies.sma_crossover import SMACrossover
from paper_trade.simulator import PaperTradingSimulator
import ccxt


class CompoundingTradingBot:
    def __init__(self, initial_nxpc=15):
        """
        Initialize Compounding Trading Bot
        
        Args:
            initial_nxpc: Starting amount in NXPC (default: 15 NXPC ≈ $7)
        """
        print("\n" + "="*70)
        print("💰 COMPOUNDING AUTO-TRADER BOT - NXPC/USDT")
        print("="*70)
        
        # Initialize strategy
        self.strategy = SMACrossover(
            fast_period=settings.SMA_FAST,
            slow_period=settings.SMA_SLOW
        )
        
        # Get current price untuk konversi NXPC → USD
        self.current_price = self._get_current_price()
        initial_usd = initial_nxpc * self.current_price
        
        print(f"🤖 Strategy: {self.strategy.name}")
        print(f"💰 Initial Capital: {initial_nxpc} NXPC (≈${initial_usd:.2f})")
        print(f"📈 Current Price: ${self.current_price:.4f}")
        print(f"🔄 Compounding: ENABLED (reinvest 100% of profits)")
        print(f"⏰ Trade Frequency: Every hour")
        print(f"📉 Stop Loss: {settings.DEFAULT_STOP_LOSS*100:.1f}%")
        print("="*70)
        
        # Initialize simulator dengan COMPOUNDING MODE
        self.simulator = PaperTradingSimulator(
            strategy=self.strategy,
            initial_balance=initial_usd,
            compounding=True  # ⬅️ COMPOUNDING ENABLED!
        )
        
        # Bot state
        self.running = True
        self.initial_nxpc = initial_nxpc
        self.start_time = datetime.now()
        self.trade_history = []
        self.hourly_balance_log = []
        
        # Performance metrics
        self.daily_profit_loss = 0
        self.daily_trades = 0
        
        print("✅ Bot initialized successfully!")
        print("   Will start trading in 10 seconds...")
        time.sleep(10)
    
    def _get_current_price(self):
        """Get current NXPC/USDT price from exchange"""
        try:
            exchange = ccxt.bitget({
                'apiKey': api_config.BITGET_API_KEY,
                'secret': api_config.BITGET_SECRET,
                'password': api_config.BITGET_PASSPHRASE,
                'options': {'defaultType': 'spot'},
                'enableRateLimit': True,
                'timeout': 10000
            })
            
            ticker = exchange.fetch_ticker(settings.DEFAULT_SYMBOL)
            return ticker['last']
            
        except Exception as e:
            print(f"⚠️  Could not fetch price from exchange: {e}")
            print("   Using fallback price: $0.45")
            return 0.45  # Fallback price
    
    def _fetch_recent_data(self, hours=24):
        """Fetch recent market data untuk analisis"""
        try:
            exchange = ccxt.bitget({
                'apiKey': api_config.BITGET_API_KEY,
                'secret': api_config.BITGET_SECRET,
                'password': api_config.BITGET_PASSPHRASE,
                'options': {'defaultType': 'spot'},
                'enableRateLimit': True,
                'timeout': 15000
            })
            
            # Fetch last 24 hours data (1h timeframe)
            ohlcv = exchange.fetch_ohlcv(
                settings.DEFAULT_SYMBOL,
                settings.DEFAULT_TIMEFRAME,
                limit=hours
            )
            
            if ohlcv and len(ohlcv) > 10:
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                return df
            
        except Exception as e:
            print(f"⚠️  Could not fetch market data: {e}")
        
        return None
    
    def execute_trade_cycle(self):
        """Execute one trade cycle (dipanggil setiap jam)"""
        timestamp = datetime.now()
        print(f"\n[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] 🔄 TRADE CYCLE STARTED")
        print("-" * 60)
        
        try:
            # 1. Get current market data
            df = self._fetch_recent_data(hours=48)  # 48 hours data
            
            if df is None or df.empty:
                print("   ⚠️  No market data available, skipping cycle")
                return
            
            # 2. Get current price
            current_price = self._get_current_price()
            current_balance_nxpc = self.simulator.balance / current_price if current_price > 0 else 0
            
            print(f"   Current Balance: {current_balance_nxpc:.2f} NXPC (${self.simulator.balance:.2f})")
            print(f"   Current Price: ${current_price:.4f}")
            print(f"   Market Data: {len(df)} candles available")
            
            # 3. Generate signals from recent data
            df_with_signals = self.strategy.generate_signals(df)
            latest_signal = df_with_signals['signal'].iloc[-1]
            
            print(f"   Latest Signal: {'BUY 📈' if latest_signal == 1 else 'SELL 📉' if latest_signal == -1 else 'HOLD ⏸️'}")
            
            # 4. Execute trade berdasarkan signal
            trade_executed = False
            
            if latest_signal == 1 and self.simulator.position == 0:
                # BUY SIGNAL
                print("   Executing BUY order...")
                trade_executed = self.simulator._execute_buy(current_price, 'NXPC', add_to_trade_list=True)
                
            elif latest_signal == -1 and self.simulator.position > 0:
                # SELL SIGNAL
                print("   Executing SELL order...")
                trade_executed = self.simulator._execute_sell(current_price, reason="SIGNAL", add_to_trade_list=True)
            
            # 5. Check stop loss jika ada position
            if self.simulator.position > 0:
                current_profit_pct = ((current_price / self.simulator.position_entry) - 1) * 100
                if current_profit_pct <= -settings.DEFAULT_STOP_LOSS * 100:
                    print(f"   ⛔ STOP LOSS triggered: {current_profit_pct:.1f}%")
                    self.simulator._execute_sell(current_price, reason="STOP_LOSS", add_to_trade_list=True)
                    trade_executed = True
            
            # 6. Log trade cycle
            if trade_executed:
                self.daily_trades += 1
                
                # Record trade
                trade_record = {
                    'timestamp': timestamp,
                    'signal': latest_signal,
                    'price': current_price,
                    'balance_nxpc': current_balance_nxpc,
                    'balance_usd': self.simulator.balance,
                    'position': self.simulator.position,
                    'position_entry': self.simulator.position_entry
                }
                self.trade_history.append(trade_record)
            
            # 7. Log hourly balance
            hourly_log = {
                'timestamp': timestamp,
                'balance_nxpc': current_balance_nxpc,
                'balance_usd': self.simulator.balance,
                'price': current_price,
                'position': self.simulator.position > 0
            }
            self.hourly_balance_log.append(hourly_log)
            
            # 8. Print status
            total_return_pct = ((self.simulator.balance / (self.initial_nxpc * 0.45)) - 1) * 100
            print(f"\n   📊 STATUS:")
            print(f"      Total Return: {total_return_pct:+.2f}%")
            print(f"      Today's Trades: {self.daily_trades}")
            print(f"      Total Trades: {self.simulator.trade_count}")
            
            # Auto-save jika ada perubahan
            if trade_executed:
                self._auto_save_state()
            
        except Exception as e:
            print(f"   ❌ ERROR in trade cycle: {e}")
            import traceback
            traceback.print_exc()
        
        print("-" * 60)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 TRADE CYCLE COMPLETED")
    
    def _auto_save_state(self):
        """Auto-save bot state"""
        try:
            # Save hourly log
            if self.hourly_balance_log:
                df_log = pd.DataFrame(self.hourly_balance_log)
                log_file = f"{settings.RESULTS_DIR}/bot_hourly_log_{datetime.now().strftime('%Y%m%d')}.csv"
                df_log.to_csv(log_file, index=False)
            
            # Save trade history
            if self.trade_history:
                df_trades = pd.DataFrame(self.trade_history)
                trades_file = f"{settings.RESULTS_DIR}/bot_trades_{datetime.now().strftime('%Y%m%d')}.csv"
                df_trades.to_csv(trades_file, index=False)
                
        except Exception as e:
            print(f"⚠️  Could not auto-save: {e}")
    
    def generate_daily_report(self):
        """Generate daily performance report"""
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📊 GENERATING DAILY REPORT")
        print("-" * 60)
        
        try:
            # Calculate daily metrics
            current_price = self._get_current_price()
            current_nxpc = self.simulator.balance / current_price if current_price > 0 else 0
            
            # Find today's start balance (from logs)
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_logs = [log for log in self.hourly_balance_log 
                         if log['timestamp'] >= today_start]
            
            if today_logs:
                start_balance = today_logs[0]['balance_nxpc']
                daily_return_pct = ((current_nxpc / start_balance) - 1) * 100
                
                print(f"   📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
                print(f"   📈 Daily Return: {daily_return_pct:+.2f}%")
                print(f"   🔢 Daily Trades: {self.daily_trades}")
                print(f"   📊 Start: {start_balance:.2f} NXPC")
                print(f"   📊 End: {current_nxpc:.2f} NXPC")
                
                # Save daily report
                report = {
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'start_nxpc': start_balance,
                    'end_nxpc': current_nxpc,
                    'daily_return_pct': daily_return_pct,
                    'daily_trades': self.daily_trades,
                    'total_trades': self.simulator.trade_count,
                    'final_balance_usd': self.simulator.balance,
                    'current_price': current_price
                }
                
                report_file = f"{settings.REPORTS_DIR}/daily_report_{datetime.now().strftime('%Y%m%d')}.json"
                with open(report_file, 'w') as f:
                    json.dump(report, f, indent=2)
                
                print(f"   💾 Report saved: {report_file}")
                
                # Reset daily counters
                self.daily_profit_loss = 0
                self.daily_trades = 0
                
            else:
                print("   ⚠️  No data for today yet")
                
        except Exception as e:
            print(f"   ❌ Error generating report: {e}")
        
        print("-" * 60)
    
    def print_bot_status(self):
        """Print current bot status"""
        current_price = self._get_current_price()
        current_nxpc = self.simulator.balance / current_price if current_price > 0 else 0
        
        total_return_pct = ((current_nxpc / self.initial_nxpc) - 1) * 100
        runtime = datetime.now() - self.start_time
        
        print(f"\n🤖 BOT STATUS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        print(f"💰 Balance: {current_nxpc:.2f} NXPC (${self.simulator.balance:.2f})")
        print(f"📈 Total Return: {total_return_pct:+.2f}%")
        print(f"🔢 Total Trades: {self.simulator.trade_count}")
        print(f"⏰ Runtime: {runtime}")
        print(f"📊 Today's Trades: {self.daily_trades}")
        print(f"🎯 Strategy: {self.strategy.name}")
        print(f"🔄 Compounding: ACTIVE")
        print(f"📉 Stop Loss: {settings.DEFAULT_STOP_LOSS*100:.1f}%")
        print("="*60)
    
    def run(self):
        """Run the compounding bot"""
        print(f"\n🚀 STARTING COMPOUNDING AUTO-TRADER BOT")
        print("="*70)
        
        # Schedule jobs
        schedule.every().hour.at(":05").do(self.execute_trade_cycle)  # Trade setiap jam di :05
        schedule.every().day.at("23:55").do(self.generate_daily_report)  # Daily report
        schedule.every(6).hours.do(self.print_bot_status)  # Status update setiap 6 jam
        
        print("✅ Bot scheduled:")
        print("   - Trade execution: Every hour at :05")
        print("   - Daily report: 23:55")
        print("   - Status update: Every 6 hours")
        print("\n📈 BOT IS NOW RUNNING! Press Ctrl+C to stop.")
        print("="*70)
        
        # Initial status
        self.print_bot_status()
        
        # Initial trade cycle
        self.execute_trade_cycle()
        
        # Main loop
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("\n\n🛑 STOPPING BOT...")
                self.running = False
                break
                
            except Exception as e:
                print(f"⚠️  Error in main loop: {e}")
                time.sleep(60)  # Wait 1 minute before retry
        
        # Final shutdown
        self.shutdown()
    
    def shutdown(self):
        """Shutdown bot gracefully"""
        print(f"\n📴 SHUTTING DOWN COMPOUNDING BOT")
        print("="*70)
        
        # Generate final report
        self.generate_daily_report()
        
        # Save final state
        current_price = self._get_current_price()
        final_nxpc = self.simulator.balance / current_price if current_price > 0 else 0
        
        final_report = {
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'initial_nxpc': self.initial_nxpc,
            'final_nxpc': final_nxpc,
            'total_return_pct': ((final_nxpc / self.initial_nxpc) - 1) * 100,
            'total_trades': self.simulator.trade_count,
            'final_balance_usd': self.simulator.balance,
            'runtime_hours': (datetime.now() - self.start_time).total_seconds() / 3600,
            'strategy': self.strategy.name
        }
        
        try:
            final_file = f"{settings.RESULTS_DIR}/bot_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(final_file, 'w') as f:
                json.dump(final_report, f, indent=2)
            
            print(f"💾 Final report saved: {final_file}")
            
        except Exception as e:
            print(f"⚠️  Could not save final report: {e}")
        
        print(f"\n📊 FINAL RESULTS:")
        print(f"   Initial: {self.initial_nxpc} NXPC")
        print(f"   Final: {final_nxpc:.2f} NXPC")
        print(f"   Return: {final_report['total_return_pct']:+.2f}%")
        print(f"   Trades: {self.simulator.trade_count}")
        print(f"   Runtime: {final_report['runtime_hours']:.1f} hours")
        print("="*70)
        print("👋 Bot stopped successfully!")
        print("="*70)


def main():
    """Main function untuk running bot"""
    print("\n" + "="*70)
    print("🚀 COMPOUNDING AUTO-TRADER BOT LAUNCHER")
    print("="*70)
    
    # Check API configuration
    if not api_config.validate_config():
        print("❌ API configuration required!")
        print("\nPlease configure your .env file with Bitget testnet API keys.")
        print("Get keys from: https://testnet.bitget.com")
        return
    
    # Check required packages
    try:
        import schedule
        import pandas as pd
    except ImportError:
        print("❌ Required packages not installed!")
        print("\nInstall required packages:")
        print("pip install schedule pandas")
        return
    
    # Get starting capital
    try:
        initial_nxpc = float(input(f"Starting NXPC amount (default: 15): ") or "15")
    except:
        initial_nxpc = 15
    
    # Confirm settings
    print(f"\n📋 BOT SETTINGS:")
    print(f"   Starting Capital: {initial_nxpc} NXPC")
    print(f"   Strategy: SMA({settings.SMA_FAST}/{settings.SMA_SLOW})")
    print(f"   Stop Loss: {settings.DEFAULT_STOP_LOSS*100:.1f}%")
    print(f"   Compounding: ENABLED")
    print(f"   Trade Frequency: Every hour")
    
    confirm = input("\nStart bot with these settings? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Bot startup cancelled.")
        return
    
    # Create and run bot
    try:
        bot = CompoundingTradingBot(initial_nxpc=initial_nxpc)
        bot.run()
        
    except Exception as e:
        print(f"\n❌ ERROR starting bot: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()