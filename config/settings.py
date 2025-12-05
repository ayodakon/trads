# config/settings.py - OPTIMIZED FOR SMALL CAPITAL & COMPOUNDING
"""
Global settings for Trading Bot - OPTIMIZED FOR NXPC/USDT (SMALL CAPITAL VERSION)
"""
import os
from datetime import datetime

class Settings:
    # ==================== EXCHANGE SETTINGS ====================
    EXCHANGE = "bitget"
    DEFAULT_SYMBOL = "NXPC/USDT"
    DEFAULT_TIMEFRAME = "1h"
    USE_TESTNET = True  # Always use testnet for safety
    
    # ==================== DATA SETTINGS ====================
    DEFAULT_DAYS_BACK = 90
    MAX_CANDLES = 2000
    DATA_CACHE_DAYS = 7  # Cache data for 7 days
    
    # ==================== BACKTEST SETTINGS ====================
    INITIAL_CAPITAL = 1000.0
    COMMISSION = 0.001  # 0.1% trading commission
    SLIPPAGE = 0.0005   # 0.05% slippage
    
    # ==================== STRATEGY PARAMETERS (OPTIMIZED FOR SMALL CAPITAL) ====================
    # SMA Crossover Strategy - OPTIMIZED FOR 15 NXPC STARTING CAPITAL
    SMA_FAST = 20      # ⬅️ UBAH: 20 (lebih cepat untuk modal kecil)
    SMA_SLOW = 45      # ⬅️ UBAH: 45 (dari 50) - lebih responsif
    
    # RSI Parameters (for combo strategy)
    RSI_PERIOD = 14
    RSI_OVERBOUGHT = 70
    RSI_OVERSOLD = 30
    
    # ==================== RISK MANAGEMENT (OPTIMIZED FOR SMALL CAPITAL) ====================
    DEFAULT_STOP_LOSS = 0.05        # ⬅️ UBAH: 5% (lebih ketat untuk modal kecil)
    DEFAULT_TAKE_PROFIT = 0.10      # ⬅️ UBAH: 10% (1:2 risk-reward tetap)
    
    # ⬇️ TAMBAHKAN UNTUK COMPOUNDING
    MIN_TRADE_SIZE = 0.5            # ⬅️ BARU: Minimum $0.5 trade
    MAX_POSITION_SIZE = 0.95        # ⬅️ UBAH: 95% (untuk compounding)
    RISK_PER_TRADE = 0.015          # ⬅️ UBAH: 1.5% (lebih konservatif)
    
    TRAILING_STOP_PCT = 0.02        # ⬅️ UBAH: 2% trailing stop
    MAX_DRAWDOWN = 0.15             # ⬅️ UBAH: 15% max drawdown
    
    # ==================== PAPER TRADING SETTINGS (OPTIMIZED FOR SMALL CAPITAL) ====================
    PAPER_INITIAL_BALANCE = 7.0     # ≈ 15 NXPC @ $0.45
    PAPER_LEVERAGE = 1.0            # No leverage for spot
    PAPER_SIMULATION_DAYS = 30      # Default simulation days
    
    # ⬇️ TAMBAHKAN UNTUK COMPOUNDING BOT
    COMPOUNDING_ENABLED = True      # ⬅️ BARU: Enable compounding
    TRADE_FREQUENCY = "1h"          # ⬅️ BARU: Trade every hour
    AUTO_REINVEST_PCT = 1.0         # ⬅️ BARU: Reinvest 100% of profits
    
    # ==================== FILE PATHS ====================
    DATA_DIR = "data"
    RESULTS_DIR = "results"
    LOGS_DIR = "logs"
    REPORTS_DIR = "reports"
    CHARTS_DIR = "charts"
    
    # ==================== COMPOUNDING BOT SETTINGS ====================
    BOT_CHECK_INTERVAL = 3600       # ⬅️ BARU: Check every 1 hour (3600 seconds)
    BOT_MAX_DAILY_TRADES = 24       # ⬅️ BARU: Max 24 trades per day (1 per hour)
    BOT_MIN_BALANCE = 0.1           # ⬅️ BARU: Minimum $0.1 balance to trade
    
    # ==================== OPTIMIZATION SETTINGS ====================
    OPTIMIZATION_DAYS = 90
    OPTIMIZATION_METRIC = "sharpe"
    PARAMETER_RANGES = {
        'sma_fast': [15, 20, 25, 30],    # ⬅️ OPTIMIZE untuk modal kecil
        'sma_slow': [40, 45, 50, 55],
        'stop_loss': [0.04, 0.05, 0.06], # ⬅️ Range lebih ketat
        'take_profit': [0.08, 0.10, 0.12]
    }
    
    # ==================== PERFORMANCE METRICS ====================
    MIN_WIN_RATE = 0.40
    MIN_PROFIT_FACTOR = 1.30
    MAX_CONSECUTIVE_LOSSES = 5
    
    # ==================== NOTIFICATION SETTINGS ====================
    ENABLE_NOTIFICATIONS = False
    TELEGRAM_BOT_TOKEN = ""
    TELEGRAM_CHAT_ID = ""
    
    # ==================== ADVANCED SETTINGS ====================
    ENABLE_HEDGING = False
    ENABLE_PYRAMIDING = False
    MAX_PYRAMID_LEVELS = 3
    
    def __init__(self):
        """Initialize and create directories"""
        self.create_directories()
        self.validate_settings()
    
    def create_directories(self):
        """Create necessary directories"""
        dirs = [
            self.DATA_DIR, 
            self.RESULTS_DIR, 
            self.LOGS_DIR,
            self.REPORTS_DIR,
            self.CHARTS_DIR
        ]
        
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
    
    def validate_settings(self):
        """Validate all settings for consistency - UPDATED FOR SMALL CAPITAL"""
        if self.SMA_SLOW <= self.SMA_FAST:
            print(f"⚠️  Warning: SMA_SLOW ({self.SMA_SLOW}) should be greater than SMA_FAST ({self.SMA_FAST})")
            self.SMA_SLOW = self.SMA_FAST + 10
        
        if self.DEFAULT_TAKE_PROFIT <= self.DEFAULT_STOP_LOSS:
            print(f"⚠️  Warning: TAKE_PROFIT should be greater than STOP_LOSS")
            self.DEFAULT_TAKE_PROFIT = self.DEFAULT_STOP_LOSS * 2
        
        # Validation for small capital
        if self.MIN_TRADE_SIZE > 1.0:
            print(f"⚠️  Warning: MIN_TRADE_SIZE ({self.MIN_TRADE_SIZE}) too high for small capital")
            self.MIN_TRADE_SIZE = 0.5
        
        if self.MAX_POSITION_SIZE > 1.0:
            print(f"⚠️  Warning: MAX_POSITION_SIZE ({self.MAX_POSITION_SIZE}) cannot exceed 100%")
            self.MAX_POSITION_SIZE = 0.95
    
    def print_settings(self):
        """Print all settings in a formatted way - UPDATED"""
        print("="*70)
        print("🤖 TRADING BOT SETTINGS - OPTIMIZED FOR SMALL CAPITAL (15 NXPC)")
        print("="*70)
        
        categories = {
            "Exchange": ["EXCHANGE", "DEFAULT_SYMBOL", "DEFAULT_TIMEFRAME", "USE_TESTNET"],
            "Strategy (Small Capital)": ["SMA_FAST", "SMA_SLOW", "RSI_PERIOD"],
            "Risk Management": ["DEFAULT_STOP_LOSS", "DEFAULT_TAKE_PROFIT", 
                               "MIN_TRADE_SIZE", "MAX_POSITION_SIZE", "RISK_PER_TRADE"],
            "Compounding Bot": ["COMPOUNDING_ENABLED", "TRADE_FREQUENCY", 
                               "AUTO_REINVEST_PCT", "BOT_MAX_DAILY_TRADES"],
            "Paper Trading": ["PAPER_INITIAL_BALANCE", "PAPER_SIMULATION_DAYS"],
            "Paths": ["DATA_DIR", "RESULTS_DIR", "LOGS_DIR", "REPORTS_DIR", "CHARTS_DIR"]
        }
        
        for category, keys in categories.items():
            print(f"\n📋 {category}:")
            print("-" * 45)
            for key in keys:
                if hasattr(self, key):
                    value = getattr(self, key)
                    # Format percentage values
                    if any(term in key.lower() for term in ['loss', 'profit', 'size', 'drawdown', 'risk', 
                                                           'commission', 'slippage', 'pct', 'reinvest']):
                        if isinstance(value, float) and value < 1:
                            value_str = f"{value*100:.1f}%"
                        else:
                            value_str = str(value)
                    else:
                        value_str = str(value)
                    
                    print(f"  {key:25}: {value_str}")
        
        # Calculate estimated metrics
        estimated_trades_per_day = 24 if self.TRADE_FREQUENCY == "1h" else 1
        print(f"\n📈 ESTIMATED METRICS (15 NXPC starting):")
        print("-" * 45)
        print(f"  Initial Capital:        15 NXPC (≈${self.PAPER_INITIAL_BALANCE:.2f})")
        print(f"  Position Size:          {self.MAX_POSITION_SIZE*100:.0f}% of balance")
        print(f"  Trades per Day:         {estimated_trades_per_day}")
        print(f"  Compounding:            {'ENABLED ✅' if self.COMPOUNDING_ENABLED else 'DISABLED'}")
        
        print("\n" + "="*70)
        print(f"⚡ Strategy: SMA({self.SMA_FAST}/{self.SMA_SLOW}) with Compounding")
        print(f"🎯 Risk-Reward: 1:{self.DEFAULT_TAKE_PROFIT/self.DEFAULT_STOP_LOSS:.1f}")
        print("="*70)
    
    def get_strategy_name(self):
        """Get formatted strategy name"""
        return f"SMA_Crossover_{self.SMA_FAST}_{self.SMA_SLOW}_Compounding"
    
    def get_timestamp(self):
        """Get current timestamp for filenames"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def get_report_filename(self, strategy_name=""):
        """Generate report filename"""
        if not strategy_name:
            strategy_name = self.get_strategy_name()
        timestamp = self.get_timestamp()
        return f"{self.REPORTS_DIR}/{strategy_name}_{timestamp}.html"
    
    def get_log_filename(self):
        """Generate log filename"""
        date_str = datetime.now().strftime("%Y%m%d")
        return f"{self.LOGS_DIR}/trading_{date_str}.log"
    
    def get_data_filename(self, symbol="", timeframe=""):
        """Generate data filename"""
        if not symbol:
            symbol = self.DEFAULT_SYMBOL.replace('/', '_')
        if not timeframe:
            timeframe = self.DEFAULT_TIMEFRAME
        return f"{self.DATA_DIR}/{symbol}_{timeframe}_{self.DEFAULT_DAYS_BACK}days.csv"
    
    def get_compounding_report_filename(self):
        """Generate compounding bot report filename"""
        date_str = datetime.now().strftime("%Y%m%d")
        return f"{self.RESULTS_DIR}/compounding_report_{date_str}.csv"

# Create global instance
settings = Settings()

# Print initialization message
print("📁 Directory ready: data")
print("📁 Directory ready: results")
print("📁 Directory ready: logs")
print("📁 Directory ready: reports")
print("📁 Directory ready: charts")
print("💰 Initial Capital: 15 NXPC (≈$7.00)")
print("⚡ Strategy: SMA(20/45) with 5% Stop Loss")
print("🔄 Compounding: ENABLED (100% reinvest)")
print("✅ Settings initialized for SMALL CAPITAL TRADING")
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
