#!/usr/bin/env python3
"""
Quick test of Binance migration
"""
import sys
sys.path.append('.')

print("🧪 QUICK TEST - BINANCE MIGRATION")
print("=" * 50)

# Test 1: Config
try:
    from config.api_config import api_config
    api_config.print_config()
    print("✅ Config: PASS")
except Exception as e:
    print(f"❌ Config: FAIL - {e}")

# Test 2: Data Fetcher
try:
    from data.fetcher import DataFetcher
    fetcher = DataFetcher()
    print(f"✅ Fetcher: PASS ({fetcher.symbol})")
    
    # Quick price check
    price = fetcher.fetch_current_price()
    if price:
        print(f"   Current price: ${price['price']}")
    
except Exception as e:
    print(f"❌ Fetcher: FAIL - {e}")

# Test 3: Python Binance
try:
    import python_binance
    print(f"✅ Python Binance: PASS")
    print(f"   API Key: {python_binance.api_key[:10]}...")
except Exception as e:
    print(f"❌ Python Binance: FAIL - {e}")

print("\n" + "=" * 50)
print("🎯 READY FOR PAPER TRADING NXPC/USDT!")
print("=" * 50)
print("\nNext: Run 'python main.py' and choose option 5")
