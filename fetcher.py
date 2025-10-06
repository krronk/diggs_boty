from imports import *
from utils import get_price_scale_and_qty_step
from client import http_client
import config

class KlineFetcher:
    def __init__(self, interval="1"):
        self.symbol = config.symbol
        self.category = config.category
        self.interval = interval
        self.client = http_client
        self.ist = pytz.timezone("Asia/Kolkata")

    def get_klines(self):
        now_ist = datetime.datetime.now(self.ist)
        start_time_ist = now_ist - datetime.timedelta(minutes=15)
        end_time_ist = now_ist
        start_time_utc = start_time_ist.astimezone(pytz.utc)
        end_time_utc = end_time_ist.astimezone(pytz.utc)
        start_ts = int(start_time_utc.timestamp() * 1000)
        end_ts = int(end_time_utc.timestamp() * 1000)

        response = self.client.get_kline(category=self.category, symbol=self.symbol, interval=self.interval,
                                         start=start_ts, end=end_ts, limit=200)

        raw = response.get("result", {}).get("list", [])
        highs = pd.Series([Decimal(sublist[2]) for sublist in raw])
        quants = Decimal(str(highs.iloc[-1]))

        price_tick, qty_tick = get_price_scale_and_qty_step(self.client, self.category, self.symbol)
        quantize_str = '0.' + ('0' * (price_tick - 1)) + '1' if price_tick > 0 else '1'
        precise_price = quants.quantize(Decimal(quantize_str), rounding=ROUND_HALF_UP)

        return precise_price


