#!/bin/bash
# ============================================
# 🤖 NXPC TRADING BOT CONTROL PANEL
# ============================================

PID_FILE="config_bot.pid"
LOG_DIR="logs"
SCRIPT_NAME="nxpc_bot_config_based.py"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════╗"
    echo "║    🤖 NXPC TRADING BOT CONTROL           ║"
    echo "╚══════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_status() {
    echo -e "${GREEN}[✓] $1${NC}"
}

print_error() {
    echo -e "${RED}[✗] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[!] $1${NC}"
}

check_bot_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0  # Running
        else
            rm -f "$PID_FILE" 2>/dev/null
            return 1  # Not running
        fi
    else
        return 1  # No PID file
    fi
}

get_latest_log() {
    ls -t "$LOG_DIR"/config_bot_*.log 2>/dev/null | head -1
}

case "$1" in
    status)
        print_header
        if check_bot_running; then
            PID=$(cat "$PID_FILE")
            print_status "Bot is RUNNING (PID: $PID)"
            
            # Show uptime
            START_TIME=$(ps -o lstart= -p "$PID" 2>/dev/null)
            if [ -n "$START_TIME" ]; then
                echo "   Start Time: $START_TIME"
            fi
            
            # Show latest log info
            LATEST_LOG=$(get_latest_log)
            if [ -f "$LATEST_LOG" ]; then
                echo "   Log File: $(basename "$LATEST_LOG")"
                echo "   Last Activity:"
                
                # Last market check
                LAST_CHECK=$(grep "Market Check" "$LATEST_LOG" | tail -1)
                if [ -n "$LAST_CHECK" ]; then
                    echo "     Market Check: $LAST_CHECK" | sed 's/.*\[//;s/\].*/]/'
                fi
                
                # Last trade
                LAST_TRADE=$(grep -E "(BUY|SELL) ORDER" "$LATEST_LOG" | tail -1)
                if [ -n "$LAST_TRADE" ]; then
                    echo "     Last Trade: $LAST_TRADE" | sed 's/.*✅ //'
                fi
                
                # Last Telegram
                LAST_TELEGRAM=$(grep "Telegram sent:" "$LATEST_LOG" | tail -1)
                if [ -n "$LAST_TELEGRAM" ]; then
                    MSG=$(echo "$LAST_TELEGRAM" | sed 's/.*Telegram sent: //')
                    echo "     Last Telegram: ${MSG:0:40}..."
                fi
            fi
            
            # Show memory usage
            MEM_USAGE=$(ps -o %mem= -p "$PID" 2>/dev/null)
            CPU_USAGE=$(ps -o %cpu= -p "$PID" 2>/dev/null)
            if [ -n "$MEM_USAGE" ]; then
                echo "   Resources: CPU ${CPU_USAGE}%, MEM ${MEM_USAGE}%"
            fi
            
        else
            print_error "Bot is NOT RUNNING"
            
            # Check if there are any orphaned processes
            ORPHANED=$(ps aux | grep "$SCRIPT_NAME" | grep -v grep)
            if [ -n "$ORPHANED" ]; then
                print_warning "Found orphaned processes:"
                echo "$ORPHANED"
                echo ""
                echo "Run './bot_control.sh cleanup' to remove them"
            fi
        fi
        ;;
    
    start)
        print_header
        if check_bot_running; then
            print_error "Bot is already running!"
            echo "   Use './bot_control.sh restart' to restart"
        else
            echo "🚀 Starting NXPC Trading Bot..."
            ./start_config_bot.sh
        fi
        ;;
    
    stop)
        print_header
        if check_bot_running; then
            PID=$(cat "$PID_FILE")
            echo "🛑 Stopping bot (PID: $PID)..."
            
            # Send shutdown notification via Python
            python3 -c "
import requests
try:
    from telegram_config import TELEGRAM_TOKEN, CHAT_ID
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    payload = {
        'chat_id': CHAT_ID,
        'text': '🛑 Bot stopped via control panel',
        'parse_mode': 'HTML'
    }
    requests.post(url, json=payload, timeout=5)
