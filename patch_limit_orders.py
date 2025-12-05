#!/usr/bin/env python3
"""
Patch main.py untuk add limit orders functionality
"""
import re

with open('main.py', 'r') as f:
    content = f.read()

# Find the limit buy/sell placeholder
old_code = '''            elif choice == '3':
                print("\\n⚠️  Limit buy coming soon!")
                
            elif choice == '4':
                print("\\n⚠️  Limit sell coming soon!")'''

new_code = '''            elif choice == '3':  # Limit Buy
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
                    
                    print(f"\\n⚠️  Eksekusi LIMIT BUY...")
                    print(f"   Jumlah: {qty} NXPC")
                    print(f"   Harga limit: ${limit_price:.4f}")
                    print(f"   Total: ${order_value:.2f}")
                    
                    confirm = input("\\nKonfirmasi order? (y/n): ").strip().lower()
                    if confirm == 'y':
                        order = client.order_limit_buy(
                            symbol='NXPCUSDT',
                            quantity=qty,
                            price=str(limit_price)
                        )
                        print(f"\\n✅ LIMIT BUY ORDER BERHASIL!")
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
                    
                    print(f"\\n⚠️  Eksekusi LIMIT SELL...")
                    print(f"   Jumlah: {qty} NXPC")
                    print(f"   Harga limit: ${limit_price:.4f}")
                    print(f"   Total: ${order_value:.2f}")
                    
                    confirm = input("\\nKonfirmasi order? (y/n): ").strip().lower()
                    if confirm == 'y':
                        order = client.order_limit_sell(
                            symbol='NXPCUSDT',
                            quantity=qty,
                            price=str(limit_price)
                        )
                        print(f"\\n✅ LIMIT SELL ORDER BERHASIL!")
                        print(f"   Order ID: {order['orderId']}")
                        print(f"   Status: {order['status']}")
                        print(f"   Price: ${order['price']}")
                        print(f"   Quantity: {order['origQty']} NXPC")
                    else:
                        print("❌ Order dibatalkan")
                        
                except Exception as e:
                    print(f"❌ Error: {e}")'''

# Replace the code
if old_code in content:
    content = content.replace(old_code, new_code)
    with open('main.py', 'w') as f:
        f.write(content)
    print("✅ main.py updated dengan limit orders!")
else:
    print("❌ Tidak menemukan code yang sesuai")
    print("Cari manual di main.py bagian:")
    print("'Limit buy coming soon!'")
