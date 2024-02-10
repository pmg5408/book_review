import os
import requests
from flask import Flask, session, render_template, request, url_for, flash, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import text
import json

app = Flask(__name__)


# Check for environment variable
#if not os.getenv("postgresql://localhost:5433/pratham"):

#    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgresql://localhost:5433/pratham")
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    return render_template("registration.html")

#@app.route("/registration", methods = ['GET', "POST"])
def registration(username, password, passwordAgain):

    session["username"] = username

    usernameExists = db.execute(text("SELECT username FROM userinfo where username = :un"), {"un": username}).fetchone()

    if session["username"] and not usernameExists:
        if(password != passwordAgain):
            return False  

        db.execute(text("INSERT INTO userinfo (username, passwords) VALUES (:username, :passwords)"),
                        {"username": session["username"], "passwords": password}) 
        db.commit()
    else: 
        return False

    return True

#@app.route("/login", methods = ['GET', 'POST'])
def loginPage(username, password):
    session["username"] = username   
    passwordCheck = db.execute(text("SELECT passwords FROM userinfo WHERE username = :un"),
                                {"un": session["username"]}).fetchone()
    if passwordCheck and password == passwordCheck[0]:
        #error = 'Incorrect Password'
        return True
    return False

@app.route("/logout")
def logout():
    session["username"] = None
    return render_template("registration.html")

@app.route("/login")
def login():
    return render_template("loginPage.html")

@app.route("/search", methods = ['GET', 'POST'])
def searchPage():

    if 'username' in request.form:

        username = request.form.get('username')
        password = request.form.get('password')
        if 'passwordAgain' in request.form:
            if registration(username, password, request.form.get('passwordAgain')):
                return render_template("searchPage.html")
            else:
                return("passwords do not match. Try again!!")
        
        else:
            if loginPage(username, password):
                return render_template("searchPage.html")
            else:
                return render_template("loginPage.html")

    #API_KEY = 'AIzaSyAHSkjIjYwcFTViZ5g5J27ZRWEeXqV2j40'
    bookResultsDict = []

    query = request.form.get('bookInfo')
    url = 'https://www.googleapis.com/books/v1/volumes?'
    res = requests.get(url, params={"q": {query}})
    data = res.json()

    if data != None:

        for i in data["items"]:
            if len(i["volumeInfo"]["industryIdentifiers"]) > 1:
                if i["volumeInfo"]["industryIdentifiers"][0]["type"] == 'ISBN_10':
                    ISBN = i["volumeInfo"]["industryIdentifiers"][0]["identifier"]
                else:
                    ISBN = i["volumeInfo"]["industryIdentifiers"][1]["identifier"]
            else:
                ISBN = i["volumeInfo"]["industryIdentifiers"][0]["identifier"]
            try:
                thumbnail = i["volumeInfo"]["imageLinks"]["smallThumbnail"]
            except KeyError:
                thumbnail = None
            bookResultsDict.append({'title': i["volumeInfo"]["title"], 'authors':i["volumeInfo"]["authors"], 'googleID':i["id"], 'ISBN':ISBN, 'thumbnail':thumbnail})
        
    return render_template("searchPage.html", bookResultsDict=bookResultsDict)

  
#   session["searchRes"] = []
#   results = 
#   for res in results:
#        session["searchRes"].append(res.books)



