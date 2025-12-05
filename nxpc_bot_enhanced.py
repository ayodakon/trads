#!/usr/bin/env python3
"""
Enhanced NXPC Trading Bot with RSI + SMA
"""
import time
import schedule
from datetime import datetime
import pandas as pd
from binance.client import Client
import python_binance
import numpy as np

class EnhancedNXPCTradingBot:
    """Enhanced bot dengan RSI + SMA strategy"""
    
    def __init__(self):
        self.client = python_binance.get_client()
        self.symbol = 'NXPCUSDT'
        self.min_notional = 5.0
        self.trades = []
        
        print(f"🚀 ENHANCED NXPC TRADING BOT")
        print(f"   Strategy: SMA20 + RSI14")
        print(f"   Mode: {'TESTNET' if self.client.testnet else 'LIVE'}")
        print("-" * 50)
    
    def calculate_rsi(self, period=14):
        """Calculate RSI indicator"""
        try:
            klines = self.client.get_historical_klines(
                symbol=self.symbol,
                interval='1h',
                limit=period + 1
            )
            
            if len(klines) > period:
                closes = [float(k[4]) for k in klines]
                prices = pd.Series(closes)
                
                # Calculate RSI
                delta = prices.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                
                return rsi.iloc[-1]
            return None
        except:
            return None
    
    def calculate_sma(self, period=20):
        """Calculate Simple Moving Average"""
        try:
            klines = self.client.get_historical_klines(
                symbol=self.symbol,
                interval='1h',
                limit=period
            )
            
            if len(klines) >= period:
                closes = [float(k[4]) for k in klines]
                return sum(closes) / len(closes)
            return None
        except:
            return None
    
    def get_market_data(self):
        """Get comprehensive market data"""
        try:
            # Price
            ticker = self.client.get_symbol_ticker(symbol=self.symbol)
            price = float(ticker['price'])
            
            # 24h stats
            ticker_24h = self.client.get_ticker(symbol=self.symbol)
            change = float(ticker_24h['priceChangePercent'])
            volume = float(ticker_24h['volume'])
            
            # Balance
            account = self.client.get_account()
            nxpc_balance = 0
            usdt_balance = 0
            
            for balance in account['balances']:
                if balance['asset'] == 'NXPC':
                    nxpc_balance = float(balance['free'])
                elif balance['asset'] == 'USDT':
                    usdt_balance = float(balance['free'])
            
            # Indicators
            sma_20 = self.calculate_sma(20)
            rsi_14 = self.calculate_rsi(14)
            
            return {
                'price': price,
                'change': change,
                'volume': volume,
                'nxpc_balance': nxpc_balance,
                'usdt_balance': usdt_balance,
                'sma_20': sma_20,
                'rsi_14': rsi_14,
                'timestamp': datetime.now()
            }
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def enhanced_strategy(self, data):
        """Enhanced strategy dengan RSI + SMA"""
        if not data or not data['sma_20'] or not data['rsi_14']:
            return None
        
        price = data['price']
        sma_20 = data['sma_20']
        rsi_14 = data['rsi_14']
        nxpc_balance = data['nxpc_balance']
        usdt_balance = data['usdt_balance']
        
        signal = None
        reason = ""
        
        # BUY Signal: Price below SMA20 AND RSI < 30 (oversold)
        if price < sma_20 and rsi_14 < 30 and usdt_balance > 10:
            min_value = 5.5
            quantity = min_value / price
            quantity = round(quantity * 10) / 10
            
            if quantity >= 0.1:
                signal = 'BUY'
                reason = f"Price${price:.4f}<SMA20${sma_20:.4f}, RSI{rsi_14:.1f}<30"
                return {'signal': signal, 'quantity': quantity, 'reason': reason}
        
        # SELL Signal: Price above SMA20+2% AND RSI > 70 (overbought)
        elif price > sma_20 * 1.02 and rsi_14 > 70 and nxpc_balance > 1:
            # Sell 30% of position (less aggressive)
            quantity = max(0.1, nxpc_balance * 0.3)
            quantity = round(quantity * 10) / 10
            
            if quantity * price >= self.min_notional:
                signal = 'SELL'
                reason = f"Price${price:.4f}>SMA20+2%${sma_20*1.02:.4f}, RSI{rsi_14:.1f}>70"
                return {'signal': signal, 'quantity': quantity, 'reason': reason}
        
        return None
    
    def run_analysis(self):
        """Run market analysis"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Market Analysis:")
        
        data = self.get_market_data()
        if not data:
            return
        
        # Display
        print(f"   Price: ${data['price']:.4f} ({data['change']:+.2f}%)")
        if data['sma_20']:
            print(f"   SMA20: ${data['sma_20']:.4f}")
        if data['rsi_14']:
            rsi = data['rsi_14']
            status = "OVERSOLD" if rsi < 30 else "OVERBOUGHT" if rsi > 70 else "NEUTRAL"
            print(f"   RSI14: {rsi:.1f} ({status})")
        
        print(f"   Balance: {data['nxpc_balance']:.1f} NXPC, ${data['usdt_balance']:.2f} USDT")
        
        # Check signal
        signal = self.enhanced_strategy(data)
        if signal:
            print(f"\n   🎯 SIGNAL: {signal['signal']}")
            print(f"      Reason: {signal['reason']}")
            print(f"      Quantity: {signal['quantity']} NXPC")
            
            confirm = input(f"\nExecute {signal['signal']}? (y/n): ").strip().lower()
            if confirm == 'y':
                self.execute_trade(signal)
        else:
            print(f"   📊 No trading signal")
    
    def execute_trade(self, signal_data):
        """Execute trade"""
        try:
            signal = signal_data['signal']
            quantity = signal_data['quantity']
            
            if signal == 'BUY':
                order = self.client.order_market_buy(
                    symbol=self.symbol,
                    quantity=quantity
                )
            else:
                order = self.client.order_market_sell(
                    symbol=self.symbol,
                    quantity=quantity
                )
            
            print(f"✅ {signal} EXECUTED!")
            print(f"   Order ID: {order['orderId']}")
            
            # Record
            self.trades.append({
                'time': datetime.now(),
                'signal': signal,
                'quantity': quantity,
                'price': float(order['fills'][0]['price']) if order.get('fills') else 0,
                'id': order['orderId']
            })
            
        except Exception as e:
            print(f"❌ Trade failed: {e}")

if __name__ == "__main__":
    bot = EnhancedNXPCTradingBot()
    
    print("\n🎯 ENHANCED BOT MENU:")
    print("1. Run Analysis Once")
    print("2. Auto-trade (5 min intervals)")
    print("3. Exit")
    
    choice = input("\nSelect: ").strip()
    
    if choice == '1':
        bot.run_analysis()
    elif choice == '2':
        interval = input("Interval minutes (default 5): ").strip()
        interval = int(interval) if interval.isdigit() else 5
        
        print(f"\n🔄 Starting auto-trade every {interval} minutes")
        print("Press Ctrl+C to stop\n")
        
        # Run immediately
        bot.run_analysis()
        
        # Schedule
        schedule.every(interval).minutes.do(bot.run_analysis)
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Bot stopped")
    else:
        print("👋 Goodbye!")
