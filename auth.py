from flask import Blueprint

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return '<p>Login</p>'


@auth.route('/sign-up')  
def sign_up():
    return "<p> sign-up</p>"   

import shelve
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a strong secret key

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        with shelve.open('user_data') as db:
            if email in db:
                return render_template('signup.html', message="Email already registered!")
            db[email] = hashed_password
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with shelve.open('user_data') as db:
            if email in db and check_password_hash(db[email], password):
                return f"Welcome back, {email}!"  # Redirect to a welcome page or dashboard
            else:
                return render_template('login.html', message="Invalid email or password.")

    return render_template('login.html')

if __name__ == "main":
    app.run(debug=True)
