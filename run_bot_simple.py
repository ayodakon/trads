#!/usr/bin/env python3
"""
Simple runner for NXPC Trading Bot with Telegram
"""
import sys
import os

# Import config
try:
    from telegram_config import TELEGRAM_TOKEN, CHAT_ID, CHECK_INTERVAL
except ImportError:
    print("❌ File telegram_config.py tidak ditemukan")
    print("   Buat dulu dengan perintah:")
    print("   nano telegram_config.py")
    sys.exit(1)

print("🤖 STARTING NXPC TRADING BOT WITH TELEGRAM")
print("=" * 50)
print(f"Token: {TELEGRAM_TOKEN[:10]}...")
print(f"Chat ID: {CHAT_ID}")
print(f"Interval: {CHECK_INTERVAL} minutes")
print("=" * 50)

# Import the main bot
sys.path.append('.')
from nxpc_bot_enhanced_telegram import NXPCTradingBotWithTelegram

# Create and run bot
bot = NXPCTradingBotWithTelegram(
    telegram_token=TELEGRAM_TOKEN,
    chat_id=CHAT_ID
)

# Start 24/7
bot.run_24_7(interval_minutes=CHECK_INTERVAL)
