#!/usr/bin/env python3
"""
NXPC Trading Bot - Config Based Version
Menggunakan telegram_config.py untuk semua settings
"""
import time
import schedule
import requests
from datetime import datetime
import python_binance
import sys
import os

# Import config
try:
    from telegram_config import (
        TELEGRAM_TOKEN,
        CHAT_ID,
        CHECK_INTERVAL,
        SYMBOL,
        USE_TESTNET,
        TARGET_PROFIT_PERCENT,
        STOP_LOSS_PERCENT,
        COMPOUND_PERCENT
    )
    print("✅ Config loaded successfully")
except ImportError as e:
    print(f"❌ Error loading config: {e}")
    print("   Make sure telegram_config.py exists")
    sys.exit(1)

class NXPCConfigBot:
    """Bot menggunakan config file"""
    
    def __init__(self):
        print("🤖 NXPC TRADING BOT - CONFIG BASED")
        print("=" * 50)
        
        # Load from config
        self.telegram_token = TELEGRAM_TOKEN
        self.chat_id = CHAT_ID
        self.symbol = SYMBOL
        self.use_testnet = USE_TESTNET
        
        # Strategy from config
        self.target_profit = TARGET_PROFIT_PERCENT
        self.stop_loss = STOP_LOSS_PERCENT
        self.compound_percent = COMPOUND_PERCENT
        
        # Telegram enabled check
        self.telegram_enabled = bool(self.telegram_token and self.chat_id)
        
        # Binance client
        self.client = python_binance.get_client(testnet=self.use_testnet)
        
        # State
        self.in_position = False
        self.entry_price = 0
        self.position_size = 0
        self.total_profit = 0
        self.trades = []
        
        # Display config
        print(f"   Symbol: {self.symbol}")
        print(f"   Mode: {'TESTNET' if self.use_testnet else 'LIVE'}")
        print(f"   Telegram: {'✅ ENABLED' if self.telegram_enabled else '❌ DISABLED'}")
        print(f"   Check Interval: {CHECK_INTERVAL} minutes")
        print(f"   Target Profit: {self.target_profit}%")
        print(f"   Stop Loss: {self.stop_loss}%")
        print(f"   Compound: {self.compound_percent}%")
        print("-" * 50)
        
        # Send startup notification
        if self.telegram_enabled:
            self.send_telegram(
                f"🚀 NXPC Trading Bot Started\n"
                f"Mode: {'TESTNET' if self.use_testnet else 'LIVE'}\n"
                f"Symbol: {self.symbol}\n"
                f"Interval: {CHECK_INTERVAL} minutes\n"
                f"Strategy: {self.target_profit}% target, {self.compound_percent}% compounding"
            )
    
    def send_telegram(self, message):
        """Send Telegram message"""
        if not self.telegram_enabled:
            return False
            
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ Telegram sent: {message[:40]}...")
                return True
            else:
                print(f"   ❌ Telegram failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Telegram error: {e}")
            return False
    
    def market_check(self):
        """Market check function"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n[{timestamp}] Market Check")
        print("-" * 40)
        
        try:
            # Get price
            ticker = self.client.get_symbol_ticker(symbol=self.symbol)
            price = float(ticker['price'])
            
            # Get account info
            account = self.client.get_account()
            
            usdt_balance = 0
            nxpc_balance = 0
            
            for balance in account['balances']:
                if balance['asset'] == 'USDT':
                    usdt_balance = float(balance['free'])
                elif balance['asset'] == 'NXPC':
                    nxpc_balance = float(balance['free'])
            
            # Calculate total value
            total_value = usdt_balance + (nxpc_balance * price)
            
            # Display info
            print(f"   Price: ${price:.4f}")
            print(f"   USDT: ${usdt_balance:.2f}")
            print(f"   NXPC: {nxpc_balance:.2f}")
            print(f"   Total: ${total_value:.2f}")
            
            if self.in_position:
                profit_pct = ((price - self.entry_price) / self.entry_price) * 100
                print(f"   Position: {self.position_size:.2f} @ ${self.entry_price:.4f}")
                print(f"   P&L: {profit_pct:+.2f}%")
            
            # Simple trading logic (bisa diganti dengan strategi kompleks)
            if not self.in_position and usdt_balance > 50:
                # Buy logic: jika harga turun 1% dari sebelumnya
                # Ini contoh sederhana, bisa diganti dengan strategi dari main.py
                print("   📊 Checking buy signals...")
                # Implement your strategy here
                print("   No buy signal (demo mode)")
            
            elif self.in_position:
                # Check sell signals
                profit_pct = ((price - self.entry_price) / self.entry_price) * 100
                
                if profit_pct >= self.target_profit:
                    print(f"   🎯 Take Profit signal: {profit_pct:.2f}%")
                elif profit_pct <= -self.stop_loss:
                    print(f"   🛑 Stop Loss signal: {profit_pct:.2f}%")
                else:
                    print(f"   📈 Holding: {profit_pct:+.2f}%")
            
            # Send hourly update to Telegram
            current_minute = datetime.now().minute
            if self.telegram_enabled and current_minute == 0:  # Every hour
                status_msg = (
                    f"⏰ Hourly Update\n"
                    f"Price: ${price:.4f}\n"
                    f"USDT: ${usdt_balance:.2f}\n"
                    f"NXPC: {nxpc_balance:.2f}\n"
                    f"In Position: {'Yes' if self.in_position else 'No'}"
                )
                if self.in_position:
                    profit_pct = ((price - self.entry_price) / self.entry_price) * 100
                    status_msg += f"\nP&L: {profit_pct:+.2f}%"
                
                self.send_telegram(status_msg)
            
            print("-" * 40)
            return True
            
        except Exception as e:
            error_msg = f"❌ Market check error: {e}"
            print(error_msg)
            
            if self.telegram_enabled:
                self.send_telegram(f"⚠️ Market Check Error\n{str(e)[:100]}")
            
            return False
    
    def run_24_7(self):
        """Run bot 24/7"""
        interval = CHECK_INTERVAL
        
        print(f"\n🔄 Starting 24/7 Operation")
        print(f"   Interval: {interval} minutes")
        print(f"   Press Ctrl+C to stop")
        print("=" * 50)
        
        # Initial market check
        self.market_check()
        
        # Schedule periodic checks
        schedule.every(interval).minutes.do(self.market_check)
        
        # Daily summary at 23:00
        schedule.every().day.at("23:00").do(
            lambda: self.send_telegram("📅 Daily summary: Bot is running")
        )
        
        # Keep alive message every 6 hours
        schedule.every(6).hours.do(
            lambda: self.send_telegram("🤖 Bot is alive and monitoring")
        )
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            print("\n\n🛑 Bot stopped by user")
            
            if self.telegram_enabled:
                self.send_telegram("🛑 Bot stopped manually\nUser interrupt")
            
            self.print_summary()
    
    def print_summary(self):
        """Print summary"""
        print("\n" + "=" * 50)
        print("📈 TRADING SUMMARY")
        print("=" * 50)
        print(f"Total Trades: {len(self.trades)}")
        print(f"Total Profit: ${self.total_profit:.2f}")
        print(f"In Position: {'Yes' if self.in_position else 'No'}")
        
        if self.trades:
            print("\nLast 3 trades:")
            for trade in self.trades[-3:]:
                time_str = trade.get('time', 'N/A')
                if hasattr(time_str, 'strftime'):
                    time_str = time_str.strftime('%H:%M:%S')
                print(f"  [{time_str}] {trade.get('type', 'N/A')}")

if __name__ == "__main__":
    print("🤖 LOADING CONFIG BASED BOT...")
    bot = NXPCConfigBot()
    bot.run_24_7()
