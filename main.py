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
    print("4. Paper Trading & COMPOUNDING BOT")  # ⬅️ UPDATE NAMA
    print("5. View Settings")
    print("6. Exit")
    print("="*60)
    
    choice = input("Select option (1-6): ").strip()
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
                view_settings()
            
            elif choice == '6':
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