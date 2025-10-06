from decimal import *

def get_price_scale_and_qty_step(client,category: str, symbol: str):
    resp = client.get_instruments_info(category=category, symbol=symbol)
    instruments = resp.get('result', {}).get('list', [])
    if not instruments:
        raise ValueError("Instrument info not found")
    instrument = instruments[0]
    price_scale = instrument.get('priceScale')
    lot_size_filter = instrument.get('lotSizeFilter', {})
    qty_step = lot_size_filter.get('qtyStep')
    return int(price_scale), Decimal(str(qty_step))

def calculate_order_params(margin, leverage, price, take_profit_threshold, stop_loss_threshold, price_scale, qty_step):
    margin = Decimal(str(margin))
    leverage = Decimal(str(leverage))
    price = Decimal(str(price))
    take_profit_threshold = Decimal(str(take_profit_threshold))
    stop_loss_threshold = Decimal(str(stop_loss_threshold))

    # Calculate order quantity floored to qty_step
    raw_qty = margin * leverage / price
    qty = (raw_qty // qty_step) * qty_step
    qty = qty.quantize(qty_step, rounding=ROUND_DOWN)

    # Calculate stop loss price rounded to price_scale decimals
    stop_loss_price = (Decimal('1') + stop_loss_threshold) * price
    stop_loss_price = stop_loss_price.quantize(Decimal(f'1e-{price_scale}'), rounding=ROUND_HALF_UP)

    # Calculate take profit price rounded to price_scale decimals
    take_profit_price = (Decimal('1') - take_profit_threshold) * price
    take_profit_price = take_profit_price.quantize(Decimal(f'1e-{price_scale}'), rounding=ROUND_HALF_UP)

    return float(qty), float(stop_loss_price), float(take_profit_price)
