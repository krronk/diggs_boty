from imports import *

with open('config.json', 'r') as f:
    data = json.load(f)

symbol = data.get('symbol')
category = data.get('category')

margin = data.get('margin')
leverage = data.get('leverage')

take_profit_threshold = data.get('take_profit_threshold')
stop_loss_threshold = data.get('stop_loss_threshold')

testnet = data.get('testnet')
