import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
import pickle
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer


app = Flask(__name__)
app.secret_key = 'your_secret_key'

DB_NAME = 'ecommerce.db'

# Create the initial database schema and sample data
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Create the products table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL
    )
''')

# Create the users table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        is_admin INTEGER NOT NULL DEFAULT 0
    )
''')

# Create the reviews table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        review_text TEXT NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')


# Commit the changes and close the connection
conn.commit()
conn.close()


@app.route('/')
def index():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return render_template('index.html', products=products)


@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/sentiment_analysis.html', methods=['GET', 'POST'])
def sentiment_analysis():
    if request.method == 'POST':
        text = request.form['text']
        analyzer = SentimentIntensityAnalyzer()
        sentiment = analyzer.polarity_scores(text)
        return render_template('sentiment_analysis.html', result=sentiment)
    else:
        return render_template('sentiment_analysis.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()

        if user:
            flash("Username already exists.", "error")
            conn.close()
            return redirect(url_for('register'))

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()

        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['is_admin'] = user[3]

            flash("Login successful.", "success")
            return redirect(url_for('index'))
            conn.close()

        else:
            flash("Invalid username or password.", "error")
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('index'))


@app.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_details(product_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE id=?", (product_id,))
    product = cursor.fetchone()

    cursor.execute(
        "SELECT users.username, reviews.review_text FROM reviews INNER JOIN users ON reviews.user_id=users.id WHERE reviews.product_id=?", (product_id,))
    reviews = cursor.fetchall()

    conn.close()

    if request.method == 'POST':
        if 'user_id' in session:
            user_id = session['user_id']
            review_text = request.form['review']

            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            cursor.execute("INSERT INTO reviews (product_id, user_id, review_text) VALUES (?, ?, ?)",
                           (product_id, user_id, review_text))
            conn.commit()
            conn.close()

            flash("Review submitted successfully!", "success")

            return redirect(url_for('product_details', product_id=product_id))

        else:
            flash("You must be logged in to submit a review.", "error")
            return redirect(url_for('login'))

    return render_template('product_details.html', product=product, reviews=reviews)


@app.route('/admin')
def admin():
    if 'user_id' in session and session['is_admin'] == 1:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT products.name, users.username, reviews.review_text FROM reviews INNER JOIN products ON reviews.product_id=products.id INNER JOIN users ON reviews.user_id=users.id")
        reviews = cursor.fetchall()
        conn.close()
        return render_template('admin.html', reviews=reviews)
    else:
        flash("You don't have permission to access the admin panel.", "error")
        return redirect(url_for('index'))


@app.route('/admin_products', methods=['GET', 'POST'])
def admin_products():
    if 'user_id' in session and session['is_admin'] == 1:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        if request.method == 'POST':
            # Check if the form is for adding a product
            if request.form.get('action') == 'add_product':
                name = request.form['name']
                price = request.form['price']

                # Add the product to the database
                cursor.execute(
                    "INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
                conn.commit()
                flash("Product added successfully!", "success")

            # Check if the form is for removing a product
            elif request.form.get('action') == 'remove_product':
                product_id = request.form['product_id']

                # Remove the product from the database
                cursor.execute(
                    "DELETE FROM products WHERE id=?", (product_id,))
                conn.commit()
                flash("Product removed successfully!", "success")

        # Fetch all products
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()

        conn.close()

        return render_template('admin_products.html', products=products)
    else:
        flash("You don't have permission to access the admin panel.", "error")
        return redirect(url_for('index'))


# Load the sentiment analysis model from the pickle file
with open('sentiment_model.pkl', 'rb') as f:
    sentiment_model = pickle.load(f)

# Initialize the sentiment intensity analyzer
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()


@app.route('/admin_reviews', methods=['GET', 'POST'])
def admin_reviews():
    if 'user_id' in session and session['is_admin'] == 1:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        if request.method == 'POST':
            # ... existing code ...

            # Analyze the sentiment of the reviews
            if request.form.get('action') == 'analyze_reviews':
                product_id = request.form['product_id']

                # Fetch the reviews for the selected product
                cursor.execute(
                    "SELECT user_id, review_text FROM reviews WHERE product_id=?", (product_id,))
                reviews = cursor.fetchall()

                # Analyze the sentiment of each review
                ratings = []
                for review in reviews:
                    user_id, text = review
                    sentiment_score = sia.polarity_scores(text)['compound']
                    # Map the sentiment score to a rating from 1 to 10
                    rating = int((sentiment_score + 1) * 5)
                    ratings.append(rating)

                # Update the ratings in the reviews table
                for i in range(len(reviews)):
                    cursor.execute("UPDATE reviews SET rating=? WHERE product_id=? AND user_id=?", (
                        ratings[i], product_id, reviews[i][0]))
                conn.commit()
                flash("Reviews analyzed and ratings updated successfully!", "success")

        # Fetch all products with their average ratings
        cursor.execute(
            "SELECT products.id, products.name, products.price, AVG(reviews.rating) FROM products LEFT JOIN reviews ON products.id = reviews.product_id GROUP BY products.id")
        products = cursor.fetchall()

        conn.close()

        return render_template('admin_reviews.html', products=products)
    else:
        # ... existing code ...
        flash("You don't have permission to access the admin panel.", "error")
        return redirect(url_for('index'))


# @app.route('/admin_reviews', methods=['GET', 'POST'])
# def admin_reviews():
#    if 'user_id' in session and session['is_admin'] == 1:
#        conn = sqlite3.connect(DB_NAME)
#        cursor = conn.cursor()
#
#        if request.method == 'POST':
#            # ... existing code ...
#
#            # Analyze the sentiment of the reviews
#            if request.form.get('action') == 'analyze_reviews':
#                product_id = request.form['product_id']
#
#                # Fetch the reviews for the selected product
#                cursor.execute("SELECT user_id, review_text FROM reviews WHERE product_id=?", (product_id,))
#                reviews = cursor.fetchall()
#
#                # Analyze the sentiment of each review
#                ratings = []
#                for review in reviews:
#                    user_id, text = review
#                    sentiment_score = sia.polarity_scores(text)['compound']
#                    rating = int((sentiment_score + 1) * 5)  # Map the sentiment score to a rating from 1 to 10
#                    ratings.append((user_id, rating))
#
#                # Update the ratings in the database
#                for user_id, rating in ratings:
#                    cursor.execute("UPDATE reviews SET rating=? WHERE product_id=? AND user_id=?", (rating, product_id, user_id))
#                conn.commit()
#                flash("Reviews analyzed and ratings updated successfully!", "success")
#
#        # ... existing code ...
#        # Fetch all products
#        cursor.execute("SELECT * FROM products")
#        products = cursor.fetchall()
#
#        conn.close()
#
#        return render_template('admin_reviews.html', products=products,rating=rating)
#    else:
#        # ... existing code ...
#        flash("You don't have permission to access the admin panel.", "error")
#        return redirect(url_for('index'))
#
# @app.route('/analysis')
# def analysis():
#
    # if 'user_id' in session and session['is_admin'] == 1:
    # if 'user' not in session:
        # return redirect('/login')
    # if session['user'] != 'admin':
        # return redirect('/')
#
        # conn = sqlite3.connect('ecommerce.db')
        # cursor = conn.cursor()
        # cursor.execute('SELECT * FROM products')
        # products = cursor.fetchall()
        # ratings = {}
#
        # for product in products:
        # product_id = product[0]
        # cursor.execute(
        # 'SELECT * FROM reviews WHERE product_id=?', (product_id,))
        # reviews = cursor.fetchall()
        # product_ratings = []
#
        # for review in reviews:
        # text = review[2]
        #  Perform sentiment analysis on the review text
        # rating = sentiment_model.predict([text])[0]
        # product_ratings.append(rating)
#
        # if len(product_ratings) > 0:
        # avg_rating = sum(product_ratings) / len(product_ratings)
        # else:
        # avg_rating = 0
#
        # ratings[product_id] = avg_rating
#
        # conn.close()
        # return render_template('analsis.html', products=products, ratings=ratings)
    # else:
        # flash("You don't have permission to access the admin panel.", "error")
        # return redirect(url_for('index'))
#
if __name__ == '__main__':
    app.run(debug=True)
