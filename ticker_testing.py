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

# msft = yf.Ticker("MSFT")

# print(msft.history())
today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)

start_date = "2022-01-01"
end_date = tomorrow.strftime('%Y-%m-%d')

data = yf.download('JPM', start=start_date, end=end_date)
print(data)

# jpm = Ticker('jpm')

# print(jpm.price['jpm']['regularMarketPrice'])