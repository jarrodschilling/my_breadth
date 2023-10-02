from yahooquery import Ticker
from nasdaq import nasdaq
from nyse import clean_nyse
import concurrent.futures
import time

start = time.time()

def check_equity(symbol):
    try:
        ticker = Ticker(symbol)
        quote_type = ticker.price[symbol]["quoteType"]
        return quote_type == "EQUITY"
    except Exception as e:
        print(f"Error for {symbol}: {str(e)}")
        return False
    
symbols = clean_nyse

with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        results = list(executor.map(check_equity, symbols))

for symbol, result in zip(symbols, results):
    if not result:
        print(f"{symbol}: False")
    #else:
        #print(f"{symbol}: False")


end = time.time()
print(end - start)