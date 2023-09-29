import sqlite3
from functions import api_call, current_price, symbol_check, create_errors, get_port_name, ma_compute_yf
import yfinance as yf


name = "20"
portfolio = "ports 1"
portfolio_id = "portfolio1"


symbol1 = "JPM"
symbol2 = "XLK"
symbol3 = "WFC"
symbol_list = [symbol1, symbol2, symbol3]

name = 20
new_list = []
conn = sqlite3.connect('database.db')
cursor = conn.cursor()



cursor.execute("SELECT * FROM portfolios WHERE users_id = ?", (20,))
stocks = cursor.fetchall()

# cursor.execute("SELECT symbol FROM portfolios WHERE users_id = ? AND portfolio_id = ?", (name, portfolio_id))
# data = cursor.fetchall()
# stocks = []
# for x in range(0, len(data)):
#     stocks.append(data[x][0])

# temp3 = []
# for element in symbol_list:
#     if element not in stocks:
#         temp3.append(element)
            

print(stocks)
# print(temp3)
conn.commit()
conn.close()

