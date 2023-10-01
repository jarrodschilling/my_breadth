import sqlite3
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from dictionaries import sectors, industries, sub_sectors, indices
from investor_quotes import quotes
import random
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from functions import login_required, portfolio_names, symbol_check, register_errors, login_errors, is_valid_password, create_errors, ma_compute_yf, add_symbols, get_port_name
# flask --app example_app.py --debug run


app = Flask(__name__)

# -------------------------------------------------------------------------------------------------------
# -------------- Setup Session/Cache
# -------------------------------------------------------------------------------------------------------

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# -------------------------------------------------------------------------------------------------------
# -------------- LOGIN PAGE [GET]
# -------------------------------------------------------------------------------------------------------

@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")

# -------------------------------------------------------------------------------------------------------
# -------------- LOGIN USER [POST] --------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------

@app.route("/login", methods=["POST"])
def login_post():

    # Forget any user_id
    session.clear()

    # Get user info from forms
    username = request.form.get("username")
    password = request.form.get("password")

    # Ensure username was submitted
    if not username:
        login_errors("Username not entered")

    # Ensure password was submitted
    if not password:
        login_errors("Password not entered")

    # Query database for username
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    rows = cursor.fetchall()

    # Ensure username exists and password is correct
    if len(rows) != 1 or not check_password_hash(rows[0][2], password):
        return login_errors("Invalid username and/or password")

    # Remember which user has logged in
    session["user_id"] = rows[0][0]
    conn.commit()
    conn.close()

    return redirect('/portfolio')

# -------------------------------------------------------------------------------------------------------
# -------------- Logout User
# -------------------------------------------------------------------------------------------------------

@app.route("/logout")
@login_required
def logout():

    # Forget any user_id
    session.clear()

    # Redirect user to home page
    return redirect("/")


# -------------------------------------------------------------------------------------------------------
# ------ REGISTRATION PAGE [GET]
# -------------------------------------------------------------------------------------------------------

@app.route("/register")
def register():
    return render_template("register.html")

# -------------------------------------------------------------------------------------------------------
# ------ REGISTER USER [POST]
# -------------------------------------------------------------------------------------------------------

@app.route("/register", methods=["POST"])
def signup_post():
    username = request.form.get("username")
    password = request.form.get("password")
    confirm_password = request.form.get("confirmpassword")

    # Check if username already exists in database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users")
    usernames = cursor.fetchall()
    conn.commit()
    conn.close()

    for user in usernames:
        if user[0] == username:
            return register_errors("That username already exists, please choose another one")
       
    # Check that username and password are each between 5 and 25 characters long
    if len(username) < 5:
        return register_errors("Username must be atleast 5 characters long")
    if len(username) > 25:
        return register_errors("Username cannot be more than 25 characters long")
    if len(password) < 5:
        return register_errors("Password must be atleast 5 characters long")
    if len(username) > 25:
        return register_errors("Password cannot be more than 25 characters long") 

    # Check that password has one number and one special character
    password_check = password
    if not is_valid_password(password_check):
        return register_errors("Password must contain at least 1 number, 1 letter, and 1 special character")

    # Check that passwords match
    if password != confirm_password:
        return register_errors("Passwords do not match")

    # All checks complete, hash password
    hash = generate_password_hash(password)

    # INSERT USER INTO users database table
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO users (username, hash) VALUES(?, ?)", (username, hash))
    
    conn.commit()
    conn.close()

    return redirect('/login')

# -------------------------------------------------------------------------------------------------------
# -------------- HOME PAGE
# -------------------------------------------------------------------------------------------------------

@app.route("/", methods=["GET"])
def index():
    random_quote = random.choice(quotes)
    return render_template("index.html", quote=random_quote)

# -------------------------------------------------------------------------------------------------------
# -------------- CORE SECTOR DETAIL PAGE
# -------------------------------------------------------------------------------------------------------