@app.route("/review/<string:googleID>", methods = ['GET', 'POST'])
def review(googleID):

    url = 'https://www.googleapis.com/books/v1/volumes/' + googleID
    res = requests.get(url)
    data = res.json()

    title = data["volumeInfo"]["title"]
    author = data["volumeInfo"]["authors"]
    year = data["volumeInfo"]["publishedDate"].split('-')[0]

    try:
        thumbnail = data["volumeInfo"]["imageLinks"]["smallThumbnail"]
    except KeyError:
        thumbnail = None    

    try:
        description = data["volumeInfo"]["description"]
    except KeyError:
        description = None
    rating = None
    review_users = None
    review_reviews = None

    if data["volumeInfo"]["industryIdentifiers"][0]["type"] == 'ISBN_10':
        isbn = data["volumeInfo"]["industryIdentifiers"][0]["identifier"]
    else:
        isbn = data["volumeInfo"]["industryIdentifiers"][1]["identifier"]

    if request.method == 'POST':
        if request.form.get('rating') != '':
            rt = float(request.form.get('rating'))
        else:
            rt = None
        rv = request.form.get('review')

        #rv = request.form.get('review')

        book_db = db.execute(text("SELECT * FROM books WHERE (isbn=:isbn)"),
                            {"isbn":isbn}).fetchone()

        if book_db:
            if rv != '':
                dummyDict = {}
                if book_db[6]:
                    dummyDict = book_db[6]
                dummyDict[session["username"]] = rv
                db.execute(text("UPDATE books SET review=:review WHERE isbn=:isbn"),
                            {"review":json.dumps(dummyDict), "isbn":isbn})

            if rt:
                if book_db[5][0]:
                    rt = (rt + (float(book_db[5][0])*float(book_db[5][1])))/(float(book_db[5][1]) + 1)
                    rt = round(rt, 2)
                    db.execute(text("UPDATE books SET rating=:rating WHERE isbn=:isbn"),
                                {"rating":[rt, float(book_db[5][1])+1], "isbn":isbn})
                else:
                    db.execute(text("UPDATE books SET rating=:rating WHERE isbn=:isbn"),
                                {"rating":[rt, 1], "isbn":isbn})

        else:
            print(isbn, title, author, year)
            db.execute(text("INSERT INTO books (isbn, title, author, year, rating, review) VALUES (:isbn, :title, :author, :year, :rating, :review)"),
            {"isbn":isbn, "title":title, "author":author, "year":year, "rating":[rt, 1], "review":{session["username"]:rv}})

        db.commit()


    book_db = db.execute(text("SELECT rating, review FROM books WHERE isbn=(:isbn)"),
                        {"isbn":isbn}).fetchone()
    print(book_db)
    if book_db:
        rating = book_db[0][0]
        if book_db:
            review = book_db[1]
            print(review)

    return render_template("review.html", title=title, isbn=isbn, authors=author, year=year, description=description, googleID=googleID, rating=rating, review=review, thumbnail=thumbnail)

@app.route("/api/bookName/<string:bookName>")
def bookName_api(bookName):
    books = db.execute(text("SELECT * FROM books WHERE title LIKE :title"),{"title": f"%{bookName}%"}).fetchall()
    if not books:
        return jsonify({"error": "A book with the given title does not exist in the database"}), 422
    #book = db.execute(text("SELECT * FROM books WHERE title LIKE :title)"),{"title": bookName}).fetchall()
    APIBooks = []
    for book in books:
        APIBooks.append({"Title": book[2], "ISBN": book[1], "Authors": book[3], "Year": book[4], "RatingsAndNumRatings": book[5], "ReviewsAndUsers": book[6]})

    return jsonify(APIBooks)

@app.route("/api/ISBN/<string:ISBN>")
def ISBN_api(ISBN):
    books = db.execute(text("SELECT * FROM books WHERE isbn LIKE :ISBN"),{"ISBN": f"%{ISBN}%"}).fetchall()
    if not books:
        return jsonify({"error": "A book with the given ISBN does not exist in the database"}), 422
    #book = db.execute(text("SELECT * FROM books WHERE title LIKE :title)"),{"title": bookName}).fetchall()
    APIBooks = []
    for book in books:
        APIBooks.append({"Title": book[2], "ISBN": book[1], "Authors": book[3], "Year": book[4], "RatingsAndNumRatings": book[5], "ReviewsAndUsers": book[6]})

    return jsonify(APIBooks)

@app.route("/api/author/<string:Author>")
def author_api(Author):
    books = db.execute(text("SELECT * FROM books WHERE author LIKE :Author"),{"Author": f"%{Author}%"}).fetchall()
    if not books:
        return jsonify({"error": "A book with the given author does not exist in the database"}), 422
    #book = db.execute(text("SELECT * FROM books WHERE title LIKE :title)"),{"title": bookName}).fetchall()
    APIBooks = []
    for book in books:
        APIBooks.append({"Title": book[2], "ISBN": book[1], "Authors": book[3], "Year": book[4], "RatingsAndNumRatings": book[5], "ReviewsAndUsers": book[6]})

    return jsonify(APIBooks)


app.run(debug=True)

# use the primary key of the boook as the primary key for the reviews so all reviews for a book will have the same primary key and also store the username, rating by each user in the reviews table