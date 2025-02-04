from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import shelve
import qrcode
from io import BytesIO
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Used for flash messages

# Ensure the directory exists for saving QR codes if needed
os.makedirs('static/qrcodes', exist_ok=True)

# Route for the payment page
@app.route('/', methods=['GET', 'POST'])
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

        return redirect(url_for('payment'))

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
        paynow_data = request.form['paynow_data']  # Details to include in the QR code

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

    return render_template('paynow.html')


if __name__ == '__main__':
    app.run(debug=True)

