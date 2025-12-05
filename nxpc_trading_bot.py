#!/usr/bin/env python3
"""
Simple NXPC/USDT Trading Bot
"""
import time
import schedule
from datetime import datetime
import pandas as pd
from binance.client import Client
import python_binance

class NXPCTradingBot:
    """Trading bot khusus untuk NXPC/USDT"""
    
    def __init__(self):
        self.client = python_binance.get_client()
        self.symbol = 'NXPCUSDT'
        self.min_notional = 5.0  # $5 minimum
        self.min_qty = 0.1  # 0.1 NXPC minimum
        
        # Trading history
        self.trades = []
        self.balance_history = []
        
        print(f"🤖 NXPC/USDT TRADING BOT")
        print(f"   Symbol: {self.symbol}")
        print(f"   Mode: {'TESTNET' if self.client.testnet else 'LIVE'}")
        print(f"   Min Order: ${self.min_notional}")
        print("-" * 50)
    
    def get_current_data(self):
        """Get current market data"""
        try:
            # Get price
            ticker = self.client.get_symbol_ticker(symbol=self.symbol)
            price = float(ticker['price'])
            
            # Get 24h stats
            ticker_24h = self.client.get_ticker(symbol=self.symbol)
            change = float(ticker_24h['priceChangePercent'])
            volume = float(ticker_24h['volume'])
            
            # Get balance
            account = self.client.get_account()
            nxpc_balance = 0
            usdt_balance = 0
            
            for balance in account['balances']:
                if balance['asset'] == 'NXPC':
                    nxpc_balance = float(balance['free'])
                elif balance['asset'] == 'USDT':
                    usdt_balance = float(balance['free'])
            
            return {
                'price': price,
                'change': change,
                'volume': volume,
                'nxpc_balance': nxpc_balance,
                'usdt_balance': usdt_balance,
                'timestamp': datetime.now()
            }
        except Exception as e:
            print(f"❌ Error getting data: {e}")
            return None
    
    def calculate_sma(self, period=20):
        """Calculate Simple Moving Average"""
        try:
            # Get historical klines
            klines = self.client.get_historical_klines(
                symbol=self.symbol,
                interval='1h',
                limit=period
            )
            
            if len(klines) >= period:
                closes = [float(k[4]) for k in klines]
                sma = sum(closes) / len(closes)
                return sma
            return None
        except:
            return None
    
    def trading_strategy(self, data):
        """
        Simple trading strategy:
        - Buy if price < SMA20 and rising
        - Sell if price > SMA20 * 1.02
        """
        sma_20 = self.calculate_sma(20)
        if not sma_20 or not data:
            return None
        
        price = data['price']
        nxpc_balance = data['nxpc_balance']
        usdt_balance = data['usdt_balance']
        
        # Strategy logic
        signal = None
        reason = ""
        
        # BUY signal: Price below SMA and we have USDT
        if price < sma_20 and usdt_balance > 10:
            # Calculate quantity (min $5.50 for safety)
            min_value = 5.5
            quantity = min_value / price
            # Round to nearest 0.1
            quantity = round(quantity * 10) / 10
            
            if quantity >= self.min_qty:
                signal = 'BUY'
                reason = f"Price ${price:.4f} < SMA20 ${sma_20:.4f}"
                return {'signal': signal, 'quantity': quantity, 'reason': reason}
        
        # SELL signal: Price above SMA * 1.02 and we have NXPC
        elif price > sma_20 * 1.02 and nxpc_balance > 1:
            # Sell half of NXPC balance
            quantity = max(self.min_qty, nxpc_balance * 0.5)
            quantity = round(quantity * 10) / 10  # Round to 0.1
            
            if quantity * price >= self.min_notional:
                signal = 'SELL'
                reason = f"Price ${price:.4f} > SMA20+2% ${sma_20*1.02:.4f}"
                return {'signal': signal, 'quantity': quantity, 'reason': reason}
        
        return None
    
    def execute_trade(self, signal_data):
        """Execute trade based on signal"""
        try:
            signal = signal_data['signal']
            quantity = signal_data['quantity']
            reason = signal_data['reason']
            
            print(f"\n🎯 TRADE SIGNAL: {signal}")
            print(f"   Reason: {reason}")
            print(f"   Quantity: {quantity} NXPC")
            
            # Get current price for display
            data = self.get_current_data()
            if not data:
                return False
            
            price = data['price']
            value = quantity * price
            
            print(f"   Price: ${price:.4f}")
            print(f"   Value: ${value:.2f}")
            
            confirm = input(f"\nExecute {signal} order? (y/n): ").strip().lower()
            
            if confirm != 'y':
                print("❌ Trade cancelled")
                return False
            
            # Execute order
            if signal == 'BUY':
                order = self.client.order_market_buy(
                    symbol=self.symbol,
                    quantity=quantity
                )
            else:  # SELL
                order = self.client.order_market_sell(
                    symbol=self.symbol,
                    quantity=quantity
                )
            
            print(f"✅ {signal} ORDER EXECUTED!")
            print(f"   Order ID: {order['orderId']}")
            print(f"   Status: {order['status']}")
            
            # Record trade
            trade = {
                'timestamp': datetime.now(),
                'signal': signal,
                'quantity': quantity,
                'price': price,
                'order_id': order['orderId'],
                'reason': reason
            }
            self.trades.append(trade)
            
            return True
            
        except Exception as e:
            print(f"❌ Trade execution failed: {e}")
            return False
    
    def run_once(self):
        """Run one iteration of trading logic"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking market...")
        
        # Get current data
        data = self.get_current_data()
        if not data:
            return
        
        # Display market info
        print(f"   Price: ${data['price']:.4f} ({data['change']:+.2f}%)")
        print(f"   Volume: {data['volume']:.0f} NXPC")
        print(f"   Balance: {data['nxpc_balance']:.2f} NXPC, ${data['usdt_balance']:.2f} USDT")
        
        # Calculate and show SMA
        sma_20 = self.calculate_sma(20)
        if sma_20:
            print(f"   SMA20: ${sma_20:.4f}")
        
        # Check trading signal
        signal_data = self.trading_strategy(data)
        if signal_data:
            self.execute_trade(signal_data)
        else:
            print("   📊 No trading signal")
    
    def run_continuous(self, interval_minutes=5):
        """Run bot continuously"""
        print(f"\n🔄 Starting continuous trading...")
        print(f"   Interval: {interval_minutes} minutes")
        print(f"   Press Ctrl+C to stop")
        print("-" * 50)
        
        # Run immediately once
        self.run_once()
        
        # Schedule
        schedule.every(interval_minutes).minutes.do(self.run_once)
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Bot stopped by user")
            self.print_summary()
    
    def print_summary(self):
        """Print trading summary"""
        if not self.trades:
            print("📭 No trades executed")
            return
        
        print("\n" + "=" * 50)
        print("📈 TRADING SUMMARY")
        print("=" * 50)
        print(f"Total Trades: {len(self.trades)}")
        
        buy_count = sum(1 for t in self.trades if t['signal'] == 'BUY')
        sell_count = sum(1 for t in self.trades if t['signal'] == 'SELL')
        
        print(f"BUY: {buy_count}, SELL: {sell_count}")
        
        # Show last 5 trades
        if self.trades:
            print(f"\nLast {min(5, len(self.trades))} trades:")
            for trade in self.trades[-5:]:
                time_str = trade['timestamp'].strftime('%H:%M:%S')
                print(f"  [{time_str}] {trade['signal']} {trade['quantity']} NXPC @ ${trade['price']:.4f}")

if __name__ == "__main__":
    bot = NXPCTradingBot()
    
    print("\n🎯 SELECT MODE:")
    print("1. Run once (manual)")
    print("2. Run continuously (auto)")
    print("3. Exit")
    
    choice = input("\nSelect (1-3): ").strip()
    
    if choice == '1':
        bot.run_once()
    elif choice == '2':
        interval = input("Check interval in minutes (default: 5): ").strip()
        interval = int(interval) if interval.isdigit() else 5
        bot.run_continuous(interval_minutes=interval)
    else:
        print("👋 Goodbye!")
