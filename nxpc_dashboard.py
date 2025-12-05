#!/usr/bin/env python3
"""
Simple NXPC Trading Dashboard
"""
import time
from datetime import datetime
import python_binance

def get_dashboard_data():
    """Get data for dashboard"""
    client = python_binance.get_client()
    
    # Account
    account = client.get_account()
    nxpc_free = 0
    usdt_free = 0
    
    for balance in account['balances']:
        if balance['asset'] == 'NXPC':
            nxpc_free = float(balance['free'])
        elif balance['asset'] == 'USDT':
            usdt_free = float(balance['free'])
    
    # Market
    ticker = client.get_symbol_ticker(symbol='NXPCUSDT')
    price = float(ticker['price'])
    
    ticker_24h = client.get_ticker(symbol='NXPCUSDT')
    change = float(ticker_24h['priceChangePercent'])
    volume = float(ticker_24h['volume'])
    
    # Portfolio value
    nxpc_value = nxpc_free * price
    total_value = usdt_free + nxpc_value
    
    return {
        'time': datetime.now().strftime('%H:%M:%S'),
        'price': price,
        'change': change,
        'volume': volume,
        'nxpc_balance': nxpc_free,
        'usdt_balance': usdt_free,
        'nxpc_value': nxpc_value,
        'total_value': total_value,
        'price_str': f"${price:.4f}",
        'change_str': f"{change:+.2f}%",
        'volume_str': f"{volume:,.0f}",
        'nxpc_str': f"{nxpc_free:,.2f}",
        'usdt_str': f"${usdt_free:,.2f}",
        'total_str': f"${total_value:,.2f}"
    }

def print_dashboard(data):
    """Print dashboard"""
    print("\n" + "="*60)
    print("📈 NXPC/USDT TRADING DASHBOARD")
    print("="*60)
    print(f"Time: {data['time']}")
    print()
    print(f"💰 PRICE: {data['price_str']} ({data['change_str']})")
    print(f"📊 24h Volume: {data['volume_str']} NXPC")
    print()
    print("💼 PORTFOLIO:")
    print(f"   NXPC: {data['nxpc_str']} (${data['nxpc_value']:.2f})")
    print(f"   USDT: {data['usdt_str']}")
    print(f"   TOTAL: {data['total_str']}")
    print()
    print("🤖 BOT STATUS: ACTIVE")
    print("📈 STRATEGY: SMA20 + RSI14")
    print("="*60)
    print("Commands: (r)efresh, (t)rade, (q)uit")

def main():
    """Main dashboard loop"""
    print("🚀 Starting NXPC Trading Dashboard...")
    
    while True:
        try:
            data = get_dashboard_data()
            print_dashboard(data)
            
            cmd = input("\n> ").strip().lower()
            
            if cmd == 'q':
                print("\n👋 Closing dashboard...")
                break
            elif cmd == 't':
                print("\nOpening trading interface...")
                import subprocess
                subprocess.run(["python", "nxpc_bot_enhanced.py"])
            elif cmd == 'r':
                continue  # Just refresh
            else:
                print("❌ Unknown command")
                
            time.sleep(2)
            
        except KeyboardInterrupt:
            print("\n\n👋 Dashboard stopped")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