@app.route("/sector-detail", methods=["POST", "GET"])
@login_required
def sector_detail():
    if request.method == "GET":

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM sectors")
        stocks = cursor.fetchall()

        cursor.execute("SELECT * FROM sectors WHERE portfolio_id = 'portfolio1'")
        portfolio1 = cursor.fetchall()
        
        cursor.execute("SELECT * FROM sectors WHERE portfolio_id = 'portfolio2'")
        portfolio2 = cursor.fetchall()
        
        cursor.execute("SELECT * FROM sectors WHERE portfolio_id = 'portfolio3'")
        portfolio3 = cursor.fetchall()
        
        portfolio1_name = portfolio_names(portfolio1)
        portfolio2_name = portfolio_names(portfolio2)
        portfolio3_name = portfolio_names(portfolio3)

        portfolio1_ema20 = ma_compute_yf(stocks, "portfolio1", "ema20")
        portfolio1_sma50 = ma_compute_yf(stocks, "portfolio1", "sma50")
        portfolio1_sma200 = ma_compute_yf(stocks, "portfolio1", "sma200")
        portfolio2_ema20 = ma_compute_yf(stocks, "portfolio2", "ema20")
        portfolio2_sma50 = ma_compute_yf(stocks, "portfolio2", "sma50")
        portfolio2_sma200 = ma_compute_yf(stocks, "portfolio2", "sma200")
        portfolio3_ema20 = ma_compute_yf(stocks, "portfolio3", "ema20")
        portfolio3_sma50 = ma_compute_yf(stocks, "portfolio3", "sma50")
        portfolio3_sma200 = ma_compute_yf(stocks, "portfolio3", "sma200")

        
        conn.commit()
        conn.close()


        return render_template("sector-detail.html", portfolio1_name=portfolio1_name, portfolio1_ema20=portfolio1_ema20, portfolio1_sma50=portfolio1_sma50, portfolio1_sma200=portfolio1_sma200, portfolio2_name=portfolio2_name, portfolio2_ema20=portfolio2_ema20, portfolio2_sma50=portfolio2_sma50, portfolio2_sma200=portfolio2_sma200, portfolio3_name=portfolio3_name, portfolio3_ema20=portfolio3_ema20, portfolio3_sma50=portfolio3_sma50, portfolio3_sma200=portfolio3_sma200)

# -------------------------------------------------------------------------------------------------------
# -------------- CORE INDEX DETAIL PAGE
# -------------------------------------------------------------------------------------------------------

@app.route("/index-detail", methods=["POST", "GET"])
@login_required
def index_detail():
    if request.method == "GET":

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM indices")
        stocks = cursor.fetchall()

        cursor.execute("SELECT * FROM indices WHERE portfolio_id = 'portfolio1'")
        portfolio1 = cursor.fetchall()
        
        cursor.execute("SELECT * FROM indices WHERE portfolio_id = 'portfolio2'")
        portfolio2 = cursor.fetchall()
        
        cursor.execute("SELECT * FROM indices WHERE portfolio_id = 'portfolio3'")
        portfolio3 = cursor.fetchall()
        
        portfolio1_name = portfolio_names(portfolio1)
        portfolio2_name = portfolio_names(portfolio2)
        portfolio3_name = portfolio_names(portfolio3)

        portfolio1_ema20 = ma_compute_yf(stocks, "portfolio1", "ema20")
        portfolio1_sma50 = ma_compute_yf(stocks, "portfolio1", "sma50")
        portfolio1_sma200 = ma_compute_yf(stocks, "portfolio1", "sma200")
        portfolio2_ema20 = ma_compute_yf(stocks, "portfolio2", "ema20")
        portfolio2_sma50 = ma_compute_yf(stocks, "portfolio2", "sma50")
        portfolio2_sma200 = ma_compute_yf(stocks, "portfolio2", "sma200")
        portfolio3_ema20 = ma_compute_yf(stocks, "portfolio3", "ema20")
        portfolio3_sma50 = ma_compute_yf(stocks, "portfolio3", "sma50")
        portfolio3_sma200 = ma_compute_yf(stocks, "portfolio3", "sma200")

        
        conn.commit()
        conn.close()


        return render_template("index-detail.html", portfolio1_name=portfolio1_name, portfolio1_ema20=portfolio1_ema20, portfolio1_sma50=portfolio1_sma50, portfolio1_sma200=portfolio1_sma200, portfolio2_name=portfolio2_name, portfolio2_ema20=portfolio2_ema20, portfolio2_sma50=portfolio2_sma50, portfolio2_sma200=portfolio2_sma200, portfolio3_name=portfolio3_name, portfolio3_ema20=portfolio3_ema20, portfolio3_sma50=portfolio3_sma50, portfolio3_sma200=portfolio3_sma200)


# -------------------------------------------------------------------------------------------------------
# -------------- DETAILED BREADTH PAGE
# -------------------------------------------------------------------------------------------------------

