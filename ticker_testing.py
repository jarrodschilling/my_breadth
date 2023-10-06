import sqlite3
import pandas as pd
import numpy as np
import yfinance as yf
from yahooquery import Ticker
import datetime
import pytz
import time



name = "1"
portfolio = "ports 1"
portfolio_id = "portfolio1"


symbol1 = "JPM"
symbol2 = "CSIQ"
symbol3 = "CNCR"

symbol_list = [symbol1, symbol2, symbol3]


symbol="NVDA"
date="today"
today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)
start_date = "2022-01-01"
if date == "yesterday_close":
    end_date = today.strftime('%Y-%m-%d')
elif date == "today":
    end_date = tomorrow.strftime('%Y-%m-%d')

# Fetch historical stock data
data = yf.download(symbol, start=start_date, end=end_date)

print(data)


ema_period = 20

data[f'EMA_{ema_period}'] = data['Close'].ewm(span=ema_period, adjust=False).mean()

# Get the most recent day's closing 20 EMA
most_recent_20_ema = data[f'EMA_{ema_period}'].iloc[-2]

print(most_recent_20_ema)