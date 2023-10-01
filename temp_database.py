import sqlite3
import yfinance as yf
from dictionaries import sub_sectors, indices
# CHANGE: portfolio, portfolio_id, symbols_upper, AND cursor.execute function for DB TABLE!

sectors = ['XLE', 'XLC', 'XLI', 'XLY', 'XLK', 'XLB', 'XLF', 'XLV', 'XLP', 'XLRE', 'XLU']
industries = ['XES', 'KIE', 'XOP', 'KCE', 'XME', 'XPH', 'XHB', 'XTN', 'XWEB', 'XSW', 'XSD', 'XAR', 'XRT', 'XHS', 'KBE', 'XBI', 'XHE', 'XTL', 'KRE']



portfolio = "Indices"
portfolio_id = "portfolio1"
symbols_upper = indices

def symbol_check(symbol):
    data = yf.download(symbol)
    name = yf.Ticker(symbol)
    output = name.info['shortName']
    return output

conn = sqlite3.connect('database.db')
cursor = conn.cursor()



for i in range(0, len(symbols_upper)):
    stock_name = symbol_check(symbols_upper[i])
    cursor.execute("INSERT INTO indices (symbol, stockname, portfolio, portfolio_id) VALUES(?, ?, ?, ?)", (symbols_upper[i], stock_name, portfolio, portfolio_id))

conn.commit()
conn.close()