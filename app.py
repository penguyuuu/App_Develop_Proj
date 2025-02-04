from flask import Flask, render_template, request, session
import shelve
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'


def get_user_db():
    return shelve.open('user_db', writeback=True)


def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None


def validate_password(password):
    return len(password) >= 6


@app.route('/')
def login_home():
    return render_template('login_home.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    message = None 
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not validate_email(email):
            message = 'Invalid email format.'
            return render_template('signup.html', message=message)

        if not validate_password(password):
            message = 'Password must be at least 6 characters long.'
            return render_template('signup.html', message=message)

        with get_user_db() as db:
            if email in db:
                message = 'An account with this email already exists.'
                return render_template('signup.html', message=message)

            db[email] = {'password': password}  # store only email and password
            message = "Account has been successfully created!"
            return render_template('login.html', message=message)

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None  
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with get_user_db() as db:
            user = db.get(email) 
            if user and user['password'] == password:
                session['email'] = email  
                message = 'Login successful!'
                return render_template('manage_account.html', message=message)
            else:
                message = 'Invalid email or password!'
                return render_template('login.html', message=message)

    return render_template('login.html')


@app.route('/manage_account', methods=['GET', 'POST'])
def manage_account():
    if 'email' not in session:  # check if the user is logged in
        message = 'You need to log in first.'
        return render_template('login.html', message=message)

    email = session['email']

    with get_user_db() as db:
        user = db.get(email)  # get user data by email

    if user is None:
        message = 'User  not found.'
        return render_template('login.html', message=message)

    if request.method == 'POST':
        new_email = request.form['email']
        new_password = request.form['password']

        if not validate_email(new_email):
            message = 'Invalid email format.'
            return render_template('manage_account.html', message=message)

        if not validate_password(new_password):
            message = 'Password must be at least 6 characters long.'
            return render_template('manage_account.html', message=message)

        with get_user_db() as db:  # update user data
            del db[email]  # remove old email entry
            db[new_email] = {'password': new_password}  # store new email and password
            session['email'] = new_email  # update session email
            message = 'Account updated successfully!'
            return render_template('manage_account.html', message=message)

    return render_template('manage_account.html', user=user)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('email', None)
    message = 'You have been logged out.'
    return render_template('logout.html', message=message)


@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'email' not in session:
        message = 'You need to log in first.'
        return render_template('login.html', message=message)

    email = session['email']
    with get_user_db() as db:
        if email in db:
            del db[email]
            message = 'Account successfully deleted.' 
            session.pop('email', None)
        else:
            message = 'User  not found.'

    return render_template('login_home.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)
