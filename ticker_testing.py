import sqlite3
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import time





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
    symbols_upper = [symbol.upper() for symbol in symbols]

    
    # INSERT Stocks into database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Check that symbol and exchange are correct
    error_symbol_list = error_symbol_list
    for i in range(0, len(symbols_upper)):
        # check to make sure symbol is correct for yfinance
        if (symbol_check(symbols_upper[i]) != False):
            stock_name = symbol_check(symbols[i])
            cursor.execute("INSERT INTO finance (symbol, stockname, portfolio, portfolio_id, users_id) VALUES(?, ?, ?, ?, ?)", (symbols_upper[i], stock_name, portfolio, portfolio_id, name))
        else:
            error_symbol_list.append(symbols_upper[i])
    
    conn.commit()
    conn.close()

name = "1"
portfolio = "ports 1"
portfolio_id = "portfolio1"


symbol1 = "AR"
symbol2 = "XAR"
symbol3 = "JPM"

symbol_list = [symbol1, symbol2, symbol3]
error_symbol_list = []

add_symbols(symbol_list, name, portfolio, portfolio_id, error_symbol_list)

print(error_symbol_list)