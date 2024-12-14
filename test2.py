from binance.client import Client

# Configurez vos clés API Binance
api_key = "YOUR_API_KEY"
api_secret = "YOUR_API_SECRET"

client = Client(api_key, api_secret)

# Récupérer les données historiques
symbol = "ADAUSDT"
interval = Client.KLINE_INTERVAL_1HOUR  # Intervalle 1 heure
klines = client.get_historical_klines(symbol, interval, "1 week ago UTC")

# Convertir les données en DataFrame
import pandas as pd
data = pd.DataFrame(klines, columns=['datetime', 'open', 'high', 'low', 'close', 'volume', 
                                     'close_time', 'quote_asset_volume', 'trades', 
                                     'taker_buy_base', 'taker_buy_quote', 'ignore'])

# Nettoyer les données
data['datetime'] = pd.to_datetime(data['datetime'], unit='ms')
data.set_index('datetime', inplace=True)
data = data[['open', 'high', 'low', 'close', 'volume']].astype(float)

# Sauvegarder en CSV
data.to_csv('ada_historical_data.csv')
