from client import http_client
from imports import *

session = http_client

# 1. Check if there is an existing position
pos_info = session.get_positions(category=config.category,symbol=config.symbol,)
positions = pos_info['result']['list']
open_pos_size = 0
for pos in positions:
    # For USDT-margined, check for "side" and "size"
    if pos['side'] in ["Buy", "Sell"] and float(pos['size']) != 0:
        open_pos_size = float(pos['size'])
        break

if open_pos_size == 0:
    # 2. Set leverage
    session.set_leverage(category=config.category,symbol=config.symbol,buyLeverage=config.leverage,sellLeverage=config.leverage,)
    print("Leverage set to", config.leverage, "x.")

    # 3. Place short order with TP/SL attached
    order = session.place_order( category=config.category,symbol=config.symbol,side="Sell",orderType="Limit",qty=qty,
                                    price=entry_price,timeInForce="PostOnly",reduceOnly=False,
                                    takeProfit=tp_price,stopLoss=sl_price,tpTriggerBy="LastPrice",slTriggerBy="LastPrice",)
    print("Short entry order placed:", order)
else:
    print(f"Open position detected (size={open_pos_size}). No new order placed.")
