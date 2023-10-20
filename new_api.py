import yfinance as yf
from datetime import datetime, timedelta
import datetime
import pandas as pd
from dictionaries import industries, sub_sectors

stock_symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
# data = yf.download(stock_symbols, period="2y")
# data = data['Adj Close']

def data_call(stocks):
    data = yf.download(stocks, period="2y")
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
    print(sma50_list)
    print(sma200_list)


ma_compute2(sub_sectors, "today")



# moving_average = data["MSFT"].rolling(window=50).mean()
# moving_average = moving_average.iloc[-1]
# print(moving_average)





# Get current price using API CALL data ------------------------ **THIS NEEDS UPDATING**
def current_price(data, date):

    if date == "yesterday_close":
        closing_price = data.iloc[-2]
    elif date == "today":
        closing_price = data.iloc[-1]

    return closing_price


# Get exponential moving average using API CALL data and user inputed period
def ema(data, ema_period, date):
    
    data[f'EMA_{ema_period}'] = data.ewm(span=ema_period, adjust=False).mean()

    # Get the most recent day's closing 20 EMA
    if date == "yesterday_close":
        most_recent_20_ema = data[f'EMA_{ema_period}'].iloc[-2]
    elif date == "today":
        most_recent_20_ema = data[f'EMA_{ema_period}'].iloc[-1]

    return most_recent_20_ema


# Get simple moving average using API CALL data and user inputed period
def sma(data, sma_period, date):

    data[f'SMA_{sma_period}'] = data.rolling(window=sma_period).mean()

    if date == "yesterday_close":
        most_recent_50_sma = data[f'SMA_{sma_period}'].iloc[-2]
    elif date == "today":
        most_recent_50_sma = data[f'SMA_{sma_period}'].iloc[-1]

    return most_recent_50_sma


# Iterate list of stocks to determine if they are above trending EMAs/SMAs
def ma_compute_yf(stocks, portfolio_id, ma_avg, date):
    portfolio_ma = []
    stock_name = []

    # Extract unique symbols from stocks
    symbols_to_fetch = set(stock[1] for stock in stocks)

    # Batch API call for all symbols
    data = api_historical_data(symbols_to_fetch)

    print(data)

    for stock in stocks:
        symbol = stock[1]
        current = current_price(data[stock], date)
        ema20 = ema(data[stock]['Adj Close'], 20, date)
        sma50 = sma(data[stock], 50, date)
        sma200 = sma(data[stock], 200, date)
        
        if (ma_avg == "ema20") and current > ema20 and ema20 > sma50 and sma50 > sma200:
            portfolio_ma.append(symbol)
        elif (ma_avg == "sma50") and current > sma50 and sma50 > sma200:
            portfolio_ma.append(symbol)
        elif (ma_avg == "sma200") and current > sma200:
            portfolio_ma.append(symbol)
    
    return portfolio_ma



# ma_compute_yf(random, "portfolio1", "ema20", "today")
