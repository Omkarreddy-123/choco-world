from flask import Flask, request, render_template, redirect
import mysql.connector
from datetime import datetime
from flask import jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/business_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

users_db = {}
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = 'omkarreddygade@gmail.com'
EMAIL_PASSWORD = 'Omkar123reddy@'
# MySQL Database connection setup
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",  # Your MySQL server host
        user="root",       # Your MySQL username
        password="root",   # Your MySQL password
        database="business_db"  # The database you created
    )

# Home route
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/business')
def business():
    return render_template('business.html')

# Add routes for other pages
@app.route('/shop')
def shop():
    return render_template('Shop.html')

@app.route('/brand')
def brand():
    return render_template('brand.html')

@app.route('/news')
def news():
    return render_template('News.html')

@app.route('/active')
def active():
    return render_template('active.html')

# Cart route (only one route for /cart)
@app.route('/cart')
def cart():
    return render_template('cart.html')

# Submit form route
@app.route('/submit', methods=['POST'])
def submit_form():
    # Get form data
    company_name = request.form['company_name']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    vat_number = request.form['vat_number']
    email = request.form['email']
    onboard_code = request.form['onboard_code']
    invoice_email = request.form['invoice_email']
    country = request.form['country']
    street = request.form['street']
    additional_address = request.form['additional_address']
    postal_code = request.form['postal_code']
    city = request.form['city']
    phone = request.form['phone']
    same_address = 'same_address' in request.form
    consent = 'consent' in request.form
    subscribe = 'subscribe' in request.form

    # Insert data into MySQL
    connection = get_db_connection()
    cursor = connection.cursor()
    query = """
        INSERT INTO business_profile (
            company_name, first_name, last_name, vat_number, email, onboard_code,
            invoice_email, country, street, additional_address, postal_code, city,
            phone, same_address, consent, subscribe
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        company_name, first_name, last_name, vat_number, email, onboard_code,
        invoice_email, country, street, additional_address, postal_code, city,
        phone, same_address, consent, subscribe
    )
    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close()

    return redirect('/thank-you')  # Redirect to a thank-you page or message

 

# Additional product routes
@app.route('/product1')
def product1():
    return render_template('product1.html')

@app.route('/product2')
def product2():
    return render_template('product2.html')

@app.route('/product3')
def product3():
    return render_template('product3.html') 

@app.route('/product4')
def product4():
    return render_template('product4.html')

@app.route('/product5')
def product5():
    return render_template('product5.html') 

@app.route('/product6')
def product6():
    return render_template('product6.html') 

@app.route('/product7')
def product7():
    return render_template('product7.html')

@app.route('/product8')
def product8():
    return render_template('product8.html')

@app.route('/product9')
def product9():
    return render_template('product9.html') 

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/active1')
def active1():
    return render_template('active1.html')

@app.route('/active2')
def active2():
    return render_template('active2.html')

@app.route('/active3')
def active3():
    return render_template('active3.html')

@app.route('/shopchocolatebar')
def shopchocolatebar():
    return render_template('shopchocolatebar.html')

@app.route('/confirmation')
def confirmation():
    return render_template('confirmation.html')



@app.route('/profile')
def profile():
    return render_template('profile.html')



@app.route('/save_order', methods=['POST'])
def save_order():
    try:
        # Get order data from the request
        order_data = request.json
        cart = order_data.get('cart', [])
        total_price = order_data.get('totalPrice', 0)
        shipping_address = order_data.get('shippingAddress', '')

        # Validate input
        if not cart:
            return jsonify({"status": "error", "message": "Cart is empty"}), 400

        # Connect to the database
        connection = get_db_connection()
        cursor = connection.cursor()

        # Insert order into orders table
        order_query = """
            INSERT INTO orders (
                total_price, 
                shipping_address, 
                order_date, 
                order_status
            ) VALUES (%s, %s, %s, %s)
        """
        order_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(order_query, (total_price, shipping_address, order_date, 'Pending'))
        order_id = cursor.lastrowid  # Get the ID of the inserted order

        # Insert order items into order_items table
        for item in cart:
            item_query = """
                INSERT INTO order_items (
                    order_id, 
                    product_name, 
                    package_quantity,
                    modal_quantity, 
                    price_per_package,
                    total_price,
                    product_description
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(item_query, (
                order_id, 
                item.get('name', ''), 
                item.get('packageQuantity', 1),
                item.get('modalQuantity', 1),
                item.get('pricePerPackage', 0),
                item.get('totalPrice', 0),
                item.get('description', '')
            ))

        # Commit the transaction
        connection.commit()

        # Close the database connection
        cursor.close()
        connection.close()

        return jsonify({
            "status": "success", 
            "order_id": order_id,
            "message": "Order saved successfully"
        }), 200

    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
        return jsonify({
            "status": "error", 
            "message": f"Database error: {str(err)}"
        }), 500
    except Exception as e:
        print(f"Unexpected error saving order: {e}")
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

@app.route('/thank-you')
def thank_you():
    return render_template('thank-you.html')



def send_confirmation_email(email, user_id):
    # Generate a unique confirmation link using user ID
    confirm_url = url_for('confirm_email', user_id=user_id, _external=True)

    # Email content
    subject = "Confirm Your Email Address"
    message = f"""
    <p>Hi,</p>
    <p>Thank you for signing up. Please confirm your email address by clicking the link below:</p>
    <p><a href="{confirm_url}">Confirm Email Address</a></p>
    <p>If you did not sign up, please ignore this email.</p>
    """

    # Send email
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'html'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            print("Confirmation email sent!")
    except Exception as e:
        print(f"Error sending email: {e}")

# Route to send email
@app.route('/send-email', methods=['POST'])
def send_email():
    data = request.json
    email = data.get('email')
    if not email:
        return jsonify({"error": "Email is required"}), 400

    # Create a user ID using a hash of the email
    user_id = hashlib.md5(email.encode()).hexdigest()

    # Store user in the database with unconfirmed status
    users_db[user_id] = {'email': email, 'confirmed': False}

    # Send confirmation email
    send_confirmation_email(email, user_id)
    return jsonify({"message": "Confirmation email sent"}), 200

# Route to confirm email
@app.route('/confirm/<user_id>')
def confirm_email(user_id):
    # Check if the user exists in the database
    user = users_db.get(user_id)
    if not user:
        return jsonify({"error": "Invalid confirmation link"}), 400

    # Mark the email as confirmed
    user['confirmed'] = True
    return jsonify({"message": f"Email {user['email']} confirmed successfully!"}), 200

@app.route('/get_orders')
def get_orders():
    try:
        # Connect to the database
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)  # Use dictionary cursor for named columns

        # Get all orders with their items
        orders_query = """
            SELECT 
                o.id,
                o.total_price,
                o.shipping_address,
                o.order_date,
                o.order_status,
                oi.product_name,
                oi.package_quantity,
                oi.modal_quantity,
                oi.price_per_package,
                oi.total_price as item_total_price,
                oi.product_description
            FROM orders o
            LEFT JOIN order_items oi ON o.id = oi.order_id
            ORDER BY o.order_date DESC
        """
        cursor.execute(orders_query)
        order_rows = cursor.fetchall()

        # Process the results into the required format
        orders_dict = {}
        formatted_orders = []

        for row in order_rows:
            order_id = row['id']
            
            # If this is a new order, initialize it
            if order_id not in orders_dict:
                orders_dict[order_id] = {
                    'id': order_id,
                    'date': row['order_date'].strftime('%Y-%m-%d %H:%M:%S'),
                    'totalPrice': float(row['total_price']),
                    'shippingAddress': row['shipping_address'],
                    'status': row['order_status'],
                    'cart': []
                }

            # Add the item to the order's cart
            if row['product_name']:  # Check if there are any items
                item = {
                    'name': row['product_name'],
                    'packageQuantity': row['package_quantity'],
                    'modalQuantity': row['modal_quantity'],
                    'pricePerPackage': float(row['price_per_package']),
                    'totalPrice': float(row['item_total_price']),
                    'description': row['product_description'],
                    # You might want to add an image URL here based on your product data
                    'image': f"/static/images/{row['product_name'].lower().replace(' ', '_')}.jpg"
                }
                orders_dict[order_id]['cart'].append(item)

        # Convert the dictionary to a list
        formatted_orders = list(orders_dict.values())

        # Close database connections
        cursor.close()
        connection.close()

        return jsonify(formatted_orders)

    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
        return jsonify({
            "status": "error",
            "message": f"Database error: {str(err)}"
        }), 500
    except Exception as e:
        print(f"Unexpected error fetching orders: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Create tables
if __name__ == '__main__':
    app.run(debug=True)
