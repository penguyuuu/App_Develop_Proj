from flask import Flask, flash, jsonify, render_template, request, redirect, session, url_for, Blueprint, views, send_file
import shelve
import re
import qrcode
from forms import BubbleTeaForm
from io import BytesIO
import os
from flask import abort

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Ensure the directory exists for saving QR codes if needed
os.makedirs('static/qrcodes', exist_ok=True)

def get_orders_db():
    return shelve.open('orders.db', 'c')

@app.route('/Aboutus')
def Aboutus():
    return render_template('Aboutus.html')

@app.route('/orders')
def orders():
    return render_template('orders.html')

@app.route('/')
def home():
    user_email = session.get('email')  # Get the email from the session if the user is logged in
    return render_template('home.html', user_email=user_email)

#orders 

# Orders and Cart Management
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
            'image': image
        }
        order_id = str(len(orders_dict) + 1)
        orders_dict[order_id] = order
        db['Orders'] = orders_dict
        db.close()
        return redirect(url_for('cart'))

    return render_template('newOrders.html', form=form, image=image)

@app.route('/cart')
def cart():
    cart_items = session.get('cart', {})

    # Calculate total price for all items in the cart
    grand_total = sum(order['total_price'] for order in cart_items.values())

    return render_template('cart.html', cart_items=cart_items, grand_total=grand_total)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    form = BubbleTeaForm(request.form)
    image = request.args.get('image', 'default.png')
    quantity = int(request.form.get('quantity', 1))

    if form.validate():
        base_price = 5.00  # Example base price
        total_price = base_price * quantity

        order = {
            'size': form.size.data,
            'sweetness': form.sweetness.data,
            'temperature': form.temperature.data,
            'remarks': form.remarks.data,
            'image': image,
            'quantity': quantity,
            'total_price': total_price
        }

        # Store in session
        if 'cart' not in session:
            session['cart'] = {}

        order_id = str(len(session['cart']) + 1)
        session['cart'][order_id] = order
        session.modified = True

        # Persist the cart to orders.db
        db = shelve.open('orders.db', 'c')
        cart_data = db.get('Cart', {})
        cart_data[order_id] = order
        db['Cart'] = cart_data
        db.close()

    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<order_id>', methods=['POST'])
def remove_from_cart(order_id):
    # Remove from session
    if 'cart' in session and order_id in session['cart']:
        del session['cart'][order_id]
        session.modified = True
        
        # Optionally, remove from orders.db if you want to persist changes
        db = shelve.open('orders.db', 'c')
        orders_dict = db.get('Cart', {})
        if order_id in orders_dict:
            del orders_dict[order_id]
            db['Cart'] = orders_dict
        db.close()
        
    return redirect(url_for('cart'))

@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    # Clear the session cart
    session.pop('cart', None)
    
    # Optionally, clear the saved cart in orders.db
    db = shelve.open('orders.db', 'c')
    if 'Cart' in db:
        del db['Cart']
    db.close()
    
    return redirect(url_for('cart'))

@app.route('/update_cart_item/<order_id>', methods=['POST'])
def update_cart_item(order_id):
    if 'cart' in session and order_id in session['cart']:
        # Update the order details
        order = session['cart'][order_id]
        order['size'] = request.form.get('size')
        order['sweetness'] = request.form.get('sweetness')
        order['temperature'] = request.form.get('temperature')
        order['remarks'] = request.form.get('remarks')
        order['quantity'] = int(request.form.get('quantity'))
        order['total_price'] = 5.00 * order['quantity']  # Update the total price
        
        session.modified = True
        
        db = shelve.open('orders.db', 'c')
        orders_dict = db.get('Cart', {})
        if order_id in orders_dict:
            orders_dict[order_id] = order
            db['Cart'] = orders_dict
        db.close()
        
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
    return shelve.open('faq.db')
@app.route('/faq', methods=['GET', 'POST'])
def faq():
    with get_db() as db:
        faqs = db.get('FAQs', [])
        if request.method == 'POST':
            question = request.form.get('question')
            description = request.form.get('description')  # Optional field

            if question:
                faq_entry = {
                    'question': question,
                    'description': description if description else None,
                    'likes': 0,
                    'comments': []
                }
                faqs.append(faq_entry)
                db['FAQs'] = faqs
                flash('FAQ added successfully!', 'success')
                return redirect(url_for('faq'))
            else:
                flash('Question is required.', 'danger')
        # Pass logged-in email to the template for conditional rendering
        return render_template('faq.html', faqs=faqs, logged_in_email=session.get('email'))