@app.route("/detail", methods=["POST", "GET"])
@login_required
def detail():
    if request.method == "GET":
        name = session.get("user_id")

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM portfolios WHERE users_id = ?", (name,))
        stocks = cursor.fetchall()

        cursor.execute("SELECT * FROM portfolios WHERE portfolio_id = 'portfolio1' AND users_id = ?", (name,))
        portfolio1 = cursor.fetchall()
        
        cursor.execute("SELECT * FROM portfolios WHERE portfolio_id = 'portfolio2' AND users_id = ?", (name,))
        portfolio2 = cursor.fetchall()
        
        cursor.execute("SELECT * FROM portfolios WHERE portfolio_id = 'portfolio3' AND users_id = ?", (name,))
        portfolio3 = cursor.fetchall()
        
        portfolio1_name = portfolio_names(portfolio1)
        portfolio2_name = portfolio_names(portfolio2)
        portfolio3_name = portfolio_names(portfolio3)

        portfolio1_ema20 = ma_compute_yf(stocks, "portfolio1", "ema20")
        portfolio1_sma50 = ma_compute_yf(stocks, "portfolio1", "sma50")
        portfolio1_sma200 = ma_compute_yf(stocks, "portfolio1", "sma200")
        portfolio2_ema20 = ma_compute_yf(stocks, "portfolio2", "ema20")
        portfolio2_sma50 = ma_compute_yf(stocks, "portfolio2", "sma50")
        portfolio2_sma200 = ma_compute_yf(stocks, "portfolio2", "sma200")
        portfolio3_ema20 = ma_compute_yf(stocks, "portfolio3", "ema20")
        portfolio3_sma50 = ma_compute_yf(stocks, "portfolio3", "sma50")
        portfolio3_sma200 = ma_compute_yf(stocks, "portfolio3", "sma200")

        
        conn.commit()
        conn.close()

        return render_template("detail.html", portfolio1_name=portfolio1_name, portfolio1_ema20=portfolio1_ema20, portfolio1_sma50=portfolio1_sma50, portfolio1_sma200=portfolio1_sma200, portfolio2_name=portfolio2_name, portfolio2_ema20=portfolio2_ema20, portfolio2_sma50=portfolio2_sma50, portfolio2_sma200=portfolio2_sma200, portfolio3_name=portfolio3_name, portfolio3_ema20=portfolio3_ema20, portfolio3_sma50=portfolio3_sma50, portfolio3_sma200=portfolio3_sma200)

# -------------------------------------------------------------------------------------------------------
# -------------- CREATE PORTFOLIO PAGE [GET]
# -------------------------------------------------------------------------------------------------------

@app.route("/create-portfolio", methods=["GET"])
@login_required
def create_portfolio_page():
    
    name = session.get("user_id")
    # Check to see if portfolio_id already exists for user
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT portfolio_id FROM portfolios WHERE users_id = ?", (name,))
    rows = cursor.fetchall()

    port1 = ""
    port2 = ""
    port3 = ""

    for row in range(0, len(rows)):
        if rows[row][0] == "portfolio1":
            port1 = True
        if rows[row][0] == "portfolio2":
            port2 = True
        if rows[row][0] == "portfolio3":
            port3 = True

    conn.commit()
    conn.close()

    return render_template("create-portfolio.html", port1=port1, port2=port2, port3=port3)
    
# -------------------------------------------------------------------------------------------------------    
# -------------- CREATE PORTFOLIO [POST] 
# -------------------------------------------------------------------------------------------------------

@app.route("/create-portfolio", methods=["POST"])
@login_required
def create_portfolio():

    # Pull data from user form
    name = session.get("user_id")
    portfolio = request.form.get("portfolio")
    portfolio_id = request.form.get("portfolio_id")
    symbols_list = request.form.getlist("symbols[]")
    error_symbol_list = []

    # Check that symbols are correct using yfinance and if they are add to database
    add_symbols(symbols_list, name, portfolio, portfolio_id, error_symbol_list)
    
    # For any symbols that are incorrect, let the user know what they are
    if len(error_symbol_list) != 0:
        return create_errors(f"Incorrect symbols: {error_symbol_list}. All other symbols added to portfolio {portfolio}")

    return redirect("/portfolio")


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# -------------------------------------------------------------------------------------------------------
# -------------- ADD PORTFOLIO 1 PAGE [GET]
# -------------------------------------------------------------------------------------------------------

@app.route("/add-portfolio/<id>", methods=["GET"])
@login_required
def add_portfolio_page(id):

    name = session.get("user_id")
    portfolio_id = f"portfolio{id}"
    portfolio = get_port_name(name, portfolio_id)

    return render_template("add-portfolio.html", portfolio_id=portfolio_id, portfolio=portfolio)

