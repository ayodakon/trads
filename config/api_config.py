# config/api_config.py - UPDATE INI!
import os
from dotenv import load_dotenv

class APIConfig:
    def __init__(self):
        # Priority 1: Environment variables
        self.BITGET_API_KEY = os.environ.get('BITGET_API_KEY')
        self.BITGET_SECRET = os.environ.get('BITGET_SECRET')
        self.BITGET_PASSPHRASE = os.environ.get('BITGET_PASSPHRASE')
        
        # Priority 2: .env file (for local dev only)
        if not all([self.BITGET_API_KEY, self.BITGET_SECRET, self.BITGET_PASSPHRASE]):
            load_dotenv()
            self.BITGET_API_KEY = os.getenv('BITGET_API_KEY')
            self.BITGET_SECRET = os.getenv('BITGET_SECRET')
            self.BITGET_PASSPHRASE = os.getenv('BITGET_PASSPHRASE')
        
        self.USE_TESTNET = os.getenv('USE_TESTNET', 'true').lower() == 'true'
        
        # Security warning
        if self.BITGET_API_KEY and "test" not in self.BITGET_API_KEY.lower():
            print("⚠️  WARNING: Using LIVE API key. Be careful!")