# import config
# from fetcher import *
# from imports import *
from streamer import *


def on_new_price(price):
    print(f"Received new price: {price}")
async def main():
    streamer = WebSocketStreamer()
    await streamer.start(price_callback=on_new_price)

if __name__ == "__main__":
    asyncio.run(main())








# print(client.get_instruments_info(category="linear",symbol="SOLUSDT", ))








# gh = KlineFetcher( config.symbol,config.category)
# print(gh.get_klines())
# async def fetch_forever():
#     fetcher = KlineFetcher()
#     while True:
#         highs = fetcher.get_klines()  # sync call, blocks briefly
#         print(highs)
#         print("-" * 40)
#         await asyncio.sleep(10)  # async non-blocking wait for 60 seconds
#
# if __name__ == "__main__":
#     asyncio.run(fetch_forever())