# -------------------------------------------------------------------------------------------------------
# -------------- ADD TO PORTFOLIO 1 [POST]
# -------------------------------------------------------------------------------------------------------

@app.route("/add-portfolio", methods=["POST"])
@login_required
def add_portfolio():

    # Pull data from user form
    name = session.get("user_id")
    portfolio_id = request.form.get("portfolio_id")
    symbols_list = request.form.getlist("symbols[]")
    error_symbol_list = []
    portfolio = get_port_name(name, portfolio_id)

    # Check that symbols are correct using yfinance and if they are add to database
    add_symbols(symbols_list, name, portfolio, portfolio_id, error_symbol_list)
    
    # For any symbols that are incorrect, let the user know what they are
    if len(error_symbol_list) != 0:
        return create_errors(f"Incorrect symbols: {error_symbol_list}. All other symbols added to portfolio {portfolio}")

    return redirect("/portfolio")

# -------------------------------------------------------------------------------------------------------
# -------------- DELETE FROM PORTFOLIO PAGE [GET]
# -------------------------------------------------------------------------------------------------------

@app.route("/delete-portfolio/<id>", methods=["GET"])
@login_required
def delete_portfolio(id):
    print("checking id out")
    name = session.get("user_id")
    portfolio_id = f"portfolio{id}"
    portfolio = get_port_name(name, portfolio_id)

    # Render current portfolios
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM portfolios WHERE users_id = ?", (name,))
    investments = cursor.fetchall()
    
    cursor.execute("SELECT * FROM portfolios WHERE portfolio_id = 'portfolio1' AND users_id = ?", (name,))
    portfolio1 = cursor.fetchall()

    cursor.execute("SELECT * FROM portfolios WHERE portfolio_id = 'portfolio2' AND users_id = ?", (name,))
    portfolio2 = cursor.fetchall()

    cursor.execute("SELECT * FROM portfolios WHERE portfolio_id = 'portfolio3' AND users_id = ?", (name,))
    portfolio3 = cursor.fetchall()
    
    
    portfolio1_name = portfolio_names(portfolio1)
    portfolio2_name = portfolio_names(portfolio2)
    portfolio3_name = portfolio_names(portfolio3)

    conn.commit()
    conn.close()

    return render_template(f"delete-portfolio{id}.html", portfolio_id=portfolio_id, portfolio=portfolio, investments=investments, portfolio1=portfolio1, portfolio1_name=portfolio1_name, portfolio2=portfolio2, portfolio2_name=portfolio2_name, portfolio3=portfolio3, portfolio3_name=portfolio3_name)

# -------------------------------------------------------------------------------------------------------
# -------------- DELETE FROM PORTFOLIO [POST]
# -------------------------------------------------------------------------------------------------------

@app.route("/delete-portfolio", methods=["POST"])
@login_required
def delete_portfolio_post():

    name = session.get("user_id")
    id = request.form.get("id")
    portfolio_id = f"portfolio{id}"
    symbols = request.form.getlist("symbols[]")

    # Delete symbols in symbol list from database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    for i in range(0, len(symbols)):
        cursor.execute("DELETE FROM portfolios WHERE users_id = ? AND portfolio_id = ? AND symbol = ?", (name, portfolio_id, symbols[i],))

    conn.commit()
    conn.close()

    return redirect("/portfolio")



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


# -------------------------------------------------------------------------------------------------------
# -------------- CURRENT PORTFOLIOS PAGE
# -------------------------------------------------------------------------------------------------------


@app.route("/portfolio", methods=["GET"])
@login_required
def portfolio_page():
    name = session.get("user_id")

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM portfolios WHERE users_id = ?", (name,))
    investments = cursor.fetchall()
    
    cursor.execute("SELECT * FROM portfolios WHERE portfolio_id = 'portfolio1' AND users_id = ?", (name,))
    portfolio1 = cursor.fetchall()
    
    cursor.execute("SELECT * FROM portfolios WHERE portfolio_id = 'portfolio2' AND users_id = ?", (name,))
    portfolio2 = cursor.fetchall()
    
    cursor.execute("SELECT * FROM portfolios WHERE portfolio_id = 'portfolio3' AND users_id = ?", (name,))
    portfolio3 = cursor.fetchall()
    
    
    portfolio1_name = portfolio_names(portfolio1)
    portfolio2_name = portfolio_names(portfolio2)
    portfolio3_name = portfolio_names(portfolio3)

    conn.commit()
    conn.close()

    return render_template("portfolio.html", investments=investments, portfolio1=portfolio1, portfolio2=portfolio2, portfolio3=portfolio3, portfolio1_name=portfolio1_name, portfolio2_name=portfolio2_name, portfolio3_name=portfolio3_name)

