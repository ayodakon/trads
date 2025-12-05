# utils/logger.py - FIXED SINGLETON
"""
Logging system
"""
import logging
import os
from datetime import datetime

class TradingLogger:
    _instance = None
    _initialized = False
    
    def __new__(cls, logs_dir="logs"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._logs_dir = logs_dir
        return cls._instance
    
    def __init__(self, logs_dir="logs"):
        # Prevent re-initialization
        if TradingLogger._initialized:
            return
        
        # Create logs directory
        self._logs_dir = logs_dir
        os.makedirs(self._logs_dir, exist_ok=True)
        
        # Setup logging
        timestamp = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(self._logs_dir, f'trading_{timestamp}.log')
        
        self.logger = logging.getLogger('TradingBot')
        self.logger.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        TradingLogger._initialized = True
        self.logger.info(f"Logger initialized. Log file: {log_file}")
    
    def info(self, message):
        self.logger.info(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def trade(self, trade_data):
        """Log trade information"""
        message = f"TRADE - {trade_data}"
        self.logger.info(message)
    
    def strategy_signal(self, signal, price, timestamp):
        """Log strategy signal"""
        message = f"SIGNAL - {signal} @ ${price:.2f} - {timestamp}"
        self.logger.info(message)

# Test the logger
if __name__ == "__main__":
    logger = TradingLogger("test_logs")
    logger.info("Test message")
    print("✅ Logger test successful!")

# Global instance
_logger_instance = None

def get_logger(logs_dir="logs"):
    """Get or create logger instance (for compatibility)"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = TradingLogger(logs_dir)
    return _logger_instance

# Convenience functions untuk import di main.py
def log_info(message):
    get_logger().info(message)

def log_warning(message):
    get_logger().warning(message)

def log_error(message):
    get_logger().error(message)

def log_trade(trade_data):
    get_logger().trade(trade_data)

def log_signal(signal, price, timestamp):
    get_logger().strategy_signal(signal, price, timestamp)

# Test jika di-run langsung
if __name__ == "__main__":
    logger = get_logger("test_logs")
    log_info("Test info message")
    log_warning("Test warning")
    log_trade({"action": "BUY", "price": 50000})
    print("✅ Logger functions test successful!")