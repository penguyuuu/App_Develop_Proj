from flask import Flask, render_template, request, redirect, url_for, session, flash # type: ignore
import shelve
import re
from werkzeug.security import generate_password_hash, check_password_hash # type: ignore

app = Flask(__name__)
app.secret_key = 'your_secret_key'


def get_user_db():
    """Open the user database."""
    return shelve.open('user_db', writeback=True)


def validate_email(email):
    """Check if email format is valid."""
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None


def validate_password(password):
    """Ensure password meets length requirement."""
    return len(password) >= 6


@app.route('/')
def home():
    """Render the home page."""
    return render_template('home.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration route."""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not validate_email(email):
            flash('Invalid email format.', 'danger')
            return redirect(url_for('signup'))

        if not validate_password(password):
            flash('Password must be at least 6 characters long.', 'danger')
            return redirect(url_for('signup'))

        with get_user_db() as db:
            if email in db:
                flash('An account with this email already exists.', 'danger')
                return redirect(url_for('signup'))

            hashed_password = generate_password_hash(password)  # Hash the password
            db[email] = {'password': hashed_password}  # Store securely

            flash("Account created successfully! Please log in.", 'success')
            return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with get_user_db() as db:
            user = db.get(email)

            if user and check_password_hash(user['password'], password):  # Verify hashed password
                session['user'] = email
                flash('Login successful!', 'success')
                return redirect(url_for('manage_account'))
            else:
                flash('Invalid email or password.', 'danger')
                return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/manage_account', methods=['GET', 'POST'])
def manage_account():
    """User account management route."""
    if 'user' not in session:
        flash('You need to log in first.', 'warning')
        return redirect(url_for('login'))

    email = session['user']

    with get_user_db() as db:
        user = db.get(email)

        if user is None:
            flash('User not found.', 'danger')
            return redirect(url_for('login'))

        if request.method == 'POST':
            new_email = request.form['email']
            new_password = request.form['password']

            if not validate_email(new_email):
                flash('Invalid email format.', 'danger')
                return redirect(url_for('manage_account'))

            if not validate_password(new_password):
                flash('Password must be at least 6 characters long.', 'danger')
                return redirect(url_for('manage_account'))

            hashed_password = generate_password_hash(new_password)

            # Update user data securely
            del db[email]
            db[new_email] = {'password': hashed_password}
            session['user'] = new_email  # Update session

            flash('Account updated successfully!', 'success')
            return redirect(url_for('manage_account'))

    return render_template('manage_account.html', user=user)


@app.route('/logout')
def logout():
    """User logout route."""
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


@app.route('/delete_account', methods=['POST'])
def delete_account():
    """User account deletion route."""
    if 'user' not in session:
        flash('You need to log in first.', 'warning')
        return redirect(url_for('login'))

    email = session['user']
    with get_user_db() as db:
        if email in db:
            del db[email]
            flash('Your account has been successfully deleted.', 'success')
            session.pop('user', None)
        else:
            flash('User not found.', 'danger')

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
