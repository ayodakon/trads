#!/bin/bash
while true; do
    echo "🚀 Starting Trading Bot..."
    python main.py
    echo "⚠️  Bot stopped, restarting in 10 seconds..."
    sleep 10
done
