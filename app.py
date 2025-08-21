from flask import Flask, request, render_template, redirect, jsonify, url_for
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import hashlib
import mysql.connector
from mysql.connector import Error
import uuid
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "omkar123@",
    "database": "chocolate_store",
    "autocommit": True
}

# Email Configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = 'omkarreddygade@gmail.com'
EMAIL_PASSWORD = 'Omkar123reddy@'  # Consider using environment variables for security

# Database connection helper
def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        logger.error(f"Database connection error: {e}")
        return None

# Test database connection on startup
def test_db_connection():
    connection = get_db_connection()
    if connection:
        connection.close()
        logger.info("Database connection successful!")
        return True
    else:
        logger.error("Failed to connect to database!")
        return False

# Routes for pages
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/business')
def business():
    return render_template('business.html')

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

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/thank-you')
def thank_you():
    return render_template('thank-you.html')

@app.route('/confirmation')
def confirmation():
    return render_template('confirmation.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

# Product routes
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

# Handle form submission
@app.route('/submit', methods=['POST'])
def submit_form():
    data = request.form.to_dict()
    logger.info(f"Form received: {data}")
    return redirect('/thank-you')

# Save order to database
@app.route('/save_order', methods=['POST'])
def save_order():
    connection = None
    try:
        # Get order data from request
        order_data = request.json
        cart = order_data.get('cart', [])
        total_price = order_data.get('totalPrice', 0)
        shipping_address = order_data.get('shippingAddress', '')
        customer_email = order_data.get('customerEmail', '')
        customer_name = order_data.get('customerName', '')

        if not cart:
            return jsonify({"status": "error", "message": "Cart is empty"}), 400

        if not shipping_address:
            return jsonify({"status": "error", "message": "Shipping address is required"}), 400

        # Generate unique order ID
        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        # Connect to database
        connection = get_db_connection()
        if not connection:
            return jsonify({"status": "error", "message": "Database connection failed"}), 500

        cursor = connection.cursor()

        # Insert order into orders table
        insert_order_query = """
        INSERT INTO orders (order_id, total_price, shipping_address, customer_email, customer_name, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        order_values = (order_id, total_price, shipping_address, customer_email, customer_name, 'Pending')
        cursor.execute(insert_order_query, order_values)

        # Insert order items
        insert_item_query = """
        INSERT INTO order_items (order_id, product_name, description, package_quantity, 
                               modal_quantity, price_per_package, total_price, product_image)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        for item in cart:
            item_values = (
                order_id,
                item.get('name', ''),
                item.get('description', ''),
                item.get('packageQuantity', 1),
                item.get('modalQuantity', 1),
                item.get('pricePerPackage', 0),
                item.get('totalPrice', 0),
                item.get('image', '')
            )
            cursor.execute(insert_item_query, item_values)

        # Commit the transaction
        connection.commit()
        logger.info(f"Order {order_id} saved successfully")

        # Send confirmation email if email provided
        if customer_email:
            send_order_confirmation_email(customer_email, order_id, total_price, cart, shipping_address)

        return jsonify({
            "status": "success",
            "order_id": order_id,
            "message": "Order saved successfully"
        }), 200

    except Error as e:
        if connection:
            connection.rollback()
        logger.error(f"Database error: {e}")
        return jsonify({
            "status": "error",
            "message": f"Database error: {str(e)}"
        }), 500
    except Exception as e:
        if connection:
            connection.rollback()
        logger.error(f"Unexpected error: {e}")
        return jsonify({
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# Get orders from database
@app.route('/get_orders')
def get_orders():
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = connection.cursor(dictionary=True)
        
        # Get orders with their items
        query = """
        SELECT o.*, GROUP_CONCAT(
            CONCAT(oi.product_name, '|', oi.modal_quantity, '|', oi.total_price, '|', oi.description, '|', oi.product_image)
            SEPARATOR ';;'
        ) as items
        FROM orders o
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        GROUP BY o.id
        ORDER BY o.order_date DESC
        """
        
        cursor.execute(query)
        orders_data = cursor.fetchall()
        
        # Format the orders data
        orders = []
        for order in orders_data:
            # Parse items
            cart_items = []
            if order['items']:
                items_list = order['items'].split(';;')
                for item_str in items_list:
                    item_parts = item_str.split('|')
                    if len(item_parts) >= 5:
                        cart_items.append({
                            "name": item_parts[0],
                            "modalQuantity": int(item_parts[1]),
                            "totalPrice": float(item_parts[2]),
                            "description": item_parts[3],
                            "image": item_parts[4]
                        })
            
            orders.append({
                "id": order['id'],
                "order_id": order['order_id'],
                "date": order['order_date'].strftime('%Y-%m-%d %H:%M:%S'),
                "totalPrice": float(order['total_price']),
                "shippingAddress": order['shipping_address'],
                "status": order['status'],
                "customerEmail": order['customer_email'],
                "customerName": order['customer_name'],
                "cart": cart_items
            })
        
        return jsonify(orders)

    except Error as e:
        logger.error(f"Database error in get_orders: {e}")
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"Unexpected error in get_orders: {e}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# Get order by ID
@app.route('/get_order/<order_id>')
def get_order(order_id):
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = connection.cursor(dictionary=True)
        
        # Get specific order
        order_query = "SELECT * FROM orders WHERE order_id = %s"
        cursor.execute(order_query, (order_id,))
        order = cursor.fetchone()
        
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        # Get order items
        items_query = "SELECT * FROM order_items WHERE order_id = %s"
        cursor.execute(items_query, (order_id,))
        items = cursor.fetchall()
        
        # Format response
        order_data = {
            "id": order['id'],
            "order_id": order['order_id'],
            "date": order['order_date'].strftime('%Y-%m-%d %H:%M:%S'),
            "totalPrice": float(order['total_price']),
            "shippingAddress": order['shipping_address'],
            "status": order['status'],
            "customerEmail": order['customer_email'],
            "customerName": order['customer_name'],
            "cart": []
        }
        
        for item in items:
            order_data['cart'].append({
                "name": item['product_name'],
                "description": item['description'],
                "packageQuantity": item['package_quantity'],
                "modalQuantity": item['modal_quantity'],
                "pricePerPackage": float(item['price_per_package']),
                "totalPrice": float(item['total_price']),
                "image": item['product_image']
            })
        
        return jsonify(order_data)

    except Error as e:
        logger.error(f"Database error in get_order: {e}")
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# Email functions
def send_order_confirmation_email(email, order_id, total_price, cart, shipping_address):
    try:
        subject = f"Order Confirmation - {order_id}"
        
        # Create HTML email content
        items_html = ""
        for item in cart:
            items_html += f"""
            <tr>
                <td>{item.get('name', '')}</td>
                <td>{item.get('modalQuantity', 1)}</td>
                <td>€{item.get('totalPrice', 0)}</td>
            </tr>
            """
        
        message = f"""
        <html>
        <body>
            <h2>Thank you for your order!</h2>
            <p><strong>Order ID:</strong> {order_id}</p>
            <p><strong>Total Amount:</strong> €{total_price}</p>
            <p><strong>Shipping Address:</strong> {shipping_address}</p>
            
            <h3>Order Items:</h3>
            <table border="1" cellpadding="5" cellspacing="0">
                <thead>
                    <tr>
                        <th>Product Name</th>
                        <th>Quantity</th>
                        <th>Price</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                </tbody>
            </table>
            
            <p>Your order will be processed and shipped soon!</p>
            <p>Thank you for choosing Simply Chocolate!</p>
        </body>
        </html>
        """
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'html'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            logger.info(f"Order confirmation email sent to {email}")
    except Exception as e:
        logger.error(f"Error sending order confirmation email: {e}")

def send_confirmation_email(email, user_id):
    confirm_url = url_for('confirm_email', user_id=user_id, _external=True)
    subject = "Confirm Your Email Address"
    message = f"""
    <html>
    <body>
        <p>Hi,</p>
        <p>Thank you for signing up. Please confirm your email address by clicking the link below:</p>
        <p><a href="{confirm_url}">Confirm Email Address</a></p>
        <p>If you did not sign up, please ignore this email.</p>
    </body>
    </html>
    """
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
            logger.info("Confirmation email sent!")
    except Exception as e:
        logger.error(f"Error sending email: {e}")

@app.route('/send-email', methods=['POST'])
def send_email():
    connection = None
    try:
        data = request.json
        email = data.get('email')
        if not email:
            return jsonify({"error": "Email is required"}), 400

        user_id = hashlib.md5(email.encode()).hexdigest()
        
        # Save to database
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            insert_query = """
            INSERT INTO users (email, user_id_hash, confirmed) 
            VALUES (%s, %s, %s) 
            ON DUPLICATE KEY UPDATE user_id_hash = %s
            """
            cursor.execute(insert_query, (email, user_id, False, user_id))
            connection.commit()
            cursor.close()

        send_confirmation_email(email, user_id)
        return jsonify({"message": "Confirmation email sent"}), 200

    except Exception as e:
        logger.error(f"Error in send_email: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if connection and connection.is_connected():
            connection.close()

@app.route('/confirm/<user_id>')
def confirm_email(user_id):
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = connection.cursor()
        # Update user confirmation status
        update_query = "UPDATE users SET confirmed = TRUE WHERE user_id_hash = %s"
        cursor.execute(update_query, (user_id,))
        
        if cursor.rowcount > 0:
            connection.commit()
            # Get user email for response
            select_query = "SELECT email FROM users WHERE user_id_hash = %s"
            cursor.execute(select_query, (user_id,))
            user = cursor.fetchone()
            email = user[0] if user else "Unknown"
            
            return jsonify({"message": f"Email {email} confirmed successfully!"}), 200
        else:
            return jsonify({"error": "Invalid confirmation link"}), 400

    except Exception as e:
        logger.error(f"Error in confirm_email: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# Update order status
@app.route('/update_order_status', methods=['POST'])
def update_order_status():
    connection = None
    try:
        data = request.json
        order_id = data.get('order_id')
        new_status = data.get('status')
        
        if not order_id or not new_status:
            return jsonify({"error": "Order ID and status are required"}), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = connection.cursor()
        update_query = "UPDATE orders SET status = %s WHERE order_id = %s"
        cursor.execute(update_query, (new_status, order_id))
        
        if cursor.rowcount > 0:
            connection.commit()
            return jsonify({"message": "Order status updated successfully"}), 200
        else:
            return jsonify({"error": "Order not found"}), 404
            
    except Exception as e:
        logger.error(f"Error updating order status: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# Run the app
if __name__ == '__main__':
    # Test database connection on startup
    if test_db_connection():
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        logger.error("Cannot start application - database connection failed!")
        exit(1)