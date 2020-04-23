import os, csv, sys, requests, json

from flask import Flask, session, render_template, request, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.secret_key = 'admin'
# login_manager = flask_login.LoginManager()
# login_manager.init_app(app)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgresql:///books")
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/newuser")
def newuser():
    return render_template("newuser.html")

# @app.route("/confirmnu/", defaults={'username':"hidden"})
@app.route("/confirm", methods=["POST"])
def confirm():
    n_username = str(request.form.get("u_name"))
    n_password = str(request.form.get("p_word"))
    if db.execute("SELECT * FROM users WHERE username = :username", {"username": n_username}).rowcount > 0:
        return render_template("error.html", message="Username already taken.")
    else:
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username": n_username, "password":n_password})
        db.commit()
        return render_template("confirmation.html")

@app.route("/book", methods=['POST','GET'])
def book(): 
    username = request.form.get('username')
    password = request.form.get('password')
    if db.execute("SELECT username FROM users WHERE username = :username", {"username": username}).fetchone() == 0:
        return render_template("error.html", message="No such username.")
    if db.execute("SELECT password FROM users WHERE username = :username", {"username": username}).fetchone()[0] == password:
        session['username'] = username
        return render_template("book.html")
    return render_template("error.html", message="Wrong password.")

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    return render_template('index.html')


@app.route("/results", methods=["POST", "GET"])
def results():
    # Retrieve form info
    searchterm = request.form.get("search_term")
    typeofsearch = request.form.get("type_search")
    if typeofsearch == "author":
        results = db.execute("SELECT * FROM books WHERE author ILIKE :search", {"search":"%"+ searchterm +"%"}).fetchall()
    elif typeofsearch == "title":
        results = db.execute("SELECT * FROM books WHERE title ILIKE :search", {"search":"%"+ searchterm +"%"}).fetchall()
    elif typeofsearch == "isbn":
        results = db.execute("SELECT * FROM books WHERE isbn ILIKE :search", {"search":"%"+ searchterm +"%"}).fetchall()
    if len(results) == 0:
        return render_template("error.html", message = "No results with those search terms.")
    return render_template("results.html", results = results, searchterm=searchterm, typeofsearch=typeofsearch)

@app.route("/results/<string:r_isbn>", methods=["POST", "GET"])
def result(r_isbn):
    r_isbn = r_isbn
    o_isbn= [r_isbn]
    book = db.execute("SELECT * FROM books WHERE isbn = :risbn", {"risbn": r_isbn}).fetchone()
    api_key = '0AdlIaUBdaEdIoMUGaDnQg'
    # api_secret = 'FWRqW6uznpmpoDpk2JoOZIj5c4y5Ym6oNrWYOFC5A'
    response = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key":api_key,"isbns":o_isbn})
    review_count = response.json()['books'][0]["reviews_count"]
    average_rating = response.json()['books'][0]["average_rating"]
    reviews = db.execute("SELECT * FROM reviews WHERE isbn = :risbn", {"risbn": r_isbn}).fetchall()
    return render_template("isbn.html", book=book, review_count=review_count, average_rating=average_rating, reviews=reviews)

@app.route("/result/<string:isbn>/newreview", methods=["POST"])
def newreview(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    u_name = session["username"]
    rating = request.form.get("rating")
    review = request.form.get("review")
    print(book, u_name, rating, review)
    db.execute("INSERT INTO reviews (rating, review, user_id, isbn) VALUES (:rating, :review, :user_id, :isbn)", {"rating": rating, "review": review, "user_id": u_name, "isbn": isbn})
    db.commit()
    api_key = '0AdlIaUBdaEdIoMUGaDnQg'
    response = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key":api_key,"isbns":isbn})
    review_count = response.json()['books'][0]["reviews_count"]
    average_rating = response.json()['books'][0]["average_rating"]
    reviews = db.execute("SELECT * FROM reviews WHERE isbn = :isbn", {"isbn": isbn}).fetchall()
    return render_template("isbn.html", book=book, review_count=review_count, average_rating=average_rating, reviews=reviews)
    




