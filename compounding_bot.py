"""
Simple Binance Compounding Bot for NXPC/USDT
"""
import time
import schedule
from datetime import datetime
from binance.client import Client
import python_binance

class SimpleBinanceBot:
    """Simple compounding bot for Binance"""
    
    def __init__(self, initial_nxpc=15):
        self.client = python_binance.get_client()
        self.symbol = 'NXPCUSDT'
        self.nxpc_balance = initial_nxpc
        self.trade_count = 0
        
        print(f"🤖 Simple Binance Bot Started")
        print(f"   Symbol: {self.symbol}")
        print(f"   Initial NXPC: {self.nxpc_balance}")
        print(f"   Mode: {'TESTNET' if self.client.testnet else 'LIVE'}")
    
    def get_price(self):
        """Get current price"""
        ticker = self.client.get_symbol_ticker(symbol=self.symbol)
        return float(ticker['price'])
    
    def check_and_trade(self):
        """Check market condition and trade"""
        try:
            price = self.get_price()
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            print(f"[{timestamp}] Price: ${price:.4f} | NXPC: {self.nxpc_balance:.2f}")
            
            # Simple strategy: Buy if price drops 1%, Sell if rises 2%
            # This is just an example - replace with your strategy
            self.trade_count += 1
            
            if self.trade_count % 3 == 0:
                print(f"   📊 Market check #{self.trade_count}")
            
            return price
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def run(self, interval_minutes=5):
        """Run bot continuously"""
        print(f"\n🔄 Running every {interval_minutes} minutes")
        print("Press Ctrl+C to stop\n")
        
        # Run immediately once
        self.check_and_trade()
        
        # Schedule
        schedule.every(interval_minutes).minutes.do(self.check_and_trade)
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Bot stopped by user")
            print(f"📈 Final check...")
            price = self.get_price()
            total_value = self.nxpc_balance * price
            print(f"   Final NXPC: {self.nxpc_balance:.2f}")
            print(f"   Final Price: ${price:.4f}")
            print(f"   Total Value: ${total_value:.2f}")

if __name__ == "__main__":
    # Get initial NXPC from account
    try:
        client = python_binance.get_client()
        account = client.get_account()
        for balance in account['balances']:
            if balance['asset'] == 'NXPC':
                initial_nxpc = float(balance['free'])
                print(f"💰 Found {initial_nxpc} NXPC in account")
                break
        else:
            initial_nxpc = 15  # Default
    except:
        initial_nxpc = 15
    
    bot = SimpleBinanceBot(initial_nxpc=initial_nxpc)
    bot.run(interval_minutes=1)  # Check every minute for testing