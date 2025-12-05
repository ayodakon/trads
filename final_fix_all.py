import os

files_with_settings = [
    'data/fetcher.py',
    'strategies/sma_crossover.py',
    'risk/manager.py', 
    'backtest/analyzer.py',
    'backtest/optimizer.py',
    'utils/visualization.py',
    'setup_live_paper.py',
    'compounding_bot.py',
    'strategies/sma_rsi_combo.py'
]

print("🚀 FIXING ALL SETTINGS IMPORTS...")
print("="*60)

for file_path in files_with_settings:
    if not os.path.exists(file_path):
        print(f"⚠️  Skipping (not found): {file_path}")
        continue
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Skip jika sudah ada import yang benar
    if 'from config.settings import settings' in content:
        print(f"✅ {file_path}: Already has correct import")
        continue
    
    # Skip jika tidak pakai settings.
    if 'settings.' not in content:
        print(f"⏭️  {file_path}: Doesn't use settings, skipping")
        continue
    
    # Tambah import di baris pertama (atau setelah shebang)
    lines = content.split('\n')
    new_lines = []
    added = False
    
    for i, line in enumerate(lines):
        # Baris pertama adalah shebang
        if i == 0 and line.startswith('#!'):
            new_lines.append(line)
            new_lines.append('from config.settings import settings')
            added = True
        # Baris pertama bukan shebang
        elif i == 0 and not added:
            new_lines.append('from config.settings import settings')
            new_lines.append(line)
            added = True
        else:
            new_lines.append(line)
    
    # Jika belum ditambah (kasus khusus)
    if not added:
        new_lines.insert(0, 'from config.settings import settings')
    
    # Write back
    with open(file_path, 'w') as f:
        f.write('\n'.join(new_lines))
    
    print(f"✅ {file_path}: Added import")

print("\n" + "="*60)
print("🎯 VERIFICATION TEST")

# Test imports
test_files = [
    'data/fetcher.py',
    'backtest/analyzer.py', 
    'utils/visualization.py'
]

for file_path in test_files:
    print(f"\n📄 Testing {file_path}:")
    try:
        # Execute first 50 lines untuk test import
        with open(file_path, 'r') as f:
            exec(f.read()[:500])
        print("   ✅ Can be executed")
    except Exception as e:
        print(f"   ❌ Error: {type(e).__name__}")

print("\n" + "="*60)
print("🎯 FINAL SETTINGS TEST")
try:
    from config.settings import settings
    print("✅ Global settings import successful")
    
    critical = ['RESULTS_DIR', 'REPORTS_DIR', 'SMA_FAST', 'SMA_SLOW', 'DEFAULT_STOP_LOSS', 'DATA_DIR']
    for attr in critical:
        value = getattr(settings, attr, 'NOT FOUND')
        print(f"   {attr}: {value}")
        
except Exception as e:
    print(f"❌ Error: {e}")