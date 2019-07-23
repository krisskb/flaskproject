import os
import hashlib

from flask import Flask, session, render_template, request, jsonify, abort
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    if 'username' not in session:
        return render_template("login.html")
    else:
        userdata = dict()
        userdata['username']=session['username']
        #print(userdata)
        return render_template("search.html", userdata=userdata)
    return "Project 1: TODO"


@app.route("/login",methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        if 'username' in session:
            userdata = dict()
            userdata['username'] = session['username']
            return render_template("search.html", userdata=userdata)
        else:
            return render_template("login.html", message="Please login.")
    uname=request.form.get('uname')
    hpwd=hashlib.sha3_512(request.form.get('upwd').encode()).digest()
    dbuser=db.execute("select userid from user_account where userid=:uname and password=:hpwd",
                      {'uname':uname,'hpwd':hpwd})
    if dbuser.fetchone() is None:
        return render_template("login.html", message="Invalid credentials.")
    else:
        userdata=dict()
        session['username']=request.form.get('uname')
        userdata['username'] = session['username']
        return render_template("search.html", userdata=userdata)


@app.route("/register",methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    uname = request.form.get('username')
    hpwd = hashlib.sha3_512(request.form.get('upwd').encode()).digest()
    name = request.form.get('username')
    email = request.form.get('email')
    dbuser = db.execute("select userid from user_account where userid=:uname ",
                        {'uname': uname})
    if dbuser.fetchone():
        return render_template("error.html", message="User already exists.")
    else:
        db.execute("INSERT INTO user_account (userid, password, username, email) values (:userid, :password, :username,:email) ",
                   {'userid': uname, 'password':hpwd, 'username': name, 'email':email})
        db.commit()
        return render_template("login.html", message="User registered. Kindly login")


@app.route("/search/", methods=['GET', 'POST'])
def searchbooks():
    if request.form.get('search') is None:
        return render_template("search.html")
    srchstr={'search': request.form.get('search') + '%' }
    results=db.execute("select * from books where title ilike :search",srchstr).fetchall()
    search_found=False
    if results:
        search_found=True
    else:
        results = db.execute("select * from books where isbn ilike :search", srchstr).fetchall()
    if results:
        search_found = True
    else:
        results = db.execute("select * from books where author ilike :search", srchstr).fetchall()
    if results:
        search_found=True
    return render_template("search.html",search_found=search_found,books=results)


@app.route("/book/<isbn>",methods=['GET','POST'])
def getbook(isbn):
    if request.method=='POST':
        revtext=request.form.get('review')
        rating=int(request.form.get('rating'))
        userid=session['username']
        db.execute("insert into user_reviews (userid, isbn, stars, review_comment) values(:userid,:isbn,:stars,:review_comment)",
                   {'userid':userid, 'isbn':isbn, 'stars':rating, 'review_comment':revtext})
        db.commit()
    bookdata = db.execute("select * from books where isbn = :isbn", {'isbn':isbn}).fetchone()
    userid = session['username']
    user_review = db.execute("select * from USER_REVIEWS where userid = :userid and isbn = :isbn",
               {'userid': userid, 'isbn':  isbn}).fetchone()
    other_review = db.execute("select * from USER_REVIEWS where userid <> :userid and isbn = :isbn",
                             {'userid': userid, 'isbn': isbn}).fetchall()
    key="5ToTGbAzfw2wTd5GIFAg"
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key":key, "isbns": bookdata.isbn} )
    average_rating=res.json()['books'][0]['average_rating']
    review_count=res.json()['books'][0]['work_ratings_count']
    return render_template("book.html", bookdata=bookdata, average_rating=average_rating,
                           review_count=review_count, user_review=user_review, other_review=other_review)


@app.route("/api/<string:isbn>", methods=['GET'])
def api(isbn):
    print('here')
    bookdata = db.execute("select * from books where isbn = :isbn", {'isbn': isbn}).fetchone()
    if not bookdata:
        abort(404)
    key = "5ToTGbAzfw2wTd5GIFAg"
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": key, "isbns": bookdata.isbn})
    print(bookdata)
    average_rating = res.json()['books'][0]['average_rating']
    review_count = res.json()['books'][0]['work_ratings_count']
    result={ "title": bookdata.title,
             "author": bookdata.author,
             "year": bookdata.year_publish,
             "isbn": bookdata.isbn,
             "review_count": review_count,
             "average_score": average_rating}
    return jsonify(result)

@app.route("/logout")
def logout():
    if 'username' in session:
        message=session['username'] + ' user logged out'
        session.pop('username')
    else:
        message='Kindly login before logout'
    return render_template("login.html", message=message)