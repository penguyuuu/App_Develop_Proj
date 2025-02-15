from flask import Flask, flash, jsonify, render_template, request, redirect, session, url_for, Blueprint, views, send_file
import shelve
import re
import qrcode
from forms import BubbleTeaForm
from io import BytesIO
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Ensure the directory exists for saving QR codes if needed
os.makedirs('static/qrcodes', exist_ok=True)

# Routes
@app.route('/Aboutus')
def Aboutus():
    return render_template('Aboutus.html')

@app.route('/orders')
def orders():
    return render_template('orders.html')

# Orders Database
def get_orders_db():
    return shelve.open('orders.db')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/newOrders', methods=['GET', 'POST'])
def new_order():
    form = BubbleTeaForm(request.form)
    image = request.args.get('image', 'default.png')  # Get image from URL
    if request.method == 'POST' and form.validate():
        db = shelve.open('orders.db', 'c')
        orders_dict = db.get('Orders', {})
        order = {
            'size': form.size.data,
            'sweetness': form.sweetness.data,
            'temperature': form.temperature.data,
            'remarks': form.remarks.data,
            'image': image  # Save image filename with order
        }
        order_id = str(len(orders_dict) + 1)
        orders_dict[order_id] = order
        db['Orders'] = orders_dict
        db.close()
        return redirect(url_for('all_orders'))

    return render_template('newOrders.html', form=form, image=image)


@app.route('/all_orders')
def all_orders():
    db = get_orders_db()
    orders = db.get('Orders', [])
    db.close()
    return render_template('all_orders.html', orders=orders)

# Cart Routes
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    form = BubbleTeaForm(request.form)
    if form.validate():
        order = {
            'size': form.size.data,
            'sweetness': form.sweetness.data,
            'temperature': form.temperature.data,
            'remarks': form.remarks.data
        }
        if 'cart' not in session:
            session['cart'] = {}
        order_id = str(len(session['cart']) + 1)
        session['cart'][order_id] = order
        session.modified = True
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/remove_from_cart/<order_id>', methods=['POST'])
def remove_from_cart(order_id):
    if 'cart' in session and order_id in session['cart']:
        del session['cart'][order_id]
        session.modified = True
    return redirect(url_for('cart'))

@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('cart'))

#jiaens code

# Route for the payment page
@app.route('/payment', methods=['GET', 'POST']) 
def payment(): 
    if request.method == 'POST': 
        action = request.form['action'] 
        card_number = request.form['card_number'] 
        card_name = request.form['card_name'] 
        expiry_date = request.form['expiry_date'] 
        cvv = request.form['cvv'] 
 
        if action == 'save': 
            # Save card logic 
            with shelve.open('card_data.db') as db: 
                db[card_number] = { 
                    'card_name': card_name, 
                    'expiry_date': expiry_date, 
                    'cvv': cvv 
                } 
            flash('Card details saved successfully!', 'success') 
        elif action == 'pay': 
            with shelve.open('payment_data.db') as payment_db: 
                payment_db[card_number] = { 
                    'card_name': card_name, 
                    'expiry_date': expiry_date, 
                    'cvv': cvv 
                } 
            # Payment logic 
            flash('Payment Successful for card number: {}'.format(card_number), 'success') 
 
 
    return render_template('payment.html') 
 
# Route to view and delete card details 
@app.route('/manage', methods=['GET', 'POST']) 
def manage(): 
    with shelve.open('card_data.db') as db: 
        card_data = dict(db) 
 
    if request.method == 'POST': 
        card_number = request.form['card_number'] 
 
        # Delete card details 
        with shelve.open('card_data.db') as db: 
            if card_number in db: 
                del db[card_number] 
                flash('Card details deleted successfully!', 'success') 
            else: 
                flash('Card number not found!', 'error') 
 
        return redirect(url_for('manage')) 
 
    return render_template('manage.html', card_data=card_data) 
 
# Route for QR code generation 
@app.route('/paynow', methods=['GET', 'POST']) 
def paynow(): 
    if request.method == 'POST': 
        card_number = request.form['card_number']  # Get the card number from the form 
        with shelve.open('card_data.db') as db: 
            card_info = db.get(card_number) 
         
        if card_info: 
            # Prepare data for QR code 
            paynow_data = f"Card Name: {card_info['card_name']}, Expiry: {card_info['expiry_date']}, CVV: {card_info['cvv']}" 
             
            # Generate QR Code 
            qr = qrcode.QRCode( 
                version=1, 
                error_correction=qrcode.constants.ERROR_CORRECT_L, 
                box_size=10, 
                border=4, 
            ) 
            qr.add_data(paynow_data) 
            qr.make(fit=True) 
 
            # Save QR code to memory 
            img = qr.make_image(fill_color="black", back_color="white") 
            buffer = BytesIO() 
            img.save(buffer) 
            buffer.seek(0) 
 
            # Render the QR code directly in the browser 
            return send_file(buffer, mimetype='image/png', as_attachment=False) 
        else: 
            flash('Card number not found!', 'error') 
            return redirect(url_for('paynow')) 
 
    return render_template('paynow.html')

# FAQ lae codes
def get_db():
    return shelve.open('faq.db')  # Use a separate database for FAQs


@app.route('/faq', methods=['GET', 'POST'])
def faq():
    db = get_db()
    faqs = db.get('FAQs', [])
    
    if request.method == 'POST':
        question = request.form.get('question')
        answer = request.form.get('answer')
        
        if question and answer:
            faqs.append({'question': question, 'answer': answer})
            db['FAQs'] = faqs
            db.close()
            flash('FAQ added successfully!', 'success')
            return redirect(url_for('faq'))
    
    db.close()
    return render_template('faq.html', faqs=faqs)

@app.route('/edit_faq/<int:faq_id>', methods=['GET', 'POST'])
def edit_faq(faq_id):
    db = get_db()
    faqs = db.get('FAQs', [])
    
    if request.method == 'POST':
        faqs[faq_id]['question'] = request.form.get('question')
        faqs[faq_id]['answer'] = request.form.get('answer')
        db['FAQs'] = faqs
        db.close()
        flash('FAQ updated successfully!', 'success')
        return redirect(url_for('faq'))
    
    db.close()
    return render_template('edit_faq.html', faq=faqs[faq_id], faq_id=faq_id)

@app.route('/delete_faq/<int:faq_id>', methods=['POST'])
def delete_faq(faq_id):
    db = get_db()
    faqs = db.get('FAQs', [])
    
    if 0 <= faq_id < len(faqs):
        del faqs[faq_id]
        db['FAQs'] = faqs
        flash('FAQ deleted successfully!', 'success')
    
    db.close()
    return redirect(url_for('faq'))

# login abby codes
def get_user_db():
    return shelve.open('user_db', writeback=True)

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

            db[email] = {'password': password}
            message = "Account created successfully!"
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
    if 'email' not in session:
        message = 'You need to log in first.'
        return render_template('login.html', message=message)

    email = session['email']
    with get_user_db() as db:
        user = db.get(email)

    if user is None:
        message = 'User not found.'
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

        with get_user_db() as db:
            del db[email]
            db[new_email] = {'password': new_password}
            session['email'] = new_email
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
            message = 'User not found.'


if __name__ == '__main__':
    app.run(debug=True)

