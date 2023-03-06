from binance.client import Client

api_key = 'NKs6lNEr3bUZw1G8SAVtPzy90lagSkFacKdH95bSSGaiPP8W6Fvq0J1dxQQI674b'
api_secret = 'jWVArzeey3lh59uKjzxAUqA7nDEngODDrZes1Aisxhtpy5flkCPGEU8asNPNOKqI'

client=Client(api_key,api_secret)

print(client.ping())

info = client.get_all_tickers()

print(info)

import pandas as pd

df=pd.DataFrame(client.get_all_tickers())

df=df.set_index("symbol")

df["price"]=df["price"].astype("float")

df.index=df.index.astype("string")

print(df)

print(df.loc["BTCUSDT"])

import pandas as pd

asset="BTCUSDT"

start="2020.01.01"

end="2020.12.31"

timeframe="1d"

df= pd.DataFrame(client.get_historical_klines(asset, timeframe,start,end))

df=df.iloc[:,:6]

df.columns=["Date","Open","High","Low","Close","Volume"]

df=df.set_index("Date")

df.index=pd.to_datetime(df.index,unit="ms")

df=df.astype("float")

print(df)

import numpy
import talib

close = numpy.random.random(100)
print(close)

moving_average = talib.SMA(close, timperiod=10)
print(moving_average)

rsi = talib.RSI(close)
print(rsi)

import mplfinance as mpl
mpl.plot(df, type='candle')

mpl.plot(df, type='candle', volume=True, mav=7)

from darts.models import ExponentialSmoothing

model = ExponentialSmoothing(df)

model.fit(df)

prediction = model.predict(len(val))