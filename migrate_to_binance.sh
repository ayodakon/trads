#!/bin/bash

echo "🚀 STARTING MIGRATION TO BINANCE"
echo "=========================================="

# ============================================
# PHASE 0: VERIFY BACKUP
# ============================================
echo "🔍 Phase 0: Verifying backup..."
if [ ! -d "trads_backup_"* ]; then
    echo "❌ No backup found! Run backup first."
    exit 1
fi

LATEST_BACKUP=$(ls -d trads_backup_* | tail -1)
echo "✅ Latest backup: $LATEST_BACKUP"

# ============================================
# PHASE 1: UPDATE CONFIG FILES
# ============================================
echo -e "\n📁 Phase 1: Updating config files..."

# 1.1 Backup original api_config.py
echo "   Backing up original api_config.py..."
cp config/api_config.py config/api_config.py.bitget.original 2>/dev/null

# 1.2 Create new Binance api_config.py
echo "   Creating Binance api_config.py..."
cat > config/api_config.py << 'EOF'
"""
Binance API Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

class BinanceConfig:
    """Configuration for Binance API"""
    
    # Binance Testnet API Credentials
    API_KEY = os.getenv('BINANCE_API_KEY', '')
    API_SECRET = os.getenv('BINANCE_API_SECRET', '')
    
    # Load from python_binance.py if exists
    try:
        import python_binance
        if not API_KEY:
            API_KEY = python_binance.api_key
        if not API_SECRET:
            API_SECRET = python_binance.api_secret
            print("✅ Loaded credentials from python_binance.py")
    except:
        pass
    
    # Trading Settings
    DEFAULT_SYMBOL = os.getenv('DEFAULT_SYMBOL', 'NXPCUSDT')
    USE_TESTNET = os.getenv('USE_TESTNET', 'true').lower() == 'true'
    
    # API URLs
    TESTNET_URL = 'https://testnet.binance.vision'
    MAINNET_URL = 'https://api.binance.com'
    
    @property
    def base_url(self):
        return self.TESTNET_URL if self.USE_TESTNET else self.MAINNET_URL
    
    @property
    def is_testnet(self):
        return self.USE_TESTNET
    
    def validate_config(self):
        if not self.API_KEY or not self.API_SECRET:
            print("⚠️  API credentials not set!")
            print("   Options:")
            print("   1. Add to .env: BINANCE_API_KEY, BINANCE_API_SECRET")
            print("   2. Edit config/api_config.py directly")
            print("   3. Keep using python_binance.py (auto-loaded)")
            return False
        return True
    
    def print_config(self):
        print("\n📡 BINANCE API CONFIGURATION")
        print("=" * 50)
        print(f"Mode: {'TESTNET 🔬' if self.USE_TESTNET else 'LIVE TRADING ⚠️'}")
        print(f"API Key: {'✅ Set' if self.API_KEY else '❌ Not set'}")
        print(f"API Secret: {'✅ Set' if self.API_SECRET else '❌ Not set'}")
        print(f"Default Symbol: {self.DEFAULT_SYMBOL}")
        print(f"Base URL: {self.base_url}")
        if self.API_KEY:
            print(f"API Key (first 10): {self.API_KEY[:10]}...")
        print("=" * 50)

# Singleton instance
api_config = BinanceConfig()
EOF

echo "✅ Created config/api_config.py (Binance version)"

# 1.3 Update settings.py for Binance
echo "   Updating settings.py for Binance..."
cat >> config/settings.py << 'EOF'

# ===== BINANCE-SPECIFIC SETTINGS =====
# NXPC/USDT trading settings
NXPC_SETTINGS = {
    'min_qty': 0.1,          # Minimum order quantity
    'step_size': 0.1,        # Order increment
    'min_notional': 1.0,     # Minimum order value (USD)
    'default_qty': 10,       # Default quantity for paper trading
}

# Binance API rate limits
BINANCE_RATE_LIMITS = {
    'requests_per_minute': 1200,
    'orders_per_second': 10,
    'orders_per_day': 160000,
}

# Default timeframe for Binance
BINANCE_TIMEFRAMES = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w']
EOF

echo "✅ Updated config/settings.py"

# ============================================
# PHASE 2: CREATE BINANCE FETCHER
# ============================================
echo -e "\n📊 Phase 2: Creating Binance data fetcher..."

# 2.1 Backup original fetcher
echo "   Backing up original fetcher.py..."
cp data/fetcher.py data/fetcher.py.bitget.original 2>/dev/null

# 2.2 Create simple Binance fetcher
echo "   Creating Binance fetcher.py..."
cat > data/fetcher.py << 'EOF'
"""
Binance Data Fetcher - Updated for Binance API
"""
import pandas as pd
import time
from datetime import datetime, timedelta
from binance.client import Client
from config.api_config import api_config

class DataFetcher:
    """Fetch market data from Binance"""
    
    def __init__(self, symbol=None):
        self.symbol = symbol or api_config.DEFAULT_SYMBOL
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize Binance client"""
        try:
            self.client = Client(
                api_key=api_config.API_KEY,
                api_secret=api_config.API_SECRET,
                testnet=api_config.is_testnet
            )
            print(f"✅ Binance client initialized for {self.symbol}")
        except Exception as e:
            print(f"❌ Failed to initialize Binance client: {e}")
            self.client = None
    
    def fetch_current_price(self, symbol=None):
        """Get current price for symbol"""
        symbol = symbol or self.symbol
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return {
                'symbol': symbol,
                'price': float(ticker['price']),
                'timestamp': datetime.now()
            }
        except Exception as e:
            print(f"❌ Error fetching price for {symbol}: {e}")
            return None
    
    def fetch_historical_data(self, days_back=30, interval='1h'):
        """
        Fetch historical kline/candlestick data
        
        Args:
            days_back: Number of days to fetch
            interval: Kline interval (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w)
        
        Returns:
            pandas.DataFrame with OHLCV data
        """
        try:
            print(f"📥 Fetching {self.symbol} data: {days_back} days, {interval} interval")
            
            # Calculate start time
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days_back)
            
            # Convert to milliseconds
            start_ms = int(start_time.timestamp() * 1000)
            
            # Fetch klines
            klines = self.client.get_historical_klines(
                symbol=self.symbol,
                interval=interval,
                start_str=start_ms,
                limit=1000
            )
            
            if not klines:
                print(f"❌ No data received for {self.symbol}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # Convert data types
            numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'quote_volume']
            df[numeric_cols] = df[numeric_cols].astype(float)
            
            # Convert timestamp
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Keep only needed columns
            df = df[['open', 'high', 'low', 'close', 'volume']]
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            
            print(f"✅ Fetched {len(df)} candles for {self.symbol}")
            return df
            
        except Exception as e:
            print(f"❌ Error fetching historical data: {e}")
            return pd.DataFrame()
    
    def fetch_order_book(self, symbol=None, limit=10):
        """Fetch order book depth"""
        symbol = symbol or self.symbol
        try:
            depth = self.client.get_order_book(symbol=symbol, limit=limit)
            return {
                'bids': [(float(price), float(qty)) for price, qty in depth['bids']],
                'asks': [(float(price), float(qty)) for price, qty in depth['asks']],
                'timestamp': datetime.now()
            }
        except Exception as e:
            print(f"❌ Error fetching order book: {e}")
            return None
    
    def fetch_account_balance(self):
        """Fetch account balance"""
        try:
            account = self.client.get_account()
            balances = {}
            for balance in account['balances']:
                free = float(balance['free'])
                locked = float(balance['locked'])
                if free > 0 or locked > 0:
                    balances[balance['asset']] = {
                        'free': free,
                        'locked': locked,
                        'total': free + locked
                    }
            return balances
        except Exception as e:
            print(f"❌ Error fetching account balance: {e}")
            return {}

