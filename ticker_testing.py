import sqlite3
import pandas as pd
import numpy as np
import yfinance as yf
from yahooquery import Ticker
from datetime import datetime, timedelta
import pytz
import time



name = "1"
portfolio = "ports 1"
portfolio_id = "portfolio1"


symbol1 = "JPM"
symbol2 = "CSIQ"
symbol3 = "CNCR"

symbol_list = [symbol1, symbol2, symbol3]
# symbol_list = nas_c



def current_price(symbol):
    symbol_j = Ticker(symbol)
    symbol_price = symbol_j.price[symbol]['regularMarketPrice']
    print(symbol_price)
    return symbol_price

def day_high(symbol):
    symbol_j = Ticker(symbol)
    symbol_day_high = symbol_j.price[symbol]['regularMarketDayHigh']
    # print(symbol_day_high)
    return symbol_day_high

def day_low(symbol):
    symbol_j = Ticker(symbol)
    symbol_day_low = symbol_j.price[symbol]['regularMarketDayLow']
    print(symbol_day_low)
    return symbol_day_low

def fifty_two_high(symbol):
    symbol_j = Ticker(symbol)
    symbol_high = symbol_j.summary_detail[symbol]['fiftyTwoWeekHigh']
    # print(symbol_high)
    return symbol_high

def fifty_two_low(symbol):
    symbol_j = Ticker(symbol)
    symbol_low = symbol_j.summary_detail[symbol]['fiftyTwoWeekLow']
    print(symbol_low)
    return symbol_low


def high_low_lists(symbol):
    new_highs_list = 0
    new_lows_list = 0
    for i in range(0, len(symbol)):
        if day_high(symbol[i]) >= fifty_two_high(symbol[i]):
            new_highs_list += 1
        elif day_low(symbol[i]) <= fifty_two_low(symbol[i]):
            new_lows_list += 1
    net_hi_low = new_highs_list - new_lows_list
    print(net_hi_low)

current_price("JPM")
