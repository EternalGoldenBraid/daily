import os
import datetime

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash


from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set, api_key = pk_9ce0dabaa1d542328c5032c1e76532d1
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # Get user portfolio
    portfolio = db.execute(" SELECT * FROM 'index' WHERE users_id = :users_id",
                            users_id = session["user_id"])

    # Generate a list of prices to pass on to jinja
    prices =[]
    for i in portfolio:
        stock = lookup(i['symbol'])
        prices.append(stock['price'])


    # Number of companies in portolio
    size = len(portfolio)

    return render_template("index.html",
                            portfolio = portfolio,
                            prices = prices,
                            size = size)

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # User reached route via POST
    if request.method=="POST":

        # Check for valid user input
        symbol = request.form.get("symbol").upper()
        quote = lookup(symbol)

        try:
            shares = int(float(request.form.get("shares")))
        except ValueError:
            return apology("ValueError", 400)

        if quote is None:
            return apology("Symbol doesn't exist", 400)
        elif symbol is None:
            return apology("Please fill in the symbol field", 400)
        elif shares < 1:
            return apology("Please use a positive integer for number of shares", 400)

        # Add to portfolio if user affords it, else return error
        else:
            price = float(shares) * quote['price']
            cash = db.execute("SELECT cash FROM users WHERE id = :user_id",
                                user_id = session["user_id"])

            # Ensure affordability
            if cash[0]['cash'] < price:
                return apology("Insufficient funds", 400)
            else:
                # Update users cash
                db.execute("UPDATE users SET cash = cash - :price WHERE id = :user_id",
                            price = price ,user_id = session["user_id"])

                # Update history: transacton is sqlite reserved word EDIT: Find error
                db.execute("INSERT INTO history (date, symbol, name, price, shares, action, users_id) VALUES(datetime('now'), :symbol, :name, :price, :shares, 'Buy', :users_id)",
                          symbol = symbol, name = quote['name'], price = price, shares = shares, users_id = session["user_id"])

                # If buying more of the same already owned stock
                match = db.execute(" SELECT symbol FROM 'index' WHERE symbol = :symbol AND users_id = :users_id",
                                    symbol = symbol, users_id = session["user_id"])
                if len(match) != 0:
                    db.execute("UPDATE 'index' SET shares = shares + :shares WHERE symbol = :symbol AND users_id = :users_id",
                                shares = shares, symbol = symbol, users_id = session["user_id"])

                # Buying a new stock
                else:
                    db.execute("INSERT INTO 'index' (symbol, name, shares, users_id) VALUES (:symbol, :name, :shares, :users_id)",
                                symbol = symbol, name = quote['name'], shares = shares, users_id = session["user_id"])

                return redirect("/")
    # User reached route via GET (ie. redirect or clicking a link)
    else:
        return render_template("buy.html")



