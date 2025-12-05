#!/bin/bash

echo "🚀 STARTING CONFIG-BASED TRADING BOT"
echo "====================================="

# Check config file
if [ ! -f "telegram_config.py" ]; then
    echo "❌ telegram_config.py not found!"
    echo "   Create it first with your Telegram token"
    exit 1
fi

# Stop existing bots
pkill -f "nxpc_bot" 2>/dev/null
sleep 2

# Create logs directory
mkdir -p logs

# Start bot
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="logs/config_bot_${TIMESTAMP}.log"

echo "📋 Starting bot..."
echo "   Log: $LOG_FILE"

nohup python nxpc_bot_config_based.py > "$LOG_FILE" 2>&1 &

PID=$!
echo $PID > config_bot.pid

sleep 3

# Check if running
if ps -p "$PID" > /dev/null; then
    echo "✅ Bot started (PID: $PID)"
    
    # Show initial output
    echo ""
    echo "🔍 Initial output:"
    tail -20 "$LOG_FILE" | grep -E "(✅|❌|🤖|🚀|Price:|USDT:|Telegram:)"
    
    echo ""
    echo "🎯 CONTROL:"
    echo "   tail -f $LOG_FILE       # Monitor logs"
    echo "   kill $PID               # Stop bot"
    echo "   cat config_bot.pid      # Show PID"
else
    echo "❌ Bot failed to start"
    echo "Check log: $LOG_FILE"
    exit 1
fi

echo "====================================="