# -------------------------------------------------------------------------------------------------------
# -------------- CORE SECTOR SUMMARY PAGE
# -------------------------------------------------------------------------------------------------------

@app.route("/sector-summary", methods=["POST", "GET"])
@login_required
def sector_summary():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM sectors")
    stocks = cursor.fetchall()

    cursor.execute("SELECT * FROM sectors WHERE portfolio_id = 'portfolio1'")
    portfolio1 = cursor.fetchall()
    
    cursor.execute("SELECT * FROM sectors WHERE portfolio_id = 'portfolio2'")
    portfolio2 = cursor.fetchall()
    
    cursor.execute("SELECT * FROM sectors WHERE portfolio_id = 'portfolio3'")
    portfolio3 = cursor.fetchall()
    
    portfolio1_name = portfolio_names(portfolio1)
    portfolio2_name = portfolio_names(portfolio2)
    portfolio3_name = portfolio_names(portfolio3)

    portfolio1_ema20 = ma_compute_yf(stocks, "portfolio1", "ema20")
    portfolio1_sma50 = ma_compute_yf(stocks, "portfolio1", "sma50")
    portfolio1_sma200 = ma_compute_yf(stocks, "portfolio1", "sma200")
    portfolio2_ema20 = ma_compute_yf(stocks, "portfolio2", "ema20")
    portfolio2_sma50 = ma_compute_yf(stocks, "portfolio2", "sma50")
    portfolio2_sma200 = ma_compute_yf(stocks, "portfolio2", "sma200")
    portfolio3_ema20 = ma_compute_yf(stocks, "portfolio3", "ema20")
    portfolio3_sma50 = ma_compute_yf(stocks, "portfolio3", "sma50")
    portfolio3_sma200 = ma_compute_yf(stocks, "portfolio3", "sma200")

    conn.commit()
    conn.close()

    total_ema20_list = portfolio1_ema20 + portfolio2_ema20 + portfolio3_ema20
    total_sma50_list = portfolio1_sma50 + portfolio2_sma50 + portfolio3_sma50
    total_sma200_list = portfolio1_sma200 + portfolio2_sma200 + portfolio3_sma200
    total_length = len(portfolio1) + len(portfolio2) + len(portfolio3)
    

    while True:
        try:
            total_ema20 = len(total_ema20_list) / total_length
            total_ema20 = "{:.2%}".format(total_ema20)

            total_sma50 = len(total_sma50_list) / total_length
            total_sma50 = "{:.2%}".format(total_sma50)

            total_sma200 = len(total_sma200_list) / total_length
            total_sma200 = "{:.2%}".format(total_sma200)
            break
        except ZeroDivisionError:
            total_ema20 = "none"
            total_sma50 = "none"
            total_sma200 = "none" 
            break

    while True:
        try:
            portfolio1_ema20_summary = len(portfolio1_ema20) / len(portfolio1)
            portfolio1_ema20_summary = "{:.2%}".format(portfolio1_ema20_summary)

            portfolio1_sma50_summary = len(portfolio1_sma50) / len(portfolio1)
            portfolio1_sma50_summary = "{:.2%}".format(portfolio1_sma50_summary)

            portfolio1_sma200_summary = len(portfolio1_sma200) / len(portfolio1)
            portfolio1_sma200_summary = "{:.2%}".format(portfolio1_sma200_summary)
            break
        except ZeroDivisionError:
            portfolio1_ema20_summary = "none"
            portfolio1_sma50_summary = "none"
            portfolio1_sma200_summary = "none" 
            break

    while True:
        try:
            portfolio2_ema20_summary = len(portfolio2_ema20) / len(portfolio2)
            portfolio2_ema20_summary = "{:.2%}".format(portfolio2_ema20_summary)

            portfolio2_sma50_summary = len(portfolio2_sma50) / len(portfolio2)
            portfolio2_sma50_summary = "{:.2%}".format(portfolio2_sma50_summary)

            portfolio2_sma200_summary = len(portfolio2_sma200) / len(portfolio2)
            portfolio2_sma200_summary = "{:.2%}".format(portfolio2_sma200_summary)
            break
        except ZeroDivisionError:
            portfolio2_ema20_summary = "none"
            portfolio2_sma50_summary = "none"
            portfolio2_sma200_summary = "none" 
            break
    
    while True:
        try:
            portfolio3_ema20_summary = len(portfolio3_ema20) / len(portfolio3)
            portfolio3_ema20_summary = "{:.2%}".format(portfolio3_ema20_summary)

            portfolio3_sma50_summary = len(portfolio3_sma50) / len(portfolio3)
            portfolio3_sma50_summary = "{:.2%}".format(portfolio3_sma50_summary)

            portfolio3_sma200_summary = len(portfolio3_sma200) / len(portfolio3)
            portfolio3_sma200_summary = "{:.2%}".format(portfolio3_sma200_summary)
            break
        except ZeroDivisionError:
            portfolio3_ema20_summary = "none"
            portfolio3_sma50_summary = "none"
            portfolio3_sma200_summary = "none" 
            break
    

    if request.method == "GET":
        return render_template("sector-summary.html", total_ema20=total_ema20, total_sma50=total_sma50, total_sma200=total_sma200, portfolio1_ema20_summary=portfolio1_ema20_summary, portfolio1_sma50_summary=portfolio1_sma50_summary, portfolio1_sma200_summary=portfolio1_sma200_summary, portfolio2_ema20_summary=portfolio2_ema20_summary, portfolio2_sma50_summary=portfolio2_sma50_summary, portfolio2_sma200_summary=portfolio2_sma200_summary, portfolio3_ema20_summary=portfolio3_ema20_summary, portfolio3_sma50_summary=portfolio3_sma50_summary, portfolio3_sma200_summary=portfolio3_sma200_summary, portfolio1_name=portfolio1_name, portfolio2_name=portfolio2_name, portfolio3_name=portfolio3_name)


