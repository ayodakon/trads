"""
main.py - UPDATED WITH COMPOUNDING BOT
Main entry point for Trading Bot
"""
import time
import sys
import os
import warnings
from datetime import datetime
warnings.filterwarnings('ignore')

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import modules
from config.settings import settings  # Ini akan create directories
from config.api_config import api_config
from data.fetcher import DataFetcher
from strategies.sma_crossover import SMACrossover
from backtest.engine import BacktestEngine
from backtest.analyzer import ResultAnalyzer
from backtest.optimizer import StrategyOptimizer

# Import logger functions - PAKAI INI
from utils.logger import get_logger, log_info, log_warning, log_error, log_trade
from utils.visualization import ChartBuilder

# Initialize logger
logger = get_logger(logs_dir=settings.LOGS_DIR)


def main_menu():
    """Display main menu - UPDATED"""
    print("\n" + "="*60)
    print("🤖 TRADING BOT - BITGET")
    print("="*60)
    print("1. Run Backtest with Default Strategy")
    print("2. Optimize Strategy Parameters")
    print("3. Compare Multiple Strategies")
    print("4. Paper Trading & COMPOUNDING BOT")
    print("5. Paper Trade NXPC/USDT (BINANCE TESTNET)")
    print("6. View Settings")
    print("7. Exit")
    print("="*60)
    
    choice = input("Select option (1-7): ").strip()
    return choice


def run_backtest():
    """Run backtest with current strategy"""
    print("\n🔍 RUNNING BACKTEST")
    print("-" * 40)
    
    # Initialize
    fetcher = DataFetcher()
    strategy = SMACrossover(fast_period=settings.SMA_FAST, slow_period=settings.SMA_SLOW)
    backtester = BacktestEngine()
    
    # Fetch data
    print("Downloading market data...")
    df = fetcher.fetch_historical_data(days_back=settings.DEFAULT_DAYS_BACK)
    
    if df.empty:
        print("❌ Failed to fetch data!")
        return
    
    print(f"✅ Data loaded: {len(df)} candles")
    
    # Run backtest
    print("Running strategy...")
    results = backtester.run(df, strategy)
    
    # Print results
    backtester.print_results(results)
    
    # Analyze results
    analyzer = ResultAnalyzer(results)
    report = analyzer.generate_report()
    
    # Save results
    prefix = analyzer.save_results(strategy.name)
    
    # Plot results
    try:
        analyzer.plot_equity_curve(save=True)
        analyzer.plot_trade_distribution()
        
        # Create dashboard
        ChartBuilder.create_dashboard(results, strategy.name)
        
    except Exception as e:
        print(f"⚠️  Visualization error: {e}")
    
    print(f"\n📁 Results saved with prefix: {prefix}")
    logger.info(f"Backtest completed - Return: {results['total_return_pct']:.2f}%")


def run_optimization():
    """Optimize strategy parameters"""
    print("\n⚙️ STRATEGY OPTIMIZATION")
    print("-" * 40)
    
    optimizer = StrategyOptimizer()
    
    # Fetch data
    print("Downloading data for optimization...")
    df = optimizer.fetcher.fetch_historical_data(days_back=60)
    
    if df.empty:
        print("❌ Failed to fetch data!")
        return
    
    # Run optimization
    results_df = optimizer.optimize_sma(df)
    
    if not results_df.empty:
        # Plot heatmap
        optimizer.plot_optimization_heatmap(results_df)
        
        # Get best parameters
        best = results_df.sort_values('total_return', ascending=False).iloc[0]
        
        print("\n" + "="*60)
        print("✅ OPTIMIZATION COMPLETE")
        print("="*60)
        print(f"Recommended: SMA({best['fast_period']}/{best['slow_period']})")
        print(f"Expected Return: {best['total_return']:.2f}%")
        print(f"Win Rate: {best['win_rate']:.1f}%")
        print("="*60)
        
        # Ask to run backtest with optimized parameters
        run_optimized = input("\nRun backtest with optimized parameters? (y/n): ").strip().lower()
        
        if run_optimized == 'y':
            print("\nRunning optimized backtest...")
            
            strategy = SMACrossover(
                fast_period=int(best['fast_period']),
                slow_period=int(best['slow_period'])
            )
            
            backtester = BacktestEngine()
            results = backtester.run(df, strategy)
            backtester.print_results(results)
    
    logger.info("Strategy optimization completed")


