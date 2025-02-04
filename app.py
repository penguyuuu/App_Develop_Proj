from flask import Flask, render_template, request, redirect, url_for, session, flash
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
def home():
    return render_template('home.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not validate_email(email):
            flash('Invalid email format.')
            return redirect(url_for('signup'))

        if not validate_password(password):
            flash('Password must be at least 6 characters long.')
            return redirect(url_for('signup'))

        with get_user_db() as db:
            if email in db:
                flash('An account with this email already exists.')
                return redirect(url_for('signup'))

            db[email] = {'password': password}  # store only email and password
            flash("Account has been successfully created!")
            return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']  #only can use email
        password = request.form['password']

        with get_user_db() as db:
            user = db.get(email)  #get user data by email

            #check if user exists and password matches
            if user and user['password'] == password:
                session['email'] = email  #store email in session
                flash('Login successful!')
                return redirect(url_for('manage_account'))
            else:
                flash('Invalid email or password!')
                return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/manage_account', methods=['GET', 'POST'])
def manage_account():
    if 'email' not in session:  #check if the user is logged in
        flash('You need to log in first.')
        return redirect(url_for('login'))

    email = session['email']
    print(f"Current session email: {email}")

    with get_user_db() as db:
        user = db.get(email)  #get user data by email
        print(f"Retrieved user data: {user}")

    if user is None:
        flash('User not found.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_email = request.form['email']
        new_password = request.form['password']

        if not validate_email(new_email):
            flash('Invalid email format.')
            return redirect(url_for('manage_account'))

        if not validate_password(new_password):
            flash('Password must be at least 6 characters long.')
            return redirect(url_for('manage_account'))

        with get_user_db() as db:       #update user data
            del db[email]  #remove old email entry
            db[new_email] = {'password': new_password}  #store new email and password
            session['email'] = new_email  #update session email
            flash('Account updated successfully!')
            return redirect(url_for('manage_account'))

    return render_template('manage_account.html', user=user)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('email', None) 
    session['logout_message'] = 'You have been logged out.'
    return redirect(url_for('logout_page'))  
@app.route('/logout_page')
def logout_page():
    message = session.pop('logout_message', None)  
    return render_template('logout.html', message=message)

@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'email' not in session:
        flash('You need to log in first.')
        return redirect(url_for('login'))

    email = session['email']
    with get_user_db() as db:
        if email in db:
            del db[email]
            flash('Your account has been successfully deleted.')
            session.pop('email', None)
            session.pop('username', None)
        else:
            flash('User  not found.')

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