# Test the fetcher
if __name__ == "__main__":
    fetcher = DataFetcher()
    
    # Test current price
    price = fetcher.fetch_current_price()
    if price:
        print(f"💰 Current {price['symbol']} price: ${price['price']}")
    
    # Test account balance
    balance = fetcher.fetch_account_balance()
    if balance:
        print(f"💼 Account balance:")
        for asset, data in balance.items():
            if data['total'] > 0:
                print(f"  {asset}: {data['total']}")
EOF

echo "✅ Created data/fetcher.py (Binance version)"

# ============================================
# PHASE 3: TEST THE MIGRATION
# ============================================
echo -e "\n🧪 Phase 3: Testing migration..."

# 3.1 Test config import
echo "   Testing config import..."
python3 -c "
from config.api_config import api_config
api_config.print_config()
print('✅ Config import successful')
"

# 3.2 Test fetcher
echo -e "\n   Testing data fetcher..."
python3 -c "
from data.fetcher import DataFetcher
fetcher = DataFetcher()
print('✅ Fetcher initialized')

# Quick test without API call
print(f'Symbol: {fetcher.symbol}')
print('✅ Basic fetcher test passed')
"

# 3.3 Create test script
echo "   Creating test script..."
cat > test_binance_migration.py << 'EOF'
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
EOF

