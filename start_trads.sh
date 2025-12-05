#!/bin/bash
# Generate session name dengan timestamp
SESSION_NAME="trads-$(date +%Y%m%d-%H%M%S)"

echo "🚀 Starting trading bot: $SESSION_NAME"
screen -S "$SESSION_NAME" -dm python main.py

echo "✅ Bot started in screen session: $SESSION_NAME"
echo ""
echo "Commands:"
echo "  Monitor:    screen -r $SESSION_NAME"
echo "  Detach:     Ctrl+A, D"
echo "  List all:   screen -ls"
echo "  Kill:       screen -XS $SESSION_NAME quit"
