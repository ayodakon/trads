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
