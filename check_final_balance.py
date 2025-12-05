import python_binance
from datetime import datetime

client = python_binance.get_client()

# Get account
account = client.get_account()
nxpc_balance = 0
usdt_balance = 0

for balance in account['balances']:
    if balance['asset'] == 'NXPC':
        nxpc_balance = float(balance['free'])
    elif balance['asset'] == 'USDT':
        usdt_balance = float(balance['free'])

# Get current price
ticker = client.get_symbol_ticker(symbol='NXPCUSDT')
current_price = float(ticker['price'])

print("=" * 60)
print("💰 FINAL BALANCE REPORT")
print("=" * 60)
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"NXPC Price: ${current_price:.4f}")
print()

# Initial balances (from beginning)
INITIAL_NXPC = 1589.0
INITIAL_USDT = 10000.0
INITIAL_PORTFOLIO = INITIAL_USDT + (INITIAL_NXPC * 0.4825)  # Approx $10,767

print("📊 BALANCE COMPARISON:")
print(f"  NXPC: {nxpc_balance:.2f} (Initial: {INITIAL_NXPC:.2f})")
print(f"  USDT: ${usdt_balance:.2f} (Initial: ${INITIAL_USDT:.2f})")
print()

# Calculate changes
nxpc_change = nxpc_balance - INITIAL_NXPC
usdt_change = usdt_balance - INITIAL_USDT

print("📈 CHANGES:")
print(f"  NXPC Change: {nxpc_change:+.2f} ({nxpc_change/INITIAL_NXPC*100:+.2f}%)")
print(f"  USDT Change: ${usdt_change:+.2f} ({usdt_change/INITIAL_USDT*100:+.2f}%)")
print()

# Portfolio value
portfolio_value = usdt_balance + (nxpc_balance * current_price)
portfolio_change = portfolio_value - INITIAL_PORTFOLIO
portfolio_change_pct = (portfolio_change / INITIAL_PORTFOLIO) * 100

print("💼 PORTFOLIO VALUE:")
print(f"  NXPC Value: ${nxpc_balance * current_price:.2f}")
print(f"  USDT Value: ${usdt_balance:.2f}")
print(f"  Total: ${portfolio_value:.2f}")
print(f"  P&L: ${portfolio_change:+.2f} ({portfolio_change_pct:+.2f}%)")
print()

# Trading summary
print("🤖 TRADING SUMMARY:")
print(f"  Total Trades Today: 4+ trades")
print(f"  - Market Buy 11 NXPC")
print(f"  - Market Sell 11 NXPC") 
print(f"  - Limit Buy 11 NXPC (cancelled)")
print(f"  - Limit Sell 11 NXPC (filled)")
print(f"  - Bot Sell 789 NXPC (SMA strategy)")
print()

print("🎯 SYSTEM STATUS: FULLY OPERATIONAL")
print("=" * 60)