@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    return jsonify("TODO")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # Fetch a list of dictionaries containing transaction history
    historydb = db.execute(" SELECT * FROM 'history' WHERE users_id = :users_id", users_id = session['user_id'])

    # Variables to pass on to render_template()
    size = len(historydb)
    users_id = []
    date = []
    symbols = []
    prices = []
    actions = []
    shares = []

    # Populate variables to be passed
    for i in range(size):
        users_id.append(historydb[i]['users_id'])
        date.append(historydb[i]['date'])
        symbols.append(historydb[i]['symbol'])
        prices.append(historydb[i]['price'])
        actions.append(historydb[i]['action'])
        shares.append(historydb[i]['shares'])

    # Pass variables to history.html
    return render_template("history.html",
                            size = size,
                            users_id = users_id,
                            date = date,
                            symbols = symbols,
                            prices = prices,
                            actions = actions,
                            shares = shares)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # User looked up a symbol
    if request.method == "POST":

        # Fetch user input
        symbol = request.form.get("symbol")

        # Ensure input is not empty and that symbol is correct
        quote = lookup(symbol)
        if symbol and quote is not None:

            # Render looked up symbol
            return render_template("quoted.html",
                                name=quote['name'],
                                price=usd(quote['price']),
                                symbol=quote['symbol'])

        # Incorrect input
        else:
            return apology("Invalid symbol", 400)

    # User reached route via GET
    else:
        return render_template("quote.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST
    if request.method == "POST":

        # Store username
        username = request.form.get("username")

        # Store password
        password = request.form.get("password")

        # Retrieve username exists
        usernames = db.execute("SELECT username FROM users WHERE username = :username",
                    username = username)

        # Ensure fields aren't blank and that password confirmation matches password
        password_confirmation = request.form.get("confirmation")
        if not username or not password or not password_confirmation:
            return apology("Username or password missing!", 400)
        elif password != password_confirmation:
            return apology("Passwords don't match!", 400)
        elif usernames:
            return apology("Username already exists!", 400)
        else:
            hash = generate_password_hash(password)
            db.execute(
                        "INSERT INTO users (username, hash) VALUES (:username, :hash)",
                        username = username, hash = hash)
            flash('Registered!')

        # Store user id in session
        session.get("user_id")
        return redirect("/login")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # User arrived via post (eg. form input)
    if request.method == "POST":
        # Check user input
        symbol = request.form.get("symbol").upper()
        shares_sell = request.form.get("shares")
        stock = db.execute(" SELECT * FROM 'index' WHERE symbol = :symbol AND users_id = :users_id",
                            symbol = symbol, users_id = session['user_id'])

        # Check ownership of given symbol
        if len(stock) == 0:
            return apology("You don't own that stock", 400)
        else:
            shares_owned = int(float(stock[0]['shares']))

        # Ensure field is nonempty
        if shares_sell is None or shares_sell == 0:
            return apology("Please insert a numbe or shares to be sold", 400)
        else:
            try:
                shares_sell = int(float(shares_sell))
            except ValueError:
                return apology("Please provide a positive integer for shares")
        if symbol is None:
            return apology("Please insert a symbol", 400)


        # Ensure user owns the stock
        elif len(stock) == 0 :
            return apology("You do not own that stock", 400)

        # Ensure number of shares is a positive integer or that user has enough shares
        elif shares_sell < 0:
            return apology("Please provide a positive integer", 400)
        elif shares_sell > shares_owned:
            return apology("You don't own that many shares", 400)

        # User input is correct
        else:
            symbol.upper()
            stock_live = lookup(symbol)

            # Calculate user revenue from sale
            revenue = shares_sell * stock_live['price']

            # User wants sells are shares owned
            if shares_sell == shares_owned:

                # Delete the corresponding row of shares
                db.execute(" DELETE FROM 'index' WHERE symbol = :symbol AND users_id = :users_id",
                            symbol = symbol, users_id = session['user_id'])

                # Update user funds
                db.execute(" UPDATE users SET cash = cash + :revenue WHERE id = :user_id",
                            revenue = revenue, user_id = session['user_id'] )

                # Update history
                db.execute(" INSERT INTO 'history'(date, symbol, name, price, shares, action, users_id) VALUES(datetime('now'), :symbol, :name, :price, :shares, 'Sell' , :users_id)",
                            symbol = symbol, name = stock_live['name'], price = revenue, shares = shares_sell, users_id = session['user_id'])

            # User sells part of the shares owned
            else:

                # Update amount of shares left
                db.execute(" UPDATE 'index' SET shares = shares - :shares WHERE symbol = :symbol AND users_id = :users_id",
                             shares = shares_sell, symbol = symbol, users_id = session['user_id'])

                # Update user funds
                db.execute(" UPDATE users SET cash = cash + :revenue WHERE id = :user_id",
                            revenue = revenue, user_id = session['user_id'] )

                # Update history
                db.execute(" INSERT INTO 'history'(date, symbol, name, price, shares, action, users_id) VALUES(datetime('now'), :symbol, :name, :price, :shares, 'Sell' , :users_id)",
                            symbol = symbol, name = stock_live['name'], price = revenue, shares = shares_sell, users_id = session['user_id'])

    # User arrived via GET (eg. link or redirect)
    else:
        return render_template("sell.html")

    return redirect("/")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
