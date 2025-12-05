#!/usr/bin/env python3
"""
Test Binance Migration
"""
import sys
sys.path.append('.')

from config.api_config import api_config
from data.fetcher import DataFetcher

def main():
    print("🧪 TESTING BINANCE MIGRATION")
    print("=" * 50)
    
    # Test 1: Config
    print("\n1. Testing API Config...")
    api_config.print_config()
    
    if not api_config.validate_config():
        print("⚠️  API config not valid, but continuing test...")
    
    # Test 2: Fetcher
    print("\n2. Testing Data Fetcher...")
    fetcher = DataFetcher()
    
    if fetcher.client:
        print(f"✅ Binance client created for {fetcher.symbol}")
        
        # Test 3: Current price (quick)
        try:
            price = fetcher.fetch_current_price()
            if price:
                print(f"✅ Current price: ${price['price']}")
            else:
                print("⚠️  Could not fetch price")
        except Exception as e:
            print(f"⚠️  Price fetch error (may be normal): {e}")
        
        # Test 4: Account balance
        try:
            balance = fetcher.fetch_account_balance()
            if balance:
                print(f"✅ Account balance fetched ({len(balance)} assets)")
                # Show top 5 assets
                count = 0
                for asset, data in balance.items():
                    if data['total'] > 0 and count < 5:
                        print(f"   {asset}: {data['total']}")
                        count += 1
            else:
                print("⚠️  Could not fetch balance")
        except Exception as e:
            print(f"⚠️  Balance fetch error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 MIGRATION TEST COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    main()