def compare_strategies():
    """Compare multiple strategies"""
    print("\n📊 STRATEGY COMPARISON")
    print("-" * 40)
    
    strategies = [
        ("SMA(20/50)", SMACrossover(20, 50)),
        ("SMA(10/30)", SMACrossover(10, 30)),
        ("SMA(30/70)", SMACrossover(30, 70)),
    ]
    
    # Fetch data
    fetcher = DataFetcher()
    df = fetcher.fetch_historical_data(days_back=90)
    
    if df.empty:
        print("❌ Failed to fetch data!")
        return
    
    results_dict = {}
    
    for name, strategy in strategies:
        print(f"\nTesting {name}...")
        
        backtester = BacktestEngine()
        results = backtester.run(df, strategy)
        
        results_dict[name] = results
        
        print(f"  Return: {results['total_return_pct']:.2f}%")
        print(f"  Win Rate: {results['win_rate']:.1f}%")
    
    # Plot comparison
    try:
        ChartBuilder.plot_strategy_comparison(results_dict)
    except Exception as e:
        print(f"⚠️  Could not plot comparison: {e}")
    
    logger.info("Strategy comparison completed")


def paper_trading():
    """Paper trading mode - UPDATED WITH COMPOUNDING BOT"""
    print("\n📝 PAPER TRADING MODE")
    print("-" * 40)
    
    # Check API config
    if not api_config.validate_config():
        print("⚠️  API configuration required for paper trading")
        print("\nCreate .env file with:")
        print("BITGET_API_KEY=your_testnet_key")
        print("BITGET_SECRET=your_testnet_secret")
        print("BITGET_PASSPHRASE=your_passphrase")
        
        create_env = input("\nCreate .env template now? (y/n): ").strip().lower()
        if create_env == 'y':
            with open('.env', 'w') as f:
                f.write("# Bitget API (get from testnet.bitget.com)\n")
                f.write("BITGET_API_KEY=your_key_here\n")
                f.write("BITGET_SECRET=your_secret_here\n")
                f.write("BITGET_PASSPHRASE=your_passphrase_here\n")
                f.write("\n# Trading settings\n")
                f.write("USE_TESTNET=true\n")
            print("\n✅ .env template created!")
            print("1. Go to: https://testnet.bitget.com")
            print("2. Create account & get API keys")
            print("3. Edit .env file with your real keys")
            print("4. Run paper trading again")
        return
    
    # ⬇️ PAPER TRADING OPTIONS YANG DIPERBARUI ⬇️
    print("\n📊 PAPER TRADING OPTIONS:")
    print("1. Run SMA Strategy (Single Simulation)")
    print("2. Run SMA+RSI Combo Strategy")
    print("3. Start COMPOUNDING AUTO-TRADER BOT")
    print("4. Real-time Price Monitor")
    print("5. Back to Main Menu")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == '1':
        from strategies.sma_crossover import SMACrossover
        from paper_trade.simulator import PaperTradingSimulator
        
        print(f"\n🤖 LOADING SMA({settings.SMA_FAST}/{settings.SMA_SLOW}) STRATEGY...")
        strategy = SMACrossover(fast_period=settings.SMA_FAST, slow_period=settings.SMA_SLOW)
        
        # Get simulation settings
        try:
            days = int(input("Simulation days (1-90): ") or "30")
            days = max(1, min(days, 90))
        except:
            days = 30
        
        # Tanya compounding mode
        use_compounding = input("Enable compounding mode? (y/n, default: y): ").strip().lower()
        compounding = False if use_compounding == 'n' else True
        
        if compounding:
            initial_balance = float(input(f"Initial balance in USD (default: ${settings.PAPER_INITIAL_BALANCE:.2f}): ") or settings.PAPER_INITIAL_BALANCE)
        else:
            initial_balance = float(input("Initial balance in USD (default: 1000): ") or "1000")
        
        simulator = PaperTradingSimulator(
            strategy=strategy, 
            initial_balance=initial_balance,
            compounding=compounding
        )
        
        print(f"\n🚀 STARTING PAPER TRADING SIMULATION")
        print(f"   Strategy: {strategy.name}")
        print(f"   Compounding: {'ENABLED ✅' if compounding else 'DISABLED'}")
        print(f"   Duration: {days} days")
        print(f"   Initial Balance: ${initial_balance:.2f}")
        print(f"   Stop Loss: {settings.DEFAULT_STOP_LOSS*100:.1f}%")
        print("   (Simulation will run in accelerated time)")
        print("-" * 50)
        
        input("Press Enter to start simulation...")
        
        simulator.run(days=days)
        
    elif choice == '2':
        try:
            from strategies.sma_rsi_combo import SMA_RSI_Combo
            from paper_trade.simulator import PaperTradingSimulator
            
            print("\n🤖 LOADING SMA+RSI COMBO STRATEGY...")
            strategy = SMA_RSI_Combo(
                sma_fast=50, 
                sma_slow=80, 
                rsi_period=14,
                rsi_overbought=65,
                rsi_oversold=35
            )
            
            initial_balance = 1000
            simulator = PaperTradingSimulator(strategy, initial_balance)
            
            print(f"\n🚀 STARTING SMA+RSI PAPER TRADING")
            print(f"   Strategy: {strategy.name}")
            simulator.run(days=3)
            
        except ImportError as e:
            print(f"❌ Error: {e}")
            print("Make sure strategies/sma_rsi_combo.py exists!")
    
    elif choice == '3':  # ⬅️ OPTION BARU: COMPOUNDING BOT
        print("\n🤖 STARTING COMPOUNDING AUTO-TRADER BOT")
        print("-" * 40)
        
        try:
            # Check required packages
            try:
                import schedule
                import pandas as pd
                import ccxt
            except ImportError as e:
                print(f"❌ Missing required package: {e}")
                print("\nPlease install required packages:")
                print("pip install schedule pandas ccxt")
                return
            
            # Import compounding bot
            try:
                from compounding_bot import CompoundingTradingBot
            except ImportError:
                print("❌ compounding_bot.py not found!")
                print("Please make sure compounding_bot.py exists in the root directory.")
                return
            
            # Get starting capital
            try:
                initial_nxpc = float(input(f"Starting NXPC amount (default: 15): ") or "15")
                if initial_nxpc <= 0:
                    print("❌ Starting amount must be positive!")
                    return
            except:
                initial_nxpc = 15
            
            # Confirm settings
            current_price = 0.45  # Estimate for display
            initial_usd = initial_nxpc * current_price
            
            print(f"\n📋 BOT SETTINGS:")
            print(f"   Starting Capital: {initial_nxpc} NXPC (≈${initial_usd:.2f})")
            print(f"   Strategy: SMA({settings.SMA_FAST}/{settings.SMA_SLOW})")
            print(f"   Stop Loss: {settings.DEFAULT_STOP_LOSS*100:.1f}%")
            print(f"   Compounding: ENABLED ✅")
            print(f"   Trade Frequency: Every hour")
            print(f"   Min Trade Size: ${settings.MIN_TRADE_SIZE}")
            
            confirm = input("\nStart bot with these settings? (y/n): ").strip().lower()
            
            if confirm != 'y':
                print("❌ Bot startup cancelled.")
                return
            
            # Create and run bot
            print(f"\n🚀 LAUNCHING COMPOUNDING BOT...")
            print("   The bot will run continuously in the background.")
            print("   It will check the market and trade every hour.")
            print("   Press Ctrl+C in this terminal to stop the bot.")
            print("-" * 50)
            
            # Countdown
            for i in range(3, 0, -1):
                print(f"   Starting in {i}...")
                time.sleep(1)
            
            bot = CompoundingTradingBot(initial_nxpc=initial_nxpc)
            bot.run()
            
        except ImportError as e:
            print(f"❌ Import Error: {e}")
            print("\nPlease install required packages:")
            print("pip install schedule pandas ccxt")
        except Exception as e:
            print(f"❌ Error starting bot: {e}")
            import traceback
            traceback.print_exc()
            logger.error(f"Compounding bot error: {e}")
    
    elif choice == '4':
        print("\n📈 REAL-TIME PRICE MONITOR")
        print("-" * 40)
        
        from data.fetcher import DataFetcher
        
        fetcher = DataFetcher()
        print("Starting real-time price monitor...")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                price_data = fetcher.fetch_current_price('NXPC/USDT')
                if price_data:
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    print(f"[{timestamp}] "
                          f"NXPC: ${price_data['price']:,.4f} | "
                          f"Change: {price_data['change']:+.2f}% | "
                          f"Vol: ${price_data['volume']:,.0f}")
                time.sleep(5)  # Update every 5 seconds
                
        except KeyboardInterrupt:
            print("\n⏹️  Price monitor stopped")
        except Exception as e:
            print(f"\n⚠️  Price monitor error: {e}")
    
    elif choice == '5':
        return  # Back to main menu
    
    else:
        print("❌ Invalid choice!")
    
    log_info("Paper trading session completed")


