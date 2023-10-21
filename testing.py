import sqlite3
from functions import api_call, current_price, symbol_check, create_errors, get_port_name, ma_compute_yf
import yfinance as yf


name = "20"
portfolio = "ports 1"
portfolio_id = "portfolio1"


symbol1 = "JPM"
symbol2 = "XLE"
symbol3 = "WFC"
symbol_list = [symbol1, symbol2, symbol3]

name = yf.Ticker(symbol2)
output = name.info['shortName']
print(output)