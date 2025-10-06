import asyncio
import datetime
import decimal

import config
from fetcher import KlineFetcher
from streamer import WebSocketStreamer
from utils import *
from client import http_client


# Shared state
threshold_container = []
state_container = []
open_position = {"size": 0, "side": None, "entry_price": None, "tp": None, "sl": None}

async def update_threshold(fetcher):
    while True:
        now = datetime.datetime.now(fetcher.ist)
        # wait till hh:mm:03
        next_update = now.replace(second=3, microsecond=0)
        if now.second >= 3:
            next_update += datetime.timedelta(minutes=1)
        await asyncio.sleep((next_update - now).total_seconds())

        try:
            threshold_container[0] = fetcher.get_klines()
            print(f"Threshold updated: {threshold_container[0]} at {datetime.datetime.now(fetcher.ist)}")
        except Exception as e:
            print(f"Threshold update error: {e}")

def get_open_position(session, symbol):
    pos_info = session.get_positions(category="linear", symbol=symbol)
    for pos in pos_info['result']['list']:
        if pos['side'] in ["Buy", "Sell"] and float(pos['size']) != 0:
            return {
                "size": float(pos["size"]),
                "side": pos["side"],
                "entry_price": float(pos.get("entry_price", 0)),
                "tp": None,  # fill if available
                "sl": None   # fill if available
            }
    return {"size": 0, "side": None, "entry_price": None, "tp": None, "sl": None}

async def print_status(session, symbol):
    while True:
        pos = get_open_position(session, symbol)
        open_position.update(pos)
        threshold = threshold_container[0] if threshold_container else None
        print(f"Open pos: size={pos['size']}, side={pos['side']} | Threshold: {threshold}")
        await asyncio.sleep(3)

async def price_callback(price, session, symbol, leverage, qty, tp_price, sl_price):
    price_val = decimal.Decimal(price)
    threshold = threshold_container[0] if threshold_container else None
    if threshold is None:
        return

    pos = get_open_position(session, symbol)
    # If price >= threshold and no open position, place order
    if price_val >= threshold and pos["size"] == 0:
        session.set_leverage(category="linear", symbol=symbol, buyLeverage=leverage, sellLeverage=leverage)
        print(f"Leverage set to {leverage}x.")
        order = session.place_order(
            category="linear", symbol=symbol, side="Sell", orderType="Limit", qty=qty,
            price=price_val, timeInForce="PostOnly", reduceOnly=False,
            takeProfit=tp_price, stopLoss=sl_price, tpTriggerBy="LastPrice", slTriggerBy="LastPrice"
        )
        print("Short order placed:", order)
    elif pos["size"] > 0:
        # Position open; optionally react or track
        pass

    # Detect order closure
    new_pos = get_open_position(session, symbol)
    if open_position["size"] > 0 and new_pos["size"] == 0:
        print("Order closed.")
        open_position.update(new_pos)

async def main():
    fetcher = KlineFetcher(config.symbol, config.category)
    threshold_container.append(fetcher.get_klines())
    state_container.append(False)

    # Your session and trading parameters here
    session = http_client
    symbol = config.symbol
    leverage = config.leverage
    qty = 0.1
    tp_price = 30000
    sl_price = 35000

    threshold_task = asyncio.create_task(update_threshold(fetcher))
    status_task = asyncio.create_task(print_status(session, symbol))
    streamer = WebSocketStreamer(symbol)

    async def callback(price):
        await price_callback(price, session, symbol, leverage, qty, tp_price, sl_price)

    streamer_task = asyncio.create_task(streamer.start(callback))

    await asyncio.gather(threshold_task, status_task, streamer_task)

if __name__ == "__main__":
    asyncio.run(main())