def paper_trade_nxpc():
    """Paper trading khusus untuk NXPC/USDT di Binance Testnet"""
    print("\n" + "="*60)
    print("📊 PAPER TRADE NXPC/USDT - BINANCE TESTNET")
    print("="*60)
    
    # Pilih mode
    print("\n🎯 Pilih Mode:")
    print("1. Market Data & Analysis")
    print("2. Simulasi Trading (Paper Trade)")
    print("3. Eksekusi Real di Testnet (Fake Money)")
    print("4. Kembali ke Menu Utama")
    
    choice = input("\nPilih opsi (1-4): ").strip()
    
    if choice == '1':
        nxpc_market_analysis()
    elif choice == '2':
        nxpc_paper_trade_sim()
    elif choice == '3':
        nxpc_real_testnet()
    elif choice == '4':
        return
    else:
        print("❌ Pilihan tidak valid!")

def nxpc_market_analysis():
    """Analisis market NXPC/USDT"""
    print("\n📈 ANALISIS MARKET NXPC/USDT")
    print("-" * 40)
    
    try:
        from binance.client import Client
        
        # Load API keys dari file python_binance.py atau .env
        try:
            # Coba import dari file yang ada
            import python_binance
            api_key = python_binance.api_key
            api_secret = python_binance.api_secret
        except:
            print("⚠️  API Key tidak ditemukan!")
            print("\nBuat file python_binance.py dengan struktur:")
            print("api_key = 'API_KEY_ANDA'")
            print("api_secret = 'SECRET_KEY_ANDA'")
            return
        
        # Inisialisasi client
        client = Client(api_key, api_secret, testnet=True)
        
        # 1. Dapatkan info pair
        symbol_info = client.get_symbol_info('NXPCUSDT')
        print("✅ Pair NXPC/USDT tersedia")
        print(f"   Status: {symbol_info['status']}")
        
        # 2. Harga saat ini
        ticker = client.get_symbol_ticker(symbol='NXPCUSDT')
        current_price = float(ticker['price'])
        print(f"\n💰 Harga saat ini: ${current_price:.6f}")
        
        # 3. Order Book (depth)
        print("\n📊 Order Book (Top 5):")
        depth = client.get_order_book(symbol='NXPCUSDT', limit=5)
        
        print("   BELI (Bids):")
        for bid in depth['bids'][:3]:
            price = float(bid[0])
            qty = float(bid[1])
            print(f"     ${price:.6f} - {qty:.0f} NXPC")
        
        print("\n   JUAL (Asks):")
        for ask in depth['asks'][:3]:
            price = float(ask[0])
            qty = float(ask[1])
            print(f"     ${price:.6f} - {qty:.0f} NXPC")
        
        # 4. Recent trades
        print("\n🔄 Recent Trades:")
        trades = client.get_recent_trades(symbol='NXPCUSDT', limit=5)
        for trade in trades:
            side = "BUY" if trade['isBuyerMaker'] else "SELL"
            qty = float(trade['qty'])
            price = float(trade['price'])
            print(f"   {side}: {qty:.1f} NXPC @ ${price:.6f}")
        
        # 5. Volume 24h
        ticker_24h = client.get_ticker(symbol='NXPCUSDT')
        volume = float(ticker_24h['volume'])
        price_change = float(ticker_24h['priceChangePercent'])
        
        print(f"\n📈 Volume 24h: {volume:.0f} NXPC")
        print(f"   Perubahan: {price_change:+.2f}%")
        
        # 6. Balance akun
        print("\n💼 Balance Akun Anda:")
        account = client.get_account()
        for balance in account['balances']:
            if balance['asset'] in ['NXPC', 'USDT', 'BTC', 'ETH']:
                free = float(balance['free'])
                if free > 0:
                    print(f"   {balance['asset']}: {free:.6f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def nxpc_paper_trade_sim():
    """Simulasi paper trading untuk NXPC/USDT"""
    print("\n📝 SIMULASI PAPER TRADING NXPC/USDT")
    print("-" * 40)
    
    try:
        from binance.client import Client
        
        # Load API keys
        try:
            import python_binance
            api_key = python_binance.api_key
            api_secret = python_binance.api_secret
        except:
            print("⚠️  API Key tidak ditemukan!")
            return
        
        client = Client(api_key, api_secret, testnet=True)
        
        # Dapatkan data
        ticker = client.get_symbol_ticker(symbol='NXPCUSDT')
        current_price = float(ticker['price'])
        
        # Balance awal (dummy atau dari API)
        account = client.get_account()
        nxpc_balance = 0
        usdt_balance = 0
        
        for balance in account['balances']:
            if balance['asset'] == 'NXPC':
                nxpc_balance = float(balance['free'])
            elif balance['asset'] == 'USDT':
                usdt_balance = float(balance['free'])
        
        print(f"\n💼 Balance Awal:")
        print(f"   NXPC: {nxpc_balance:.2f}")
        print(f"   USDT: ${usdt_balance:.2f}")
        print(f"\n💰 Harga NXPC/USDT: ${current_price:.6f}")
        
        # Menu simulasi
        print("\n🎯 Simulasi Trading:")
        print("1. Beli NXPC (Market)")
        print("2. Jual NXPC (Market)")
        print("3. Set Limit Order")
        print("4. Lihat hasil simulasi")
        print("5. Kembali")
        
        # Tracking simulasi
        simulated_trades = []
        simulated_nxpc = nxpc_balance
        simulated_usdt = usdt_balance
        
        while True:
            choice = input("\nPilih aksi (1-5): ").strip()
            
            if choice == '1':
                try:
                    amount = float(input("Jumlah NXPC yang ingin dibeli: "))
                    cost = amount * current_price
                    
                    if simulated_usdt >= cost:
                        simulated_nxpc += amount
                        simulated_usdt -= cost
                        
                        simulated_trades.append({
                            'type': 'BUY',
                            'amount': amount,
                            'price': current_price,
                            'cost': cost,
                            'timestamp': datetime.now().strftime('%H:%M:%S')
                        })
                        
                        print(f"✅ SIMULASI: Beli {amount:.2f} NXPC @ ${current_price:.6f}")
                        print(f"   Biaya: ${cost:.4f}")
                    else:
                        print(f"❌ Saldo USDT tidak cukup! Butuh ${cost:.2f}, punya ${simulated_usdt:.2f}")
                        
                except ValueError:
                    print("❌ Input tidak valid!")
                    
            elif choice == '2':
                try:
                    amount = float(input("Jumlah NXPC yang ingin dijual: "))
                    
                    if simulated_nxpc >= amount:
                        revenue = amount * current_price
                        simulated_nxpc -= amount
                        simulated_usdt += revenue
                        
                        simulated_trades.append({
                            'type': 'SELL',
                            'amount': amount,
                            'price': current_price,
                            'revenue': revenue,
                            'timestamp': datetime.now().strftime('%H:%M:%S')
                        })
                        
                        print(f"✅ SIMULASI: Jual {amount:.2f} NXPC @ ${current_price:.6f}")
                        print(f"   Pendapatan: ${revenue:.4f}")
                    else:
                        print(f"❌ Saldo NXPC tidak cukup! Butuh {amount:.2f}, punya {simulated_nxpc:.2f}")
                        
                except ValueError:
                    print("❌ Input tidak valid!")
                    
            elif choice == '3':
                print("\n⚠️  Limit order simulation coming soon!")
                
            elif choice == '4':
                print("\n📊 HASIL SIMULASI:")
                print(f"   Balance NXPC: {simulated_nxpc:.2f}")
                print(f"   Balance USDT: ${simulated_usdt:.2f}")
                
                total_value = simulated_usdt + (simulated_nxpc * current_price)
                initial_value = usdt_balance + (nxpc_balance * current_price)
                pnl = total_value - initial_value
                
                print(f"   Total Value: ${total_value:.2f}")
                print(f"   P&L: ${pnl:+.2f} ({pnl/initial_value*100:+.2f}%)")
                
                if simulated_trades:
                    print(f"\n📋 Riwayat Trade ({len(simulated_trades)}):")
                    for i, trade in enumerate(simulated_trades, 1):
                        if trade['type'] == 'BUY':
                            print(f"   {i}. BUY {trade['amount']:.2f} NXPC @ ${trade['price']:.6f}")
                        else:
                            print(f"   {i}. SELL {trade['amount']:.2f} NXPC @ ${trade['price']:.6f}")
                
            elif choice == '5':
                break
                
            else:
                print("❌ Pilihan tidak valid!")
                
    except Exception as e:
        print(f"❌ Error: {e}")

def nxpc_real_testnet():
    """Eksekusi real di Binance Testnet (fake money)"""
    print("\n🚀 REAL TESTNET TRADING NXPC/USDT")
    print("-" * 40)
    print("⚠️  PERINGATAN: Ini akan eksekusi order REAL di Binance Testnet")
    print("    Menggunakan FAKE MONEY (uang dummy)")
    print("-" * 40)
    
    confirm = input("\nLanjutkan? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Dibatalkan!")
        return
    
    try:
        from binance.client import Client
        
        # Load API keys
        try:
            import python_binance
            api_key = python_binance.api_key
            api_secret = python_binance.api_secret
        except:
            print("⚠️  API Key tidak ditemukan!")
            return
        
        client = Client(api_key, api_secret, testnet=True)
        
        # Cek balance dulu
        print("\n💼 Balance Akun:")
        account = client.get_account()
        for balance in account['balances']:
            if balance['asset'] in ['NXPC', 'USDT']:
                free = float(balance['free'])
                if free > 0:
                    print(f"   {balance['asset']}: {free:.6f}")
        
        # Cek harga
        ticker = client.get_symbol_ticker(symbol='NXPCUSDT')
        current_price = float(ticker['price'])
        print(f"\n💰 Harga NXPC/USDT: ${current_price:.6f}")
        
        # Menu trading
        print("\n🎯 Pilih Aksi:")
        print("1. Market Buy")
        print("2. Market Sell")
        print("3. Limit Buy")
        print("4. Limit Sell")
        print("5. Lihat Open Orders")
        print("6. Cancel Order")
        print("7. Kembali")
        
        while True:
            choice = input("\nPilih (1-7): ").strip()
            
            if choice == '1':
                try:
                    qty = float(input("Jumlah NXPC yang ingin dibeli: "))
                    
                    # Cek min quantity (0.1)
                    if qty < 0.1:
                        print(f"❌ Minimal beli 0.1 NXPC")
                        continue
                    
                    print(f"\n⚠️  Eksekusi MARKET BUY...")
                    print(f"   Jumlah: {qty} NXPC")
                    print(f"   Harga: ~${current_price:.6f}")
                    
                    confirm = input("\nKonfirmasi order? (y/n): ").strip().lower()
                    if confirm == 'y':
                        order = client.order_market_buy(
                            symbol='NXPCUSDT',
                            quantity=qty
                        )
                        print(f"\n✅ ORDER BERHASIL!")
                        print(f"   Order ID: {order['orderId']}")
                        print(f"   Status: {order['status']}")
                        print(f"   Executed: {order['executedQty']} NXPC")
                        print(f"   Cost: {order['cummulativeQuoteQty']} USDT")
                    else:
                        print("❌ Order dibatalkan")
                        
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
            elif choice == '2':
                try:
                    qty = float(input("Jumlah NXPC yang ingin dijual: "))
                    
                    if qty < 0.1:
                        print(f"❌ Minimal jual 0.1 NXPC")
                        continue
                    
                    print(f"\n⚠️  Eksekusi MARKET SELL...")
                    print(f"   Jumlah: {qty} NXPC")
                    print(f"   Harga: ~${current_price:.6f}")
                    
                    confirm = input("\nKonfirmasi order? (y/n): ").strip().lower()
                    if confirm == 'y':
                        order = client.order_market_sell(
                            symbol='NXPCUSDT',
                            quantity=qty
                        )
                        print(f"\n✅ ORDER BERHASIL!")
                        print(f"   Order ID: {order['orderId']}")
                        print(f"   Status: {order['status']}")
                        print(f"   Executed: {order['executedQty']} NXPC")
                        print(f"   Revenue: {order['cummulativeQuoteQty']} USDT")
                    else:
                        print("❌ Order dibatalkan")
                        
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
            elif choice == '3':  # Limit Buy
                try:
                    qty = float(input("Jumlah NXPC yang ingin dibeli: "))
                    
                    if qty < 0.1:
                        print(f"❌ Minimal beli 0.1 NXPC")
                        continue
                    
                    current_price = float(ticker['price'])
                    limit_price = float(input(f"Harga limit (current: ${current_price:.4f}): ") or str(round(current_price * 0.99, 4)))
                    
                    order_value = qty * limit_price
                    if order_value < 5:
                        print(f"❌ Order value terlalu kecil! Minimal $5.00")
                        print(f"   Value: ${order_value:.2f}")
                        continue
                    
                    print(f"\n⚠️  Eksekusi LIMIT BUY...")
                    print(f"   Jumlah: {qty} NXPC")
                    print(f"   Harga limit: ${limit_price:.4f}")
                    print(f"   Total: ${order_value:.2f}")
                    
                    confirm = input("\nKonfirmasi order? (y/n): ").strip().lower()
                    if confirm == 'y':
                        order = client.order_limit_buy(
                            symbol='NXPCUSDT',
                            quantity=qty,
                            price=str(limit_price)
                        )
                        print(f"\n✅ LIMIT BUY ORDER BERHASIL!")
                        print(f"   Order ID: {order['orderId']}")
                        print(f"   Status: {order['status']}")
                        print(f"   Price: ${order['price']}")
                        print(f"   Quantity: {order['origQty']} NXPC")
                    else:
                        print("❌ Order dibatalkan")
                        
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
            elif choice == '4':  # Limit Sell
                try:
                    qty = float(input("Jumlah NXPC yang ingin dijual: "))
                    
                    if qty < 0.1:
                        print(f"❌ Minimal jual 0.1 NXPC")
                        continue
                    
                    current_price = float(ticker['price'])
                    limit_price = float(input(f"Harga limit (current: ${current_price:.4f}): ") or str(round(current_price * 1.01, 4)))
                    
                    order_value = qty * limit_price
                    if order_value < 5:
                        print(f"❌ Order value terlalu kecil! Minimal $5.00")
                        print(f"   Value: ${order_value:.2f}")
                        continue
                    
                    print(f"\n⚠️  Eksekusi LIMIT SELL...")
                    print(f"   Jumlah: {qty} NXPC")
                    print(f"   Harga limit: ${limit_price:.4f}")
                    print(f"   Total: ${order_value:.2f}")
                    
                    confirm = input("\nKonfirmasi order? (y/n): ").strip().lower()
                    if confirm == 'y':
                        order = client.order_limit_sell(
                            symbol='NXPCUSDT',
                            quantity=qty,
                            price=str(limit_price)
                        )
                        print(f"\n✅ LIMIT SELL ORDER BERHASIL!")
                        print(f"   Order ID: {order['orderId']}")
                        print(f"   Status: {order['status']}")
                        print(f"   Price: ${order['price']}")
                        print(f"   Quantity: {order['origQty']} NXPC")
                    else:
                        print("❌ Order dibatalkan")
                        
                except Exception as e:
                    print(f"❌ Error: {e}")
                
            elif choice == '5':
                try:
                    orders = client.get_open_orders(symbol='NXPCUSDT')
                    if orders:
                        print(f"\n📋 Open Orders ({len(orders)}):")
                        for order in orders:
                            print(f"   ID: {order['orderId']} | {order['side']} {order['origQty']} @ ${order['price']}")
                    else:
                        print("📭 Tidak ada open orders")
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
            elif choice == '6':
                try:
                    order_id = input("Order ID yang ingin dicancel: ").strip()
                    result = client.cancel_order(symbol='NXPCUSDT', orderId=order_id)
                    print(f"✅ Order {order_id} dicancel!")
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
            elif choice == '7':
                break
                
            else:
                print("❌ Pilihan tidak valid!")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def view_settings():
    """Display current settings"""
    settings.print_settings()
    
    if api_config.USE_TESTNET:
        print("\n📡 API MODE: TESTNET (Sandbox)")
    else:
        print("\n📡 API MODE: LIVE TRADING")
        if api_config.BITGET_API_KEY:
            print("✅ API Key: Configured")
        else:
            print("❌ API Key: Not configured")
    
    # Show compounding bot settings
    print(f"\n🤖 COMPOUNDING BOT SETTINGS:")
    print(f"   Initial NXPC: {settings.PAPER_INITIAL_BALANCE/0.45:.1f} NXPC")
    print(f"   Min Trade Size: ${settings.MIN_TRADE_SIZE}")
    print(f"   Max Position: {settings.MAX_POSITION_SIZE*100:.0f}%")
    print(f"   Trade Frequency: {settings.TRADE_FREQUENCY}")
    print(f"   Compounding: {'ENABLED ✅' if settings.COMPOUNDING_ENABLED else 'DISABLED'}")


def main():
    """Main program loop"""
    logger.info("Trading Bot started")
    
    while True:
        try:
            choice = main_menu()
            
            if choice == '1':
                run_backtest()
            
            elif choice == '2':
                run_optimization()
            
            elif choice == '3':
                compare_strategies()
            
            elif choice == '4':
                paper_trading()

            elif choice == '5':
                paper_trade_nxpc()
            
            elif choice == '6':
                view_settings()
            
            elif choice == '7':
                print("\n👋 Goodbye!")
                logger.info("Trading Bot stopped")
                break
            
            else:
                print("\n❌ Invalid choice!")
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
            break
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logger.error(f"Main loop error: {e}")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    # Check if running in correct directory
    required_folders = ['config', 'data', 'strategies', 'backtest', 'paper_trade', 'utils']
    
    for folder in required_folders:
        if not os.path.exists(folder):
            print(f"❌ Missing folder: {folder}")
            print("Please run from project root directory")
            sys.exit(1)
    
    # Check for compounding_bot.py
    if not os.path.exists('compounding_bot.py'):
        print("⚠️  Note: compounding_bot.py not found")
        print("The compounding bot feature will not be available")
        print("Make sure compounding_bot.py is in the root directory")
    
    # Start main program
    main()