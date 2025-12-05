"""
Binance API Configuration - CLEAN VERSION
"""
import os
from dotenv import load_dotenv

load_dotenv()

class BinanceConfig:
    """Configuration for Binance API"""
    
    # Load from python_binance.py
    try:
        import python_binance
        API_KEY = python_binance.api_key
        API_SECRET = python_binance.api_secret
        LOADED_FROM_FILE = True
    except ImportError:
        # Fallback to .env
        API_KEY = os.getenv('BINANCE_API_KEY', '')
        API_SECRET = os.getenv('BINANCE_API_SECRET', '')
        LOADED_FROM_FILE = False
    
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
            return False
        return True
    
    def print_config(self):
        print("\n📡 BINANCE API CONFIGURATION")
        print("=" * 50)
        print(f"Mode: {'TESTNET 🔬' if self.USE_TESTNET else 'LIVE TRADING ⚠️'}")
        print(f"API Key: {'✅ Set' if self.API_KEY else '❌ Not set'}")
        print(f"API Secret: {'✅ Set' if self.API_SECRET else '❌ Not set'}")
        print(f"Loaded from: {'python_binance.py' if self.LOADED_FROM_FILE else '.env'}")
        print(f"Default Symbol: {self.DEFAULT_SYMBOL}")
        print(f"Base URL: {self.base_url}")
        if self.API_KEY:
            print(f"API Key (first 10): {self.API_KEY[:10]}...")
        print("=" * 50)

# Singleton instance
api_config = BinanceConfig()
