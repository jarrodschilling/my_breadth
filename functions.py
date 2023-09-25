from functools import wraps
from flask import session, redirect, render_template
import requests
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import sqlite3

# Global variables for caching data
data_cache = {}

# Call the yfinance API for data needed and cache it
def api_call(symbol):
    if symbol in data_cache:
        return data_cache[symbol]
    
    start_date = "2022-01-01"
    end_date = datetime.today().strftime('%Y-%m-%d')

    # Fetch historical stock data
    data = yf.download(symbol, start=start_date, end=end_date)
    
    # Cache the data for future use
    data_cache[symbol] = data

    return data


# Get current price using API CALL data
def current_price(data):
    data = data
    yesterday_closing_price = data['Close'].iloc[-1]

    return yesterday_closing_price


# Get exponential moving average using API CALL data and user inputed period
def ema(data, ema_period):
    data = data
    ema_period = ema_period
    
    data[f'EMA_{ema_period}'] = data['Close'].ewm(span=ema_period, adjust=False).mean()

    # Get the most recent day's closing 20 EMA
    most_recent_20_ema = data[f'EMA_{ema_period}'].iloc[-1]

    return most_recent_20_ema


# Get simple moving average using API CALL data and user inputed period
def sma(data, sma_period):
    data = data
    sma_period = sma_period
    data[f'SMA_{sma_period}'] = data['Close'].rolling(window=sma_period).mean()

    most_recent_50_sma = data[f'SMA_{sma_period}'].iloc[-1]

    return most_recent_50_sma


# Make batched API CALLS
def batch_api_call(symbols):
    data = {}
    for symbol in symbols:
        data[symbol] = api_call(symbol)
    return data


# Iterate list of stocks to determine if they are above trending EMAs/SMAs
def ma_compute_yf(stocks, portfolio_id, ma_avg):
    portfolio_ma = []
    stock_name = []

    # Extract unique symbols from stocks
    symbols_to_fetch = set(stock[1] for stock in stocks)

    # Batch API call for all symbols
    data = batch_api_call(symbols_to_fetch)

    for stock in stocks:
        symbol = stock[1]
        name = stock[2]
        portfolio = stock[4]
        current = current_price(data[symbol])
        ema20 = ema(data[symbol], 20)
        sma50 = sma(data[symbol], 50)
        sma200 = sma(data[symbol], 200)
        
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


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def portfolio_names(port):
    while True:
        try:
            port_name = port[0][3]
            break
        except IndexError:
            port_name = "none"
            break

    return port_name


# FOR ADD TO PORTFOLIO - Get portfolio name that matches portfolio_id from database
def get_port_name(name, portfolio_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT portfolio FROM portfolios WHERE users_id = ? AND portfolio_id = ?", (name, portfolio_id,))
    rows = cursor.fetchall()
    portfolio = rows[0][0]

    conn.commit()
    conn.close()

    return portfolio


def symbol_check(symbol):
    data = yf.download(symbol)
    if data.empty:
        return False
    else:
        name = yf.Ticker(symbol)
        output = name.info['shortName']
        return output

def add_symbols(symbols_list, name, portfolio, portfolio_id, error_symbol_list):
    # Remove empty symbols from array
    symbols = []
    for i in range(0, len(symbols_list)):
        if symbols_list[i] != "":
            symbols.append(symbols_list[i])
    
    # Make symbols uppercase
    symbols_upper_data = [symbol.upper() for symbol in symbols]

    
    # INSERT Stocks into database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Check that symbol not already in database portfolio
    cursor.execute("SELECT symbol FROM portfolios WHERE users_id = ? AND portfolio_id = ?", (name, portfolio_id))
    data = cursor.fetchall()
    stocks = []
    for x in range(0, len(data)):
        stocks.append(data[x][0])
        
    symbols_upper = []
    for element in symbols_upper_data:
        if element not in stocks:
            symbols_upper.append(element)

    # Check that symbol and exchange are correct
    error_symbol_list = error_symbol_list
    for i in range(0, len(symbols_upper)):
        # check to make sure symbol is correct for yfinance
        stock_name = symbol_check(symbols[i])
        if (stock_name != False):
            cursor.execute("INSERT INTO portfolios (symbol, stockname, portfolio, portfolio_id, users_id) VALUES(?, ?, ?, ?, ?)", (symbols_upper[i], stock_name, portfolio, portfolio_id, name))
        else:
            error_symbol_list.append(symbols_upper[i])
    
    conn.commit()
    conn.close()


def register_errors(problem):
    return render_template('register.html', problem=problem)


def login_errors(problem):
    return render_template('login.html', problem=problem)


def create_errors(problem):
    return render_template('create-error.html', problem=problem)


def is_valid_password(password):
    # Check for at least one digit, one letter, and one special character
    has_digit = any(char.isdigit() for char in password)
    has_letter = any(char.isalpha() for char in password)
    has_special = any(char for char in password if not char.isalnum())

    return has_digit and has_letter and has_special