# Import necessary libraries
import os
import datetime
import random

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, url_for, jsonify, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Setting global variables
UPLOAD_FOLDER = 'static/files'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
DEFAULT_GOAL = 12

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = 'testsecretkey'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///libercache.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    # render the home if the user has logged in, else render the index
    # set a random ineger for popular book
    random_int = random.randint(1, 10)
    # check if "user_id exists in session"
    if "user_id" in session:
        # Fetch user's library
        user_library = db.execute("""
                        SELECT title, author, rating, progress, status, cover_image
                        FROM user_books ub JOIN books b
                        ON ub.book_id = b.id
                        WHERE user_id =? 
                        ORDER BY date_added DESC
                        LIMIT 5;
                        """, session["user_id"])

        # Fetch user's wishlist
        user_wishlist = db.execute("""
                        SELECT title, author
                        FROM wishlist w JOIN books b
                        ON w.book_id = b.id
                        WHERE user_id = ?
                        ORDER BY date_added DESC;
                        """, session["user_id"])
        
        # Get total number of books
        max_value = db.execute("SELECT COUNT(*) AS books_count FROM books;")[0]["books_count"]

        # Generate a list of 5 random book IDs
        random_list = random.sample(range(1, max_value + 1), 5)

        # Convert the list into a tuple so it can be used in the SQL query
        random_tuple = tuple(random_list)

        # Execute the query with the tuple of IDs
        recommended = db.execute(f"SELECT cover_image FROM books WHERE id IN ({','.join(['?' for _ in random_tuple])})", *random_tuple)

        # Get a random book for popular section
        popular = db.execute("""
                        SELECT title, author, cover_image
                        FROM books 
                        WHERE id = ?;
                        """, random_int)[0]
        
        return render_template("home.html", user_library=user_library, user_wishlist=user_wishlist, recommended=recommended, popular=popular)
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    '''signup the user'''
    if request.method == "POST":
        # Ensure all fields are filled
        for i in ["name", "email", "username", "password","password-confirm"]:
            if not request.form.get(i):
                return apology("{} not provided".format(i))
        
        name = request.form.get("name")
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Check if username already exists in database
        checklist = db.execute("SELECT * FROM users WHERE username = ?;", username)
        if len(checklist):
            return apology("username already exists")

        # Check if email is already registered
        check_email = db.execute("SELECT * FROM users WHERE email = ?;", email)
        if len(check_email):
            return apology("Email already registered")
        
        # Check if password and password confirm match
        if not password == request.form.get("password-confirm"):
            return apology("Password does not match confirmation")
        
        # Write details to users database
        # Hash password
        password_hash = generate_password_hash(password)

        try:
            db.execute("INSERT INTO users(name, email, username, hash) VALUES (?, ?, ?, ?);", name, email, username, password_hash)
        except ValueError:
            return apology("username already exists in database", 400)
        
        # Confirm sign-up with simple message
        return render_template("apology.html",status=1)
    
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password")

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

@app.route("/library", methods=["GET", "POST"])
@login_required
def library():
    # Fetch user's library
    user_library = db.execute("""
                            SELECT title, author, published_year, rating, review, progress, date_added, status, cover_image
                            FROM user_books ub JOIN books b
                            ON ub.book_id = b.id
                            WHERE user_id =?
                            ORDER BY date_added DESC;
                            """, session["user_id"])
    
    # Convert status and date for each book
    for book in user_library:
        book["status"] = convert_status(book.get("status"))
        book["date_added"] = sqlite_timestamp_to_date(book.get("date_added"))

    return render_template("library.html", user_library=user_library)