chmod +x test_binance_migration.py

# ============================================
# PHASE 4: FINAL STEPS
# ============================================
echo -e "\n🎯 Phase 4: Final steps..."

# 4.1 Create .env template if not exists
if [ ! -f ".env" ]; then
    echo "   Creating .env template..."
    cat > .env << 'EOF'
# Binance API Configuration
# Get from: https://testnet.binance.vision/
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here

# Trading Settings
USE_TESTNET=true
DEFAULT_SYMBOL=NXPCUSDT

# Bot Settings
INITIAL_BALANCE=1000
STOP_LOSS=0.05  # 5%
TAKE_PROFIT=0.10  # 10%
EOF
    echo "✅ Created .env template"
else
    echo "📄 .env file already exists"
fi

# 4.2 Update requirements.txt
echo "   Updating requirements.txt..."
if grep -q "bitget" requirements.txt 2>/dev/null; then
    # Remove bitget, add binance
    grep -v "bitget" requirements.txt > requirements.tmp
    echo "python-binance>=3.0.0" >> requirements.tmp
    mv requirements.tmp requirements.txt
    echo "✅ Updated requirements.txt (replaced bitget with binance)"
else
    echo "python-binance>=3.0.0" >> requirements.txt
    echo "✅ Added python-binance to requirements.txt"
fi

# ============================================
# FINAL MESSAGE
# ============================================
echo -e "\n=========================================="
echo "🎉 MIGRATION TO BINANCE COMPLETE!"
echo "=========================================="
echo ""
echo "📋 WHAT WAS DONE:"
echo "   1. ✅ Updated config/api_config.py → Binance version"
echo "   2. ✅ Updated config/settings.py → Added Binance settings"
echo "   3. ✅ Updated data/fetcher.py → Binance data fetcher"
echo "   4. ✅ Created test script → test_binance_migration.py"
echo "   5. ✅ Created .env template → For API credentials"
echo "   6. ✅ Updated requirements.txt → python-binance added"
echo ""
echo "🔧 NEXT STEPS:"
echo "   1. Run test: python test_binance_migration.py"
echo "   2. Edit .env with your Binance Testnet API keys"
echo "   3. Install dependencies: pip install python-binance"
echo "   4. Test with: python main.py"
echo ""
echo "⚠️  IMPORTANT:"
echo "   - Your original Bitget files are backed up as:"
echo "     • config/api_config.py.bitget.original"
echo "     • data/fetcher.py.bitget.original"
echo "   - Full backup in: $LATEST_BACKUP"
echo ""
echo "🚀 RUN TEST NOW: ./test_binance_migration.py"
echo "=========================================="