@app.route('/add_comment/<int:faq_id>', methods=['POST'])
def add_comment(faq_id):
    logged_in_user_email = session.get('email')

    if logged_in_user_email != 'staff@gmail.com':
        flash('Only staff members can add comments.', 'danger')
        return redirect(url_for('faq'))

    db = get_db()
    faqs = db.get('FAQs', [])

    if not (0 <= faq_id < len(faqs)):
        db.close()
        abort(404)

    comment = request.form.get('comment')
    user = request.form.get('user', 'Admin')
    is_owner = request.form.get('is_owner') == 'true'

    if comment:
        faqs[faq_id]['comments'].append({'user': user, 'comment': comment, 'is_owner': is_owner})
        db['FAQs'] = faqs
        flash('Comment added successfully!', 'success')

    db.close()
    return redirect(url_for('faq'))


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

@app.route('/edit_faq/<int:faq_id>', methods=['GET', 'POST'])
def edit_faq(faq_id):
    db = get_db()
    faqs = db.get('FAQs', [])
    
    if request.method == 'POST':
        email = request.form.get('email')
        if email == 'staff@gmail.com':
            faqs[faq_id]['question'] = request.form.get('question')
            faqs[faq_id]['description'] = request.form.get('description')  # Allow editing description
            db['FAQs'] = faqs
            db.close()
            flash('FAQ updated successfully!', 'success')
            return redirect(url_for('faq'))
        else:
            db.close()
            flash('Only staff members can edit FAQs.', 'danger')
            return redirect(url_for('faq'))
    
    db.close()
    return render_template('edit_faq.html', faq=faqs[faq_id], faq_id=faq_id)

def ensure_comments_key():
    db = get_db()
    faqs = db.get('FAQs', [])
    updated = False

    for faq in faqs:
        if 'comments' not in faq:
            faq['comments'] = []
            updated = True  # Mark that changes were made
        if 'description' not in faq:
            faq['description'] = None  # Ensure all existing FAQs have a 'description' key
            updated = True

    if updated:
        db['FAQs'] = faqs
        print("All FAQs now have a 'description' and 'comments' key.")
    db.close()


# login abby codes
# Route for the login page

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with shelve.open('user_data.db') as db:
            if email in db:
                user = db[email]
                if user['password'] == password:
                    session['email'] = email
                    flash('Login successful!', 'success')
                    return redirect(url_for('home'))
                else:
                    flash('Incorrect password. Please try again.', 'danger')
                    return render_template('login.html', error="Incorrect password.")
            else:
                flash('Email not found. Please sign up.', 'warning')
                return render_template('login.html', error="Email not found.")
    return render_template('login.html')

# Signup Route
@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with shelve.open('user_data.db') as db:
            if email in db:
                flash('Email already registered. Please log in.', 'warning')
                return render_template('login.html', error="Email already registered.")
            else:
                db[email] = {'name': request.form['name'], 'password': password}
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))

# Profile Route
@app.route('/profile')
def profile():
    if 'email' not in session:
        return redirect(url_for('login'))

    user_email = session['email']
    with shelve.open('user_data.db') as db:
        user_data = db[user_email] if user_email in db else {}

    return render_template('profile.html', user_data={'name': user_data.get('name', ''), 'email': user_email})

# Update Profile Route
@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'email' not in session:
        return redirect(url_for('login'))

    user_email = session['email']
    new_name = request.form['name']
    new_email = request.form['email']
    new_password = request.form['password']

    with shelve.open('user_data.db', writeback=True) as db:
        if user_email in db:
            user_data = db[user_email]
            user_data['name'] = new_name
            user_data['email'] = new_email
            if new_password:
                user_data['password'] = new_password

            if new_email != user_email:
                db[new_email] = user_data
                del db[user_email]
                session['email'] = new_email  # Update session with new email

            flash('Profile updated successfully!', 'success')
        else:
            flash('User not found. Please log in again.', 'danger')

    return redirect(url_for('profile'))

# Delete Account Route
@app.route('/delete_account')
def delete_account():
    if 'email' not in session:
        return redirect(url_for('login'))

    user_email = session['email']
    with shelve.open('user_data.db') as db:
        if user_email in db:
            del db[user_email]
            session.pop('email', None)
            flash('Your account has been deleted.', 'info')

    return redirect(url_for('home'))

# Logout Route
@app.route('/logout')
def logout():
    session.pop('email', None)  # Clear the session
    return redirect(url_for('home'))  # Redirect to home page without flash message




if __name__ == '__main__':
    app.run(debug=True)