# -------------------------------------------------------------------------------------------------------
# -------------- CORE INDEX SUMMARY PAGE
# -------------------------------------------------------------------------------------------------------

@app.route("/index-summary", methods=["POST", "GET"])
@login_required
def index_summary():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM indices")
    stocks = cursor.fetchall()

    cursor.execute("SELECT * FROM indices WHERE portfolio_id = 'portfolio1'")
    portfolio1 = cursor.fetchall()
    
    cursor.execute("SELECT * FROM indices WHERE portfolio_id = 'portfolio2'")
    portfolio2 = cursor.fetchall()
    
    cursor.execute("SELECT * FROM indices WHERE portfolio_id = 'portfolio3'")
    portfolio3 = cursor.fetchall()
    
    portfolio1_name = portfolio_names(portfolio1)
    portfolio2_name = portfolio_names(portfolio2)
    portfolio3_name = portfolio_names(portfolio3)

    portfolio1_ema20 = ma_compute_yf(stocks, "portfolio1", "ema20")
    portfolio1_sma50 = ma_compute_yf(stocks, "portfolio1", "sma50")
    portfolio1_sma200 = ma_compute_yf(stocks, "portfolio1", "sma200")
    portfolio2_ema20 = ma_compute_yf(stocks, "portfolio2", "ema20")
    portfolio2_sma50 = ma_compute_yf(stocks, "portfolio2", "sma50")
    portfolio2_sma200 = ma_compute_yf(stocks, "portfolio2", "sma200")
    portfolio3_ema20 = ma_compute_yf(stocks, "portfolio3", "ema20")
    portfolio3_sma50 = ma_compute_yf(stocks, "portfolio3", "sma50")
    portfolio3_sma200 = ma_compute_yf(stocks, "portfolio3", "sma200")

    conn.commit()
    conn.close()

    total_ema20_list = portfolio1_ema20 + portfolio2_ema20 + portfolio3_ema20
    total_sma50_list = portfolio1_sma50 + portfolio2_sma50 + portfolio3_sma50
    total_sma200_list = portfolio1_sma200 + portfolio2_sma200 + portfolio3_sma200
    total_length = len(portfolio1) + len(portfolio2) + len(portfolio3)
    

    while True:
        try:
            total_ema20 = len(total_ema20_list) / total_length
            total_ema20 = "{:.2%}".format(total_ema20)

            total_sma50 = len(total_sma50_list) / total_length
            total_sma50 = "{:.2%}".format(total_sma50)

            total_sma200 = len(total_sma200_list) / total_length
            total_sma200 = "{:.2%}".format(total_sma200)
            break
        except ZeroDivisionError:
            total_ema20 = "none"
            total_sma50 = "none"
            total_sma200 = "none" 
            break

    while True:
        try:
            portfolio1_ema20_summary = len(portfolio1_ema20) / len(portfolio1)
            portfolio1_ema20_summary = "{:.2%}".format(portfolio1_ema20_summary)

            portfolio1_sma50_summary = len(portfolio1_sma50) / len(portfolio1)
            portfolio1_sma50_summary = "{:.2%}".format(portfolio1_sma50_summary)

            portfolio1_sma200_summary = len(portfolio1_sma200) / len(portfolio1)
            portfolio1_sma200_summary = "{:.2%}".format(portfolio1_sma200_summary)
            break
        except ZeroDivisionError:
            portfolio1_ema20_summary = "none"
            portfolio1_sma50_summary = "none"
            portfolio1_sma200_summary = "none" 
            break

    while True:
        try:
            portfolio2_ema20_summary = len(portfolio2_ema20) / len(portfolio2)
            portfolio2_ema20_summary = "{:.2%}".format(portfolio2_ema20_summary)

            portfolio2_sma50_summary = len(portfolio2_sma50) / len(portfolio2)
            portfolio2_sma50_summary = "{:.2%}".format(portfolio2_sma50_summary)

            portfolio2_sma200_summary = len(portfolio2_sma200) / len(portfolio2)
            portfolio2_sma200_summary = "{:.2%}".format(portfolio2_sma200_summary)
            break
        except ZeroDivisionError:
            portfolio2_ema20_summary = "none"
            portfolio2_sma50_summary = "none"
            portfolio2_sma200_summary = "none" 
            break
    
    while True:
        try:
            portfolio3_ema20_summary = len(portfolio3_ema20) / len(portfolio3)
            portfolio3_ema20_summary = "{:.2%}".format(portfolio3_ema20_summary)

            portfolio3_sma50_summary = len(portfolio3_sma50) / len(portfolio3)
            portfolio3_sma50_summary = "{:.2%}".format(portfolio3_sma50_summary)

            portfolio3_sma200_summary = len(portfolio3_sma200) / len(portfolio3)
            portfolio3_sma200_summary = "{:.2%}".format(portfolio3_sma200_summary)
            break
        except ZeroDivisionError:
            portfolio3_ema20_summary = "none"
            portfolio3_sma50_summary = "none"
            portfolio3_sma200_summary = "none" 
            break
    

    if request.method == "GET":
        return render_template("sector-summary.html", total_ema20=total_ema20, total_sma50=total_sma50, total_sma200=total_sma200, portfolio1_ema20_summary=portfolio1_ema20_summary, portfolio1_sma50_summary=portfolio1_sma50_summary, portfolio1_sma200_summary=portfolio1_sma200_summary, portfolio2_ema20_summary=portfolio2_ema20_summary, portfolio2_sma50_summary=portfolio2_sma50_summary, portfolio2_sma200_summary=portfolio2_sma200_summary, portfolio3_ema20_summary=portfolio3_ema20_summary, portfolio3_sma50_summary=portfolio3_sma50_summary, portfolio3_sma200_summary=portfolio3_sma200_summary, portfolio1_name=portfolio1_name, portfolio2_name=portfolio2_name, portfolio3_name=portfolio3_name)


# -------------------------------------------------------------------------------------------------------
# -------------- BREADTH SUMMARY PAGE
# -------------------------------------------------------------------------------------------------------

@app.route("/summary", methods=["POST", "GET"])
@login_required
def summary():
    name = session.get("user_id")

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM portfolios WHERE users_id = ?", (name,))
    stocks = cursor.fetchall()

    cursor.execute("SELECT * FROM portfolios WHERE portfolio_id = 'portfolio1' AND users_id = ?", (name,))
    portfolio1 = cursor.fetchall()
    
    cursor.execute("SELECT * FROM portfolios WHERE portfolio_id = 'portfolio2' AND users_id = ?", (name,))
    portfolio2 = cursor.fetchall()
    
    cursor.execute("SELECT * FROM portfolios WHERE portfolio_id = 'portfolio3' AND users_id = ?", (name,))
    portfolio3 = cursor.fetchall()
    
    portfolio1_name = portfolio_names(portfolio1)
    portfolio2_name = portfolio_names(portfolio2)
    portfolio3_name = portfolio_names(portfolio3)

    portfolio1_ema20 = ma_compute_yf(stocks, "portfolio1", "ema20")
    portfolio1_sma50 = ma_compute_yf(stocks, "portfolio1", "sma50")
    portfolio1_sma200 = ma_compute_yf(stocks, "portfolio1", "sma200")
    portfolio2_ema20 = ma_compute_yf(stocks, "portfolio2", "ema20")
    portfolio2_sma50 = ma_compute_yf(stocks, "portfolio2", "sma50")
    portfolio2_sma200 = ma_compute_yf(stocks, "portfolio2", "sma200")
    portfolio3_ema20 = ma_compute_yf(stocks, "portfolio3", "ema20")
    portfolio3_sma50 = ma_compute_yf(stocks, "portfolio3", "sma50")
    portfolio3_sma200 = ma_compute_yf(stocks, "portfolio3", "sma200")

    conn.commit()
    conn.close()

    total_ema20_list = portfolio1_ema20 + portfolio2_ema20 + portfolio3_ema20
    total_sma50_list = portfolio1_sma50 + portfolio2_sma50 + portfolio3_sma50
    total_sma200_list = portfolio1_sma200 + portfolio2_sma200 + portfolio3_sma200
    total_length = len(portfolio1) + len(portfolio2) + len(portfolio3)
    

    while True:
        try:
            total_ema20 = len(total_ema20_list) / total_length
            total_ema20 = "{:.2%}".format(total_ema20)

            total_sma50 = len(total_sma50_list) / total_length
            total_sma50 = "{:.2%}".format(total_sma50)

            total_sma200 = len(total_sma200_list) / total_length
            total_sma200 = "{:.2%}".format(total_sma200)
            break
        except ZeroDivisionError:
            total_ema20 = "none"
            total_sma50 = "none"
            total_sma200 = "none" 
            break

    while True:
        try:
            portfolio1_ema20_summary = len(portfolio1_ema20) / len(portfolio1)
            portfolio1_ema20_summary = "{:.2%}".format(portfolio1_ema20_summary)

            portfolio1_sma50_summary = len(portfolio1_sma50) / len(portfolio1)
            portfolio1_sma50_summary = "{:.2%}".format(portfolio1_sma50_summary)

            portfolio1_sma200_summary = len(portfolio1_sma200) / len(portfolio1)
            portfolio1_sma200_summary = "{:.2%}".format(portfolio1_sma200_summary)
            break
        except ZeroDivisionError:
            portfolio1_ema20_summary = "none"
            portfolio1_sma50_summary = "none"
            portfolio1_sma200_summary = "none" 
            break

    while True:
        try:
            portfolio2_ema20_summary = len(portfolio2_ema20) / len(portfolio2)
            portfolio2_ema20_summary = "{:.2%}".format(portfolio2_ema20_summary)

            portfolio2_sma50_summary = len(portfolio2_sma50) / len(portfolio2)
            portfolio2_sma50_summary = "{:.2%}".format(portfolio2_sma50_summary)

            portfolio2_sma200_summary = len(portfolio2_sma200) / len(portfolio2)
            portfolio2_sma200_summary = "{:.2%}".format(portfolio2_sma200_summary)
            break
        except ZeroDivisionError:
            portfolio2_ema20_summary = "none"
            portfolio2_sma50_summary = "none"
            portfolio2_sma200_summary = "none" 
            break
    
    while True:
        try:
            portfolio3_ema20_summary = len(portfolio3_ema20) / len(portfolio3)
            portfolio3_ema20_summary = "{:.2%}".format(portfolio3_ema20_summary)

            portfolio3_sma50_summary = len(portfolio3_sma50) / len(portfolio3)
            portfolio3_sma50_summary = "{:.2%}".format(portfolio3_sma50_summary)

            portfolio3_sma200_summary = len(portfolio3_sma200) / len(portfolio3)
            portfolio3_sma200_summary = "{:.2%}".format(portfolio3_sma200_summary)
            break
        except ZeroDivisionError:
            portfolio3_ema20_summary = "none"
            portfolio3_sma50_summary = "none"
            portfolio3_sma200_summary = "none" 
            break
    

    if request.method == "GET":
        return render_template("summary.html", total_ema20=total_ema20, total_sma50=total_sma50, total_sma200=total_sma200, portfolio1_ema20_summary=portfolio1_ema20_summary, portfolio1_sma50_summary=portfolio1_sma50_summary, portfolio1_sma200_summary=portfolio1_sma200_summary, portfolio2_ema20_summary=portfolio2_ema20_summary, portfolio2_sma50_summary=portfolio2_sma50_summary, portfolio2_sma200_summary=portfolio2_sma200_summary, portfolio3_ema20_summary=portfolio3_ema20_summary, portfolio3_sma50_summary=portfolio3_sma50_summary, portfolio3_sma200_summary=portfolio3_sma200_summary, portfolio1_name=portfolio1_name, portfolio2_name=portfolio2_name, portfolio3_name=portfolio3_name)