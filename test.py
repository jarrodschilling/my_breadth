import yfinance as yf

# msft = yf.Ticker("MSFT")
# msft.info

def api_historical_data(symbols):
    data = yf.download(symbols, start="2022-01-01", end="2023-10-18")
    return data['Close']

print(api_historical_data("jpm"))