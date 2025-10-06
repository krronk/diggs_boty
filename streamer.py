import asyncio
from pybit.unified_trading import WebSocket
import config  # assumes config.symbol, config.testnet, config.channel_type are set

class WebSocketStreamer:
    def __init__(self):
        self.symbol = config.symbol
        self.ws = WebSocket(testnet=False, channel_type=config.category)
        self.price_callback = None

    def trade_callback(self, msg):
        # This callback receives and processes incoming trade messages
        if "data" in msg and msg["data"]:
            price_str = msg["data"][0].get("p")
            if price_str and self.price_callback:
                self.price_callback(price_str)

    async def start(self, price_callback):
        self.price_callback = price_callback
        self.ws.trade_stream(symbol=self.symbol, callback=self.trade_callback)
        print("WebSocket subscribed, streaming prices...")

        # Keep the loop alive to allow callbacks to execute asynchronously
        while True:
            await asyncio.sleep(0.5)

# Example usage if running streamer.py standalone
if __name__ == "__main__":
    def on_new_price(price):
        print(f"Received new price: {price}")

    async def main():
        streamer = WebSocketStreamer()
        await streamer.start(price_callback=on_new_price)

    asyncio.run(main())
