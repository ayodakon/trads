from config.settings import settings
# setup_live_paper.py
import schedule
import time
from datetime import datetime
import sys
import os
sys.path.append('.')

from config import settings
from strategies.sma_rsi_combo import SMA_RSI_Combo
from paper_trade import PaperTradingSimulator

class LivePaperTrader:
    def __init__(self):
        self.strategy = SMA_RSI_Combo(
            sma_fast=settings.SMA_FAST,
            sma_slow=settings.SMA_SLOW,
            rsi_period=settings.RSI_PERIOD,
            rsi_overbought=settings.RSI_OVERBOUGHT,
            rsi_oversold=settings.RSI_OVERSOLD
        )
        
        self.simulator = PaperTradingSimulator(self.strategy)
        self.running = True
        self.trades_today = 0
        
        print("="*60)
        print("🔄 LIVE PAPER TRADING SYSTEM")
        print("="*60)
        print(f"Strategy: {self.strategy.name}")
        print(f"Symbol: {settings.DEFAULT_SYMBOL}")
        print(f"Timeframe: {settings.DEFAULT_TIMEFRAME}")
        print(f"Balance: ${self.simulator.balance:.2f}")
        print("="*60)
        print("System will check for trades every hour")
        print("Press Ctrl+C to stop")
        print("="*60)
    
    def check_and_trade(self):
        """Check market conditions and execute trades"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🔍 Checking market...")
        
        try:
            # Run mini-simulation dengan data terbaru
            # Untuk simplicity, kita run simulation 1 hari setiap jam
            self.simulator.run(days=1)
            
            # Update daily trade count
            self.trades_today = len([t for t in self.simulator.trades 
                                   if t['timestamp'].date() == datetime.now().date()])
            
            print(f"   Trades today: {self.trades_today}")
            print(f"   Current Balance: ${self.simulator.balance:.2f}")
            
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
    
    def daily_report(self):
        """Generate daily performance report"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 📊 DAILY REPORT")
        print("-"*40)
        
        today_trades = [t for t in self.simulator.trades 
                       if t['timestamp'].date() == datetime.now().date()]
        
        if today_trades:
            buy_trades = [t for t in today_trades if t['action'] == 'BUY']
            sell_trades = [t for t in today_trades if t['action'] == 'SELL']
            
            print(f"   Today's Trades: {len(buy_trades)} BUY, {len(sell_trades)} SELL")
            
            if sell_trades:
                profitable = [t for t in sell_trades if t.get('profit_pct', 0) > 0]
                print(f"   Profitable: {len(profitable)}/{len(sell_trades)}")
        
        print(f"   Current Balance: ${self.simulator.balance:.2f}")
        print(f"   Daily P&L: ${self.simulator.balance - 1000:.2f}")
        print("-"*40)
    
    def run(self):
        """Run the live paper trading system"""
        # Schedule jobs
        schedule.every().hour.at(":00").do(self.check_and_trade)
        schedule.every().day.at("17:00").do(self.daily_report)  # Report setiap sore
        
        print(f"\n✅ Live Paper Trading Started at {datetime.now().strftime('%H:%M:%S')}")
        print("   Will check for trades every hour at :00")
        print("   Daily report at 17:00")
        
        # Initial check
        self.check_and_trade()
        
        # Main loop
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n🛑 Stopping Live Paper Trading...")
                self.running = False
                break
            except Exception as e:
                print(f"⚠️  Error in main loop: {e}")
                time.sleep(60)
        
        # Final report
        self.final_report()
    
    def final_report(self):
        """Generate final report when stopping"""
        print(f"\n{'='*60}")
        print("📈 FINAL LIVE PAPER TRADING REPORT")
        print(f"{'='*60}")
        
        perf = self.simulator.get_performance_summary()
        
        print(f"Start Balance:    $1000.00")
        print(f"Final Balance:    ${perf['final_balance']:.2f}")
        print(f"Total Return:     {perf['total_return_pct']:+.2f}%")
        print(f"Total Trades:     {perf['total_trade_pairs']} pairs")
        print(f"Win Rate:         {perf['win_rate']:.1f}%")
        print(f"Running Time:     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Save to file
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{settings.RESULTS_DIR}/live_paper_final_{timestamp}.txt"
            
            with open(filename, 'w') as f:
                f.write(f"Live Paper Trading Final Report\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Final Balance: ${perf['final_balance']:.2f}\n")
                f.write(f"Total Return: {perf['total_return_pct']:+.2f}%\n")
                f.write(f"Win Rate: {perf['win_rate']:.1f}%\n")
            
            print(f"\n💾 Report saved to: {filename}")
            
        except Exception as e:
            print(f"⚠️  Could not save report: {e}")
        
        print(f"{'='*60}")
        print("🎯 RECOMMENDATION:")
        if perf['total_return_pct'] > 5:
            print("✅ Performance GOOD - Consider small real money test")
        else:
            print("⚠️  Performance MODERATE - Continue paper trading")
        print(f"{'='*60}")

if __name__ == "__main__":
    # Install schedule jika belum: pip install schedule
    try:
        import schedule
    except ImportError:
        print("Installing schedule library...")
        os.system("pip install schedule")
        import schedule
    
    trader = LivePaperTrader()
    trader.run()