@app.route("/add-book", methods=["POST"])
@login_required
def add_book():
    # Handle submitting a new book
    # Check if title was provided
    title = request.form.get('title')
    if not title:
        return 'Must provide book title'
    
    # check if title already exists in books table
    check = db.execute("SELECT * FROM books WHERE title = ?;", title)
    if len(check):
        return 'Book already exists in database'

    # insert the new book into the database
    db.execute("INSERT INTO books(title) VALUES (?);", title)

    # check if the pubished_year is valid
    try:
        published_year = int(request.form.get('published_year'))
        if published_year > datetime.datetime.now().year or published_year < 1600:
            return 'Invalid Publication Year'
    except ValueError:
        return 'Enter a valid number for Publication year'

    # iteratively update other fields
    for i in ['author', 'genre', 'published_year']:
        if request.form.get(i):
            db.execute("UPDATE books SET {} = ? WHERE title = ?;".format(i), request.form.get(i), title)

    # File upload handling
    # check if file was uploaded
    if 'image' not in request.files:

        # if the image was not added process the rest of the fields
        return 'Book succesfully added'
    
    file = request.files['image']
    
    if file.filename == '':
        return 'No selected file'
    
    # check if the file uploaded is the allowed file type
    if not file or not allowed_file(file.filename):
        return 'Invalid file type'
    
    # Replace spaces with dashes and secure the filename
    custom_name = request.form.get('title', '').strip().replace(' ', '-')
    custom_name = secure_filename(custom_name)

    # Get the file extension from the original filename
    file_ext = os.path.splitext(file.filename)[1]
    
    # Combine the custom name with the original extension
    new_filename = f"{custom_name}{file_ext}"

    cover_image_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
    file.save(cover_image_path)
    db.execute("UPDATE books SET cover_image = ? WHERE title = ?;", cover_image_path, title)

    return 'Book succesfully added'


@app.route("/explore", methods=["GET", "POST"])
@login_required
def explore():
    return render_template("explore.html")

@app.route('/search')
@login_required
def search():
    # Handle book search
    query = request.args.get('q', '')
    if len(query) < 2:
        return render_template('search_results.html', books=[])
    
    # Search for books matching the query
    books = db.execute("SELECT * FROM books WHERE title LIKE ? OR author LIKE ? ORDER BY title LIMIT 15" , f'%{query}%', f'%{query}%')

    if not books:
        return render_template('search_results.html', books=[])
    
    return render_template('search_results.html', books=books)

@app.route("/log-book", methods=["POST"])
@login_required
def log_book():
    # Handle logging a book in user's library
    if not request.method == "POST":
        return 'Invalid Operation'
    
    title = request.form.get('title')
    if not title:
        return 'Please Provide Book title'
    
    # check if the title exists in the user's library
    check = db.execute("""
                       SELECT * FROM user_books
                       WHERE user_id = ?
                       AND book_id IN(SELECT id FROM books WHERE title = ?);
                       """, session["user_id"], title)
    if len(check):
        return 'Book Already Exists in your Library'
    
    # check if a valid reading status was submitted
    status = request.form.get("status")
    if status not in list(STATUS_MAPPING.keys()):
        return "Invalid Reading Status"

    if status == 'currently_reading':
        # check if the pubished_year is valid
        try:
            progress = int(request.form.get('progress'))
            if progress > 99 or progress < 1:
                return 'Enter a value between 0 and 100'
        except ValueError:
            return 'Enter a valid percentage of the book you have read'

    elif status == 'read':
        progress = 100
    else:
        progress = 0

    # Insert the book into user's library
    db.execute("""INSERT INTO user_books(user_id, book_id, status, progress)
               SELECT ?, id, ?, ?
               FROM books WHERE title = ?;
               """,session["user_id"], status, progress, title,)
    
    
    # ensure user provided a valid rating
    if request.form.get('rating'):
        try:
            rating = int(request.form.get('rating'))
            if rating > 10 or rating < 0:
                return 'Rate the book between 0 and 10'
        except ValueError:
            return 'Enter an integer between 0 and 10'

        db.execute("""UPDATE user_books SET rating = ? WHERE user_id = ? and book_id IN (
                   SELECT id FROM books WHERE title = ?);""", rating, session["user_id"], title)

    # update the review if user gave a review
    if request.form.get('review'):
        review = request.form.get('review')
        db.execute("""UPDATE user_books SET review = ? WHERE user_id = ? and book_id IN (
                   SELECT id FROM books WHERE title = ?);""", review, session["user_id"], title)


    return "Book successfully logged in your library"

