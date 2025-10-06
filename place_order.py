from pybit.unified_trading import HTTP
import os

# Set your API credentials
api_key = os.getenv("BYBIT_API_KEY")
api_secret = os.getenv("BYBIT_API_SECRET")

# Initialize Bybit session (mainnet endpoint)
session = HTTP(testnet=False,api_key=api_key,api_secret=api_secret,)

symbol = "SOLUSDT"
qty = 10
entry_price = 24.50
tp_price = 22.00
sl_price = 25.50
leverage = 10

# 1. Check if there is an existing position
pos_info = session.get_positions(category="linear",symbol=symbol,)
positions = pos_info['result']['list']
open_pos_size = 0
for pos in positions:
    # For USDT-margined, check for "side" and "size"
    if pos['side'] in ["Buy", "Sell"] and float(pos['size']) != 0:
        open_pos_size = float(pos['size'])
        break

if open_pos_size == 0:
    # 2. Set leverage
    session.set_leverage(category="linear",symbol=symbol,buyLeverage=leverage,sellLeverage=leverage,)
    print("Leverage set to", leverage, "x.")

    # 3. Place short order with TP/SL attached
    order = session.place_order( category="linear",symbol=symbol,side="Sell",orderType="Limit",qty=qty,
                                    price=entry_price,timeInForce="PostOnly",reduceOnly=False,
                                    takeProfit=tp_price,stopLoss=sl_price,tpTriggerBy="LastPrice",slTriggerBy="LastPrice",)
    print("Short entry order placed:", order)
else:
    print(f"Open position detected (size={open_pos_size}). No new order placed.")