except:
    pass
            " 2>/dev/null
            
            kill "$PID"
            sleep 2
            
            if check_bot_running; then
                kill -9 "$PID" 2>/dev/null
                print_warning "Force killed bot"
            fi
            
            rm -f "$PID_FILE" 2>/dev/null
            print_status "Bot stopped successfully"
        else
            print_error "Bot is not running"
        fi
        ;;
    
    restart)
        print_header
        echo "🔁 Restarting bot..."
        $0 stop > /dev/null 2>&1
        sleep 3
        ./start_config_bot.sh
        ;;
    
    logs)
        print_header
        LATEST_LOG=$(get_latest_log)
        if [ -f "$LATEST_LOG" ]; then
            echo "📋 Showing last 50 lines of: $(basename "$LATEST_LOG")"
            echo "═"$(printf '═%.0s' {1..50})
            tail -50 "$LATEST_LOG"
        else
            print_error "No log files found in $LOG_DIR/"
        fi
        ;;
    
    monitor)
        print_header
        LATEST_LOG=$(get_latest_log)
        if [ -f "$LATEST_LOG" ]; then
            echo "📡 LIVE MONITORING - $(basename "$LATEST_LOG")"
            echo "   Press Ctrl+C to stop"
            echo "═"$(printf '═%.0s' {1..50})
            tail -f "$LATEST_LOG"
        else
            print_error "No log files found"
        fi
        ;;
    
    cleanup)
        print_header
        echo "🧹 Cleaning up bot processes..."
        
        # Kill all bot processes
        pkill -f "$SCRIPT_NAME" 2>/dev/null
        pkill -f "nxpc_bot" 2>/dev/null
        
        # Remove PID files
        rm -f config_bot.pid compounding_bot.pid 2>/dev/null
        
        # Count killed processes
        COUNT=$(ps aux | grep -E "(nxpc_bot|python.*nxpc)" | grep -v grep | wc -l)
        if [ "$COUNT" -eq 0 ]; then
            print_status "Cleanup complete - all bot processes removed"
        else
            print_warning "Some processes still running. Use 'ps aux | grep nxpc' to check"
        fi
        ;;
    
    config)
        print_header
        echo "⚙️  Current Configuration:"
        echo "═"$(printf '═%.0s' {1..50})
        
        if [ -f "telegram_config.py" ]; then
            python3 -c "
try:
    from telegram_config import *
    print('📱 Telegram Config:')
    print(f'   Token: {TELEGRAM_TOKEN[:15]}...')
    print(f'   Chat ID: {CHAT_ID}')
    print(f'   Interval: {CHECK_INTERVAL} minutes')
    print(f'   Symbol: {SYMBOL}')
    print(f'   Testnet: {USE_TESTNET}')
    print(f'   Target Profit: {TARGET_PROFIT_PERCENT}%')
    print(f'   Stop Loss: {STOP_LOSS_PERCENT}%')
    print(f'   Compound: {COMPOUND_PERCENT}%')
except Exception as e:
    print(f'Error reading config: {e}')
            "
        else
            print_error "telegram_config.py not found!"
        fi
        ;;
    
    test-telegram)
        print_header
        echo "📱 Testing Telegram Connection..."
        python3 -c "
import requests
try:
    from telegram_config import TELEGRAM_TOKEN, CHAT_ID
    print('✅ Config loaded')
    print(f'   Token: {TELEGRAM_TOKEN[:15]}...')
    print(f'   Chat ID: {CHAT_ID}')
    
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    payload = {
        'chat_id': CHAT_ID,
        'text': '🔔 TEST: Telegram connection is working!',
        'parse_mode': 'HTML'
    }
    
    import time
    start = time.time()
    response = requests.post(url, json=payload, timeout=10)
    elapsed = time.time() - start
    
    if response.status_code == 200:
        print(f'✅ Telegram OK ({elapsed:.2f}s)')
        print('   Message sent successfully!')
    else:
        print(f'❌ Telegram Failed: {response.status_code}')
        print(f'   Response: {response.text[:100]}')
        
except ImportError:
    print('❌ telegram_config.py not found!')
except Exception as e:
    print(f'❌ Error: {e}')
        "
        ;;
    
    help|*)
        print_header
        echo -e "${BLUE}Available Commands:${NC}"
        echo ""
        echo -e "${GREEN}  ./bot_control.sh status${NC}"
        echo "     Check bot status and show details"
        echo ""
        echo -e "${GREEN}  ./bot_control.sh start${NC}"
        echo "     Start the bot (if not running)"
        echo ""
        echo -e "${GREEN}  ./bot_control.sh stop${NC}"
        echo "     Stop the bot gracefully"
        echo ""
        echo -e "${GREEN}  ./bot_control.sh restart${NC}"
        echo "     Restart the bot"
        echo ""
        echo -e "${GREEN}  ./bot_control.sh logs${NC}"
        echo "     Show recent logs"
        echo ""
        echo -e "${GREEN}  ./bot_control.sh monitor${NC}"
        echo "     Live log monitoring"
        echo ""
        echo -e "${GREEN}  ./bot_control.sh cleanup${NC}"
        echo "     Clean up all bot processes"
        echo ""
        echo -e "${GREEN}  ./bot_control.sh config${NC}"
        echo "     Show current configuration"
        echo ""
        echo -e "${GREEN}  ./bot_control.sh test-telegram${NC}"
        echo "     Test Telegram connection"
        echo ""
        echo -e "${GREEN}  ./bot_control.sh help${NC}"
        echo "     Show this help message"
        echo ""
        echo "═"$(printf '═%.0s' {1..50})
        echo "📊 Bot will check market every 30 minutes"
        echo "📱 Telegram notifications are enabled"
        echo "📈 Strategy: 3% target, 2% stop loss, 10% compounding"
        ;;
esac