@app.route("/update-progress", methods=["POST"])
@login_required
def update_progress():
    # Handle updating book progress
    if request.method != "POST":
        return 'Invalid Operation'
    
    # Get form data
    user_id = session["user_id"]
    book_id = db.execute("SELECT id FROM books WHERE title = ?", request.form.get("title"))
    if book_id:
        book_id = book_id[0]["id"]
    else:
        # Handle the case where the book is not found
        return "Book not found"

    # check if the user provided a status and update the status
    if request.form.get('status'):
        status = {v: k for k, v in STATUS_MAPPING.items()}.get(request.form.get('status'))
        if status not in list(STATUS_MAPPING.keys()):
            return "Invalid Reading Status"
        db.execute("UPDATE user_books SET status = ? WHERE user_id = ? and book_id = ?", status, user_id, book_id)

    # check if user provided progress update
    if request.form.get("progress"):
        try:
            progress = int(request.form.get('progress'))
            if progress > 99 or progress < 1:
                return 'Enter a value between 0 and 100'
        except ValueError:
            return 'Enter a valid percentage of the book you read'
        db.execute("UPDATE user_books SET progress = ? WHERE user_id = ? and book_id = ?", progress, user_id, book_id)

    # check if user provided a rating update
    if request.form.get("rating"):
        try:
            rating = int(request.form.get('rating'))
            if rating > 10 or rating < 0:
                return 'Rate the book between 0 and 10'
        except ValueError:
            return 'Enter an integer between 0 and 10'
        db.execute("UPDATE user_books SET rating = ? WHERE user_id = ? and book_id = ?", rating, user_id, book_id)
    
    # update review if user provided a new review
    if request.form.get("review"):
        review = request.form.get('review')
        db.execute("UPDATE user_books SET review = ? WHERE user_id = ? and book_id = ?", review, user_id, book_id)
    
    return 'Book updated succesfully'

@app.route("/remove-book/<string:book_title>", methods=["GET"])
@login_required
def remove_book(book_title):
    user_id = session["user_id"]

    # Delete the book from the user's library
    db.execute("DELETE FROM user_books WHERE user_id = ? AND book_id IN(SELECT id FROM books WHERE title = ?)", user_id, book_title)

    # Redirect the user back to the library page
    return redirect("/library")

@app.route("/remove-item/<string:book_title>", methods=["GET"])
@login_required
def remove_item(book_title):
    # Handle removing a book from user's library
    user_id = session["user_id"]

    # check if title exists in books table
    check = db.execute("SELECT * FROM wishlist WHERE user_id = ? AND book_id IN(SELECT id FROM books WHERE title = ?);", user_id, book_title)
    if not len(check):
        return redirect("/")

    # Delete the book from the user's library
    db.execute("DELETE FROM wishlist WHERE user_id = ? AND book_id IN(SELECT id FROM books WHERE title = ?)", user_id, book_title)

    # Redirect the user back to the library page
    return redirect("/")

@app.route("/add-item/<string:book_title>", methods=["GET"])
@login_required
def add_item(book_title):
    user_id = session["user_id"]

    # check if title already exists in books table
    check = db.execute("SELECT * FROM wishlist WHERE user_id = ? AND book_id IN(SELECT id FROM books WHERE title = ?);", user_id, book_title)
    if len(check):
        return redirect("/explore")
    
    db.execute("""INSERT INTO wishlist(user_id, book_id)
               SELECT ?, id
               FROM books WHERE title = ?;
               """, user_id, book_title)

    # Redirect the user back to the library page
    return redirect("/explore")

