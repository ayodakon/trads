import python_binance
import time

client = python_binance.get_client()

# Get current price
ticker = client.get_symbol_ticker(symbol='NXPCUSDT')
current_price = float(ticker['price'])

print(f"💰 Current Price: ${current_price}")

# Set limit price 1% below current
limit_price = round(current_price * 0.99, 4)
quantity = 11  # Above $5 minimum

print(f"\n📊 Setting LIMIT BUY Order:")
print(f"   Quantity: {quantity} NXPC")
print(f"   Limit Price: ${limit_price} (-1%)")
print(f"   Total Value: ${quantity * limit_price:.2f}")

confirm = input("\nPlace limit buy order? (y/n): ")

if confirm.lower() == 'y':
    try:
        order = client.order_limit_buy(
            symbol='NXPCUSDT',
            quantity=quantity,
            price=str(limit_price)
        )
        
        print(f"\n✅ LIMIT ORDER PLACED!")
        print(f"   Order ID: {order['orderId']}")
        print(f"   Status: {order['status']}")  # Should be NEW
        print(f"   Price: ${order['price']}")
        print(f"   Quantity: {order['origQty']} NXPC")
        
        # Check open orders
        time.sleep(1)
        print(f"\n🔍 Checking open orders...")
        open_orders = client.get_open_orders(symbol='NXPCUSDT')
        print(f"   Open orders: {len(open_orders)}")
        
        if open_orders:
            print(f"\n📋 Open Orders Details:")
            for o in open_orders:
                print(f"   ID: {o['orderId']}, {o['side']} {o['origQty']} @ ${o['price']}")
            
            # Ask to cancel
            cancel = input("\nCancel this limit order? (y/n): ")
            if cancel.lower() == 'y':
                result = client.cancel_order(
                    symbol='NXPCUSDT',
                    orderId=order['orderId']
                )
                print(f"✅ Order cancelled!")
                
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("❌ Order cancelled")
