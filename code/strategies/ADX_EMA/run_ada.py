import os
import sys
import json
import ta
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utilities.bitget_futures import BitgetFutures


# --- CONFIG ---
params = {
    'symbol': 'ADA/USDT:USDT',
    'timeframe': '15m',
    'margin_mode': 'isolated',  # 'cross'
    'balance_fraction': 1,
    'leverage': 5,
    'average_type': 'EMA',  # 'SMA', 'EMA', 'WMA', 'DCM' 
    'average_period_fast': 9,  # Fast EMA period
    'average_period_slow': 21,  # Slow EMA period
    'adx_period': 14,  # ADX period
    'adx_threshold': 25,  # Minimum ADX value to consider a strong trend
    'stop_loss_pct': 0.4,
    'use_longs': True,  # set to False if you want to use only shorts
    'use_shorts': True,  # set to False if you want to use only longs
}

key_path = 'TradingPerso/secret.json'
key_name = 'envelope'

tracker_file = f"TradingPerso/code/strategies/envelope/tracker_{params['symbol'].replace('/', '-').replace(':', '-')}.json"

# trigger_price_delta = 0.005  # what I use for a 1h timeframe
trigger_price_delta = 0.0015  # what I use for a 15m timeframe

# --- AUTHENTICATION ---
print(f"\n{datetime.now().strftime('%H:%M:%S')}: >>> starting execution for {params['symbol']}")
with open(key_path, "r") as f:
    api_setup = json.load(f)[key_name]
bitget = BitgetFutures(api_setup)


# --- TRACKER FILE ---
if not os.path.exists(tracker_file):
    with open(tracker_file, 'w') as file:
        json.dump({"status": "ok_to_trade", "last_side": None, "stop_loss_ids": []}, file)

def read_tracker_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def update_tracker_file(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file)


# --- CANCEL OPEN ORDERS ---
orders = bitget.fetch_open_orders(params['symbol'])
for order in orders:
    bitget.cancel_order(order['id'], params['symbol'])
trigger_orders = bitget.fetch_open_trigger_orders(params['symbol'])
long_orders_left = 0
short_orders_left = 0
for order in trigger_orders:
    if order['side'] == 'buy' and order['info']['tradeSide'] == 'open':
        long_orders_left += 1
    elif order['side'] == 'sell' and order['info']['tradeSide'] == 'open':
        short_orders_left += 1
    bitget.cancel_trigger_order(order['id'], params['symbol'])
print(f"{datetime.now().strftime('%H:%M:%S')}: orders cancelled, {long_orders_left} longs left, {short_orders_left} shorts left")


# --- FETCH OHLCV DATA, CALCULATE INDICATORS ---
data = bitget.fetch_recent_ohlcv(params['symbol'], params['timeframe'], 100).iloc[:-1]

# Calculate EMA (Exponential Moving Averages)
data['ema_fast'] = ta.trend.ema_indicator(data['close'], window=params['average_period_fast'])
data['ema_slow'] = ta.trend.ema_indicator(data['close'], window=params['average_period_slow'])
data['ema_signal'] = data['ema_fast'] > data['ema_slow']

# Calculate ADX (Average Directional Index)
data['adx'] = ta.trend.adx(data['high'], data['low'], data['close'], window=params['adx_period'])

def calculate_entry_signals(data):
    """Calculate entry signals based on EMA cross and ADX."""
    data['long_signal'] = (data['ema_signal'] == True) & (data['adx'] > params['adx_threshold'])
    data['short_signal'] = (data['ema_signal'] == False) & (data['adx'] > params['adx_threshold'])
    return data

data = calculate_entry_signals(data)

print(f"{datetime.now().strftime('%H:%M:%S')}: ohlcv data fetched and indicators calculated")


# --- PLACE ORDERS BASED ON SIGNALS ---
latest_data = data.iloc[-1]
if params['use_longs'] and latest_data['long_signal']:
    amount = balance / latest_data['close']
    min_amount = bitget.fetch_min_amount_tradable(params['symbol'])
    if amount >= min_amount:
        bitget.place_trigger_limit_order(
            symbol=params['symbol'],
            side='buy',
            amount=amount,
            trigger_price=latest_data['close'],
            price=latest_data['close'],
            print_error=True,
        )
        print(f"{datetime.now().strftime('%H:%M:%S')}: Placed long order at {latest_data['close']}")

if params['use_shorts'] and latest_data['short_signal']:
    amount = balance / latest_data['close']
    min_amount = bitget.fetch_min_amount_tradable(params['symbol'])
    if amount >= min_amount:
        bitget.place_trigger_limit_order(
            symbol=params['symbol'],
            side='sell',
            amount=amount,
            trigger_price=latest_data['close'],
            price=latest_data['close'],
            print_error=True,
        )
        print(f"{datetime.now().strftime('%H:%M:%S')}: Placed short order at {latest_data['close']}")

print(f"{datetime.now().strftime('%H:%M:%S')}: <<< Execution finished")