@app.route("/stats", methods=["GET", "POST"])
@login_required
def stats():
    # Get the current user's ID from the session
    user_id = session["user_id"]

    # Retrieve the user's library
    user_library = db.execute("""
                        SELECT title, author, rating, genre, progress, date_added, status
                        FROM user_books ub JOIN books b
                        ON ub.book_id = b.id
                        WHERE user_id =?
                        ORDER BY date_added DESC;
                        """, user_id)
    
    # Convert the status of each book to a more readable format
    for book in user_library:
        book["status"] = convert_status(book.get("status"))

    # Count the number of books in the user's library by genre, ordered by the most common genre
    genre_count = db.execute("""
                            SELECT b.genre, COUNT(*) AS book_count
                            FROM user_books ub
                            JOIN books b ON ub.book_id = b.id
                            WHERE ub.user_id = ?
                            GROUP BY b.genre
                            ORDER BY book_count DESC;
                            """, user_id)

    # Count the number of books the user has finished reading
    finished_dict = db.execute("""
                            SELECT COUNT(*) AS f_count
                            FROM user_books ub 
                            JOIN  books b ON ub.book_id = b.id
                            WHERE ub.user_id = ?
                            AND ub.status = 'read'; 
                            """, user_id)
    
    # Get the count of finished books, defaulting to 0 if none are found
    if finished_dict:
        finished = finished_dict[0]["f_count"]
    else:
        finished = 0

    # Count the number of books the user is currently reading
    current_dict = db.execute("""
                            SELECT COUNT(*) AS c_count
                            FROM user_books ub 
                            JOIN  books b ON ub.book_id = b.id
                            WHERE ub.user_id = ?
                            AND ub.status = 'currently_reading'; 
                            """, user_id)
    
    # Get the count of currently reading books, defaulting to 0 if none are found
    if current_dict:
        current = current_dict[0]["c_count"]
    else:
        current = 0   

    # Calculate the current completion percentage (number of books being read multiplied by 100)
    current_completion = current * 100

    # Sum the progress of all books the user is currently reading
    current_progress_dict = db.execute("""
                               SELECT SUM(progress) as total_progress
                               FROM user_books ub JOIN books b
                               ON ub.book_id = b.id
                               WHERE ub.user_id = ?
                               AND ub.status = 'currently_reading';
                               """, user_id)
    
    # Get the total progress for currently reading books, defaulting to 0 if none are found
    current_progress = current_progress_dict[0]["total_progress"] if current_progress_dict[0]["total_progress"] is not None else 0

    # Calculate the progress percentage for currently reading books, handling division by zero
    try:
        progress = current_progress / current_completion
    except ZeroDivisionError:
        progress = 0

     # Calculate the total progress by combining finished books and progress of currently reading books
    total_progress = finished + progress

    # Calculate the progress percentage towards a predefined goal
    progress_percent = round((total_progress / DEFAULT_GOAL) * 100)

    # Count the number of books in the user's wishlist by genre
    wishlist_dict = db.execute("""
                                SELECT b.genre, COUNT(*) AS wl_count
                                FROM wishlist w JOIN books b
                                ON w.book_id = b.id
                                WHERE w.user_id = ?
                                GROUP BY b.genre
                                ORDER BY wl_count DESC;
                                """, user_id)
    
    # Extract genres and counts for wishlist books
    wishlist_genres = [item["genre"] for item in wishlist_dict]
    wishlist_counts = [item["wl_count"] for item in wishlist_dict]

    # Count the number of books in the entire libercache database by genre
    lib_dict = db.execute("""
                            SELECT genre, COUNT(*) AS lib_count
                            FROM books
                            GROUP BY genre
                            ORDER BY lib_count DESC;
                            """)
    
    # Extract genres and counts for the entire library
    lib_genres = [item["genre"] for item in lib_dict]
    lib_counts = [item["lib_count"] for item in lib_dict]

    return render_template("stats.html", 
                           user_library=user_library, 
                           genre_count=genre_count, 
                           finished=finished, 
                           current=current, 
                           progress_percent=progress_percent,
                           wishlist_genres=wishlist_genres,
                           wishlist_counts=wishlist_counts,
                           lib_genres=lib_genres,
                           lib_counts=lib_counts)

# converts sql timestamp to date 
def sqlite_timestamp_to_date(timestamp):
    # uses strftime to format the date returned
    return datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').strftime('%B %d, %Y')  

# converts reading status by using mapping
STATUS_MAPPING = {'not_started':'Not Started', 'currently_reading':'Currently Reading', 'read':'Read'}
def convert_status(s):
    return STATUS_MAPPING.get(s, s)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# you can include this snippet to run 'app.py' as a regular python file
if __name__ == '__main__':
    app.run(debug=True)
