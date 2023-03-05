import os
import requests
from flask import Flask, session, render_template, request, url_for, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import text

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

@app.route("/registration", methods = ['GET', "POST"])
def registration():

    session ["username"] = request.form.get('username')
    password = request.form.get('password')
    passwordAgain = request.form.get('passwordAgain')

    if session["username"] != None:
        if(password != passwordAgain):
            return("passwords do not match. Try again!!")  

        db.execute(text("INSERT INTO userinfo (username, passwords) VALUES (:username, :passwords)"),
                        {"username": session ["username"], "passwords": password}) 
        db.commit()

    return render_template("loginPage.html")

@app.route("/login", methods = ['GET', 'POST'])
def loginPage():
    session["username"] = request.form.get('username')
    password = request.form.get('password')    
    
    passwordCheck = db.execute(text("SELECT passwords FROM userinfo WHERE username = :un"),
                                {"un":session["username"]}).fetchall()

    if password == passwordCheck[0].passwords:
        #error = 'Incorrect Password'
        return render_template("searchPage.html")
    return render_template("loginPage.html")

@app.route("/logout")
def logout():
    session["username"] = None
    return render_template("logout.html")

@app.route("/search", methods = ['GET', 'POST'])
def searchPage():

    #API_KEY = 'AIzaSyAHSkjIjYwcFTViZ5g5J27ZRWEeXqV2j40'

    searchRes = []

    query = request.form.get('bookInfo')
    url = 'https://www.googleapis.com/books/v1/volumes?'
    res = requests.get(url, params={"q": {query}})
    data = res.json()
#        title = data["items"]["volumeInfo"]["title"]
    if data != None:
        for i in data["items"]:
            searchRes.append(i["volumeInfo"]["title"])

#        print("here")
    #print(q, url)
    query = '%' + query + '%'
    print(query)
    #b = db.execute(text("SELECT title FROM books WHERE title = :query"),{"query": query}).fetchall()
    books_db = db.execute(text("SELECT title FROM books WHERE title ILIKE (:query) OR author ILIKE (:query) OR isbn ILIKE (:query)"),
                        {"query": query}).fetchall()

    for book in books_db:
        print("why")
        searchRes.append(book.title)
        
    print("hello")

    return render_template("searchPage.html", searchRes = searchRes)

  
#   session["searchRes"] = []
#   results = 
#   for res in results:
#        session["searchRes"].append(res.books)



@app.route("/review/<string:bookName>", methods = ['GET', 'POST'])
def review(bookName):

    url = 'https://www.googleapis.com/books/v1/volumes?'
    res = requests.get(url, params={"q": {bookName}})
    data = res.json()
    session["id"] = data["items"][0]["id"]
    session["author"] = data["items"][0]["volumeInfo"]["authors"]
    session["year"] = data["items"][0]["volumeInfo"]["publishedDate"]
    session["isbn"] = data["items"][0]["volumeInfo"]["industryIdentifiers"][0]["identifier"]

    if request.method == 'POST':



        rt = request.form.get('rating')
        rv = request.form.get('review')

        a = db.execute(text("SELECT * FROM books WHERE (title = :title)"),
                            {"title": bookName}).fetchone()


        if session["rating"] == 0 and a != None:

            db.execute(text("UPDATE books SET rating = :rating, review = :review, username = :username WHERE title = :bookName"),
                        {"rating": rt, "review": rv, "username": session["username"], "bookName": bookName})
        else:
            print(bookName, session["username"])
            t = db.execute(text("SELECT * FROM books WHERE (title = :title AND username = :un)"),
                                {"title": bookName, "un": session["username"]}).fetchone()
            if t is None:

                db.execute(text("INSERT INTO books (isbn, title, author, year, rating, review, username) VALUES (:isbn, :title, :author, :year, :rating, :review, :username)"),
                        {"isbn":session["isbn"], "title":bookName, "author":session["author"], "year": session["year"], "rating":rt, "review":rv, "username": session["username"]})
        db.commit()

    bookDeets = db.execute(text("SELECT isbn, author, year FROM books WHERE title = :title LIMIT 1"),
                                {"title": bookName}).fetchall()

    rr = db.execute(text("SELECT review, rating FROM books WHERE title = :title"),
                                {"title": bookName}).fetchall()

    

    allReviews = []
    i = 0.0
    rate = 0.0
    if rr != []:
        if rr[0].rating != 0 and rr[0].review !=0:
            for r in rr:
                i = i + 1.0
                if r.rating != None:
                    rate = float(r.rating) + rate
                if r.review != None:
                    allReviews.append(r.review)
                print(r.review)
            session["rating"] = rate/i
        
    else:
        session["rating"] = 0

    if bookDeets != []:
        session["isbn"] = bookDeets[0].isbn
        session ["author"] = bookDeets[0].author
        session ["year"] = bookDeets[0].year
    return render_template("review.html", bookName=bookName, isbn=session["isbn"], author=session["author"], rating=session["rating"], review=allReviews, year=session["year"])

app.run(debug=True)

# use the primary key of the boook as the primary key for the reviews so all reviews for a book will have the same primary key and also store the username, rating by each user in the reviews table