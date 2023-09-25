import sqlite3
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import time
from yf_test import api_call

start = time.time()
start_cp = time.time()
def current_price(data):
    data = data
    # Get yesterday's closing price
    yesterday_closing_price = data['Close'].iloc[-1]

    return yesterday_closing_price
end_cp = time.time()

start_ema = time.time()
def ema(data, ema_period):
    data = data
    ema_period = ema_period
    
    data[f'EMA_{ema_period}'] = data['Close'].ewm(span=ema_period, adjust=False).mean()

    # Get the most recent day's closing 20 EMA
    most_recent_20_ema = data[f'EMA_{ema_period}'].iloc[-1]

    return most_recent_20_ema
end_ema = time.time()


start_sma = time.time()
def sma(data, sma_period):
    data = data
    sma_period = sma_period
    data[f'SMA_{sma_period}'] = data['Close'].rolling(window=sma_period).mean()

    most_recent_50_sma = data[f'SMA_{sma_period}'].iloc[-1]

    return most_recent_50_sma
end_sma = time.time()

start_ma_comp = time.time()
def ma_compute_yf(stocks, portfolio_id, ma_avg):
    portfolio_ma = []

    for stock in stocks:
        symbol = stock[1]
        portfolio = stock[5]
        data = api_call(symbol)
        current = current_price(data)
        ema20 = ema(data, 20)
        sma50 = sma(data, 50)
        sma200 = sma(data, 200)
        

        if portfolio == portfolio_id:
            if (ma_avg == "ema20") and current > ema20 and ema20 > sma50 and sma50 > sma200:
                portfolio_ma.append(symbol)
            elif (ma_avg == "sma50") and current > sma50 and sma50 > sma200:
                portfolio_ma.append(symbol)
            elif (ma_avg == "sma200") and current > sma200:
                portfolio_ma.append(symbol)

    return portfolio_ma

end_ma_comp = time.time()
name = 18

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM portfolios WHERE users_id = ?", (name,))
stocks = cursor.fetchall()

start_ema20 = time.time()
portfolio1_ema20 = ma_compute_yf(stocks, "portfolio1", "ema20")
end_ema20 = time.time()

start_sma50 = time.time()
portfolio1_sma50 = ma_compute_yf(stocks, "portfolio1", "sma50")
end_sma50 = time.time()

start_sma200 = time.time()
portfolio1_sma200 = ma_compute_yf(stocks, "portfolio1", "sma200")
end_sma200 = time.time()

print(portfolio1_ema20)
print(portfolio1_sma50)
print(portfolio1_sma200)

end = time.time()


total_cp = (end_cp - start_cp) * 10**3
total_ema = (end_ema - start_ema) * 10**3
total_sma = (end_sma - start_sma) * 10**3
total_ma_comp = (end_ma_comp - start_ma_comp) * 10**3
total_ema20 = (end_ema20 - start_ema20) * 10**3
total_sma50 = (end_sma50 - start_sma50) * 10**3
total_sma200 = (end_sma200 - start_sma200) * 10**3
total_time = (end - start) * 10**3

print(f"Total Current Price: {total_cp}")
print(f"Total EMA: {total_ema}")
print(f"Total SMA: {total_sma}")
print(f"Total MA Compute YF: {total_ma_comp}")
print(f"Total EMA20: {total_ema20}")
print(f"Total SMA50: {total_sma50}")
print(f"Total SMA200: {total_sma200}")
print(f"Total Time: {total_time}")