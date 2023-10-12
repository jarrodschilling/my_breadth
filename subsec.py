# import yfinance, run .ticker and print ticker symbol and name for all sub-sectors in terminal, then can copy to FAQ

import yfinance as yf
from dictionaries import sub_sectors, sectors, indices

indices.sort()

msft = "MSFT"

for symbol in indices:
    data = yf.download(symbol)
    name = yf.Ticker(symbol)
    output = name.info['longName']
    print(output)
