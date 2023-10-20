import yfinance as yf
from datetime import datetime, timedelta
import datetime
import pandas as pd
import sqlite3
from dictionaries import industries, sub_sectors


def data_call(stocks):
    data = yf.download(stocks, period="2y")
    # data = yf.download(stocks, start="2020-01-01", end="2022-03-03")
    data = data['Adj Close']
    return data

def current_price(stock_data, date):
    if date == "today":
        return stock_data.iloc[-1]
    elif date == "yesterday":
        return stock_data.iloc[-2]
    

def ema_20_day(stock_data, period, date):
    data = stock_data.ewm(span=period, adjust=False).mean()
    if date == "today":
        return data.iloc[-1]
    elif date == "yesterday":
        return data.iloc[-2]
    
def simple_ma(stock_data, period, date):
    data = stock_data.rolling(window=period).mean()
    if date == "today":
        return data.iloc[-1]
    elif date == "yesterday":
        return data.iloc[-2]

def ma_compute2(stocks, date):
    ema20_list = []
    sma50_list = []
    sma200_list = []
    data = data_call(stocks)
    for stock in stocks:
        stock_data = data[stock]
        price = current_price(stock_data, date)
        ema20 = ema_20_day(stock_data, 20, date)
        sma50 = simple_ma(stock_data, 50, date)
        sma200 = simple_ma(stock_data, 200, date)
        if price > ema20 and ema20 > sma50 and sma50 > sma200:
            ema20_list.append(stock)
            sma50_list.append(stock)
            sma200_list.append(stock)
        elif price > sma50 and sma50 > sma200:
            sma50_list.append(stock)
            sma200_list.append(stock)
        elif price > sma200:
            sma200_list.append(stock)

    return ema20_list, sma50_list, sma200_list

# twenty_day, fifty_day, hundred_day = ma_compute2(sub_sectors, "today")

# -------------------------------------------------------------------------------------------------------
# -------------- OLD
# -------------------------------------------------------------------------------------------------------

def ma_compute_yf(stocks, data, portfolio_id, ma_avg, date):
    portfolio_ma = []
    stock_name = []

    for stock in stocks:
        symbol = stock[1]
        name = stock[2]
        portfolio = stock[4]
        stock_data = data[symbol]
        current = current_price(stock_data, date)
        ema20 = ema_20_day(stock_data, 20, date)
        sma50 = simple_ma(stock_data, 50, date)
        sma200 = simple_ma(stock_data, 200, date)
        
        if portfolio == portfolio_id:
            if (ma_avg == "ema20") and current > ema20 and ema20 > sma50 and sma50 > sma200:
                portfolio_ma.append(symbol)
                stock_name.append(name)
            elif (ma_avg == "sma50") and current > sma50 and sma50 > sma200:
                portfolio_ma.append(symbol)
                stock_name.append(name)
            elif (ma_avg == "sma200") and current > sma200:
                portfolio_ma.append(symbol)
                stock_name.append(name)

    result = []
    for x, y in zip(portfolio_ma, stock_name):
        result.append([x, y])
    
    return result


date = "today"

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM sectors")
stocks = cursor.fetchall()

symbols_to_fetch = set(stock[1] for stock in stocks)
data = data_call(symbols_to_fetch)


portfolio1_ema20 = ma_compute_yf(stocks, data, "portfolio1", "ema20", "today")
portfolio1_sma50 = ma_compute_yf(stocks, data, "portfolio1", "sma50", "today")
portfolio1_sma200 = ma_compute_yf(stocks, data, "portfolio1", "sma200", "today")
portfolio2_ema20 = ma_compute_yf(stocks, data, "portfolio2", "ema20", "today")
portfolio2_sma50 = ma_compute_yf(stocks, data, "portfolio2", "sma50", "today")
portfolio2_sma200 = ma_compute_yf(stocks, data, "portfolio2", "sma200", "today")
portfolio3_ema20 = ma_compute_yf(stocks, data, "portfolio3", "ema20", "today")
portfolio3_sma50 = ma_compute_yf(stocks, data, "portfolio3", "sma50", "today")
portfolio3_sma200 = ma_compute_yf(stocks, data, "portfolio3", "sma200", "today")


conn.commit()
conn.close()

# print(portfolio1_ema20)
print(portfolio1_sma50)
# print(portfolio1_sma200)
# print(portfolio2_ema20)
print(portfolio2_sma50)
# print(portfolio2_sma200)
# print(portfolio3_ema20)
print(portfolio3_sma50)
# print(portfolio3_sma200)