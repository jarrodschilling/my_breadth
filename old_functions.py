def symbol_check(symbol):
    data = yf.download(symbol)
    if data.empty:
        return False
    else:
        return True


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
        if (symbol_check(symbols_upper[i]) == True):
            cursor.execute("INSERT INTO portfolios (symbol, portfolio, portfolio_id, users_id) VALUES(?, ?, ?, ?)", (symbols_upper[i], portfolio, portfolio_id, name))
        else:
            error_symbol_list.append(symbols_upper[i])
    
    conn.commit()
    conn.close()

    # if errors in symbol, let the user know what they are
    return error_symbol_list


def api_call(symbol):
    symbol = symbol
    start_date = "2022-01-01"
    end_date = datetime.today().strftime('%Y-%m-%d')

    # Fetch historical stock data
    data = yf.download(symbol, start=start_date, end=end_date)

    return data