# data/fetcher.py - FIXED
"""
Data fetching from exchanges
"""
import ccxt
import pandas as pd
import time
from datetime import datetime, timedelta
import os

# Import settings
try:
    from config.settings import settings
except ImportError as e:
    print(f"⚠️  Settings import error: {e}")
    
    # Fallback settings
    class SimpleSettings:
        def __init__(self):
            self.EXCHANGE = "bitget"
            self.DEFAULT_SYMBOL = "BTC/USDT"
            self.DEFAULT_TIMEFRAME = "1h"
            self.DEFAULT_DAYS_BACK = 90
            self.MAX_CANDLES = 1000
            self.DATA_DIR = "data"
    
    settings = SimpleSettings()

class DataFetcher:
    def __init__(self, exchange_id=None):
        # Akses settings sebagai OBJECT, bukan class
        self.exchange_id = exchange_id or settings.EXCHANGE
        self.exchange = self._init_exchange()
    
    def _init_exchange(self):
        """Initialize exchange connection"""
        exchange_class = getattr(ccxt, self.exchange_id)
        return exchange_class({
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
    
    def fetch_historical_data(self, symbol=None, timeframe=None, 
                            days_back=None, save_csv=True):
        """
        Fetch historical OHLCV data
        """
        # Akses settings sebagai OBJECT
        symbol = symbol or settings.DEFAULT_SYMBOL
        timeframe = timeframe or settings.DEFAULT_TIMEFRAME
        days_back = days_back or settings.DEFAULT_DAYS_BACK
        
        print(f"📥 Fetching {symbol} {timeframe} data ({days_back} days)...")
        
        # Calculate start time
        since = self.exchange.parse8601(
            (datetime.now() - timedelta(days=days_back)).isoformat()
        )
        
        all_data = []
        current_since = since
        
        try:
            while True:
                # Fetch data in batches
                ohlcv = self.exchange.fetch_ohlcv(
                    symbol=symbol,
                    timeframe=timeframe,
                    since=current_since,
                    limit=settings.MAX_CANDLES
                )
                
                if not ohlcv:
                    break
                
                all_data.extend(ohlcv)
                current_since = ohlcv[-1][0] + 1
                
                # Progress
                latest = datetime.fromtimestamp(ohlcv[-1][0] / 1000)
                print(f"  Downloaded until: {latest.strftime('%Y-%m-%d %H:%M')}")
                
                if len(ohlcv) < settings.MAX_CANDLES:
                    break
                
                time.sleep(self.exchange.rateLimit / 1000)
                
        except Exception as e:
            print(f"⚠️  Warning: {e}")
        
        if not all_data:
            print("❌ No data fetched!")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(
            all_data,
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        print(f"✅ Downloaded {len(df)} candles")
        
        # Save to CSV
        if save_csv:
            self._save_to_csv(df, symbol, timeframe, days_back)
        
        return df
    
    def _save_to_csv(self, df, symbol, timeframe, days_back):
        """Save DataFrame to CSV"""
        os.makedirs(settings.DATA_DIR, exist_ok=True)
        
        filename = f"{symbol.replace('/', '_')}_{timeframe}_{days_back}days.csv"
        filepath = os.path.join(settings.DATA_DIR, filename)
        
        df.to_csv(filepath)
        print(f"💾 Data saved: {filepath}")
    
    def fetch_current_price(self, symbol=None):
        """Get current market price"""
        symbol = symbol or settings.DEFAULT_SYMBOL
        
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'price': ticker['last'],
                'high': ticker['high'],
                'low': ticker['low'],
                'volume': ticker['quoteVolume'],
                'change': ticker['percentage'],
                'timestamp': ticker['datetime']
            }
        except Exception as e:
            print(f"Error fetching price: {e}")
            return None

if __name__ == "__main__":
    # Test the fetcher
    fetcher = DataFetcher()
    
    # Test price
    price = fetcher.fetch_current_price()
    if price:
        print(f"\n💰 {price['symbol']}: ${price['price']:.2f}")
        print(f"📈 24h Change: {price['change']:.2f}%")
    
    # Test historical (small sample)
    print("\n" + "="*50)
    df = fetcher.fetch_historical_data(days_back=1)
    if not df.empty:
        print(f"\n📊 Data sample:")
        print(df.head())