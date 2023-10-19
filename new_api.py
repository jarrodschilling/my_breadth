import yfinance as yf
from datetime import datetime, timedelta
import datetime
import pandas as pd
from dictionaries import industries, sub_sectors


# Testing new API function
def api_historical_data(symbols):
    data = yf.download(symbols, start="2022-01-01", end="2023-10-18")
    return data['Adj Close']


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

    for stock in stocks:
        symbol = stock[1]
        name = stock[2]
        portfolio = stock[4]
        current = current_price(data, date)
        ema20 = ema(data, 20, date)
        sma50 = sma(data, 50, date)
        sma200 = sma(data, 200, date)
        
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

ma_compute_yf(sub_sectors, "portfolio1", "ema20", "today")