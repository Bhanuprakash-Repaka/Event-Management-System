from flask import Flask, render_template, request, redirect, send_file, url_for, session, flash, Response
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os
import csv
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'events_management'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('index.html')

# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        details = request.form
        name = details['name']
        email = details['email']
        phone = details['phone']
        password = details['password']
        address = details['address']
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO users (name, email, phone, password, address) VALUES (%s, %s, %s, %s, %s)', (name, email, phone, password, address))
        mysql.connection.commit()
        cursor.close()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# Event Customization
@app.route('/customize_event', methods=['GET', 'POST'])
def customize_event():
    if 'loggedin' in session:
        if request.method == 'POST':
            details = request.form
            event_type = details['event_type']
            venue = details['venue']
            guest_count = details['guest_count']
            catering = details['catering_preferences']
            decoration = details['decoration_details']
            entertainment = details['entertainment_options']
            photography = details['photography_options']
            special_req = details['special_requirements']
            estimated_cost = details['estimated_cost']
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO event_customization (user_id, event_type, venue, guest_count, catering_preferences, decoration_details, entertainment_options, photography_options, special_requirements, estimated_cost) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (session['id'], event_type, venue, guest_count, catering, decoration, entertainment, photography, special_req, estimated_cost))
            mysql.connection.commit()
            cursor.close()
            flash('Event customization saved successfully!', 'success')
            return redirect(url_for('dashboard'))
        return render_template('customize_event.html')
    return redirect(url_for('login'))


# Event Management
@app.route('/admin/events', methods=['GET', 'POST'])
def manage_events():
    if 'loggedin' in session and session['email'] == 'admin@gmail.com':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST':
            event_type = request.form['event_type']
            description = request.form['description']
            price_range = request.form['price_range']
            available_venues = request.form['available_venues']
            service_providers = request.form['service_providers']
            cursor.execute('INSERT INTO events (event_type, description, price_range, available_venues, service_providers) VALUES (%s, %s, %s, %s, %s)', (event_type, description, price_range, available_venues, service_providers))
            mysql.connection.commit()
            flash('Event added successfully!', 'success')
        cursor.execute('SELECT * FROM events')
        events = cursor.fetchall()
        return render_template('manage_events.html', events=events)
    return redirect(url_for('login'))

@app.route('/admin/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    if 'loggedin' in session and session['email'] == 'admin@gmail.com':
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE FROM events WHERE id = %s', (event_id,))
        mysql.connection.commit()
        flash('Event deleted successfully!', 'success')
    return redirect(url_for('manage_events'))

# Booking an Event
@app.route('/book_event', methods=['GET', 'POST'])
def book_event():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM events')
        events = cursor.fetchall()
        
        if request.method == 'POST':
            event_id = request.form['event_id']
            booking_date = request.form['booking_date']
            booking_time = request.form['booking_time']
            location = request.form['location']
            estimated_cost = request.form['estimated_cost']
            deposit_paid = request.form['deposit_paid']
            payment_method = request.form['payment_method']
            payment_status = 'Pending'  # Mark payment as completed after successful payment
            
            # Check if another booking exists for the same date, time, and location
            cursor.execute('SELECT * FROM bookings WHERE booking_date = %s AND booking_time = %s AND location = %s',
                           (booking_date, booking_time, location))
            existing_booking = cursor.fetchone()
            
            if existing_booking:
                return render_template('book_event.html', events=events, error_message='This location is already booked for the selected date and time. Please choose another location.')
               
            # Insert booking details into database
            cursor.execute('INSERT INTO bookings (user_id, event_id, booking_date, booking_time, location, estimated_cost, deposit_paid, payment_status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', 
                           (session['id'], event_id, booking_date, booking_time, location, estimated_cost, deposit_paid, payment_status))
            mysql.connection.commit()
            
            # Get the booking ID for the invoice
            cursor.execute('SELECT LAST_INSERT_ID() AS booking_id')
            booking = cursor.fetchone()
            booking_id = booking['booking_id']
            
            return render_template('book_event.html', events=events, success_message='Event booked successfully and payment completed!', redirect_url=url_for('generate_invoice', booking_id=booking_id))
        
        return render_template('book_event.html', events=events)
    return redirect(url_for('login'))

# Generate Invoice after Payment
@app.route('/generate_invoice/<int:booking_id>')
def generate_invoice(booking_id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT b.id, e.event_type, b.booking_date, b.booking_time, b.location, b.estimated_cost, b.deposit_paid, b.payment_status FROM bookings b JOIN events e ON b.event_id = e.id WHERE b.id = %s AND b.user_id = %s', (booking_id, session['id']))
        booking = cursor.fetchone()
        
        if booking:
            return render_template('invoice.html', booking=booking)
        else:
            return redirect(url_for('book_event'))
    return redirect(url_for('login'))

@app.route('/booking_history', methods=['GET'])
def booking_history():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''SELECT b.id, e.event_type, b.booking_date, b.booking_time, b.estimated_cost, 
                          b.deposit_paid, b.payment_status FROM bookings b 
                          JOIN events e ON b.event_id = e.id WHERE b.user_id = %s''', (session['id'],))
        bookings = cursor.fetchall()
        return render_template('booking_history.html', bookings=bookings)
    return redirect(url_for('login'))

from flask import Response

@app.route('/download_invoice/<int:booking_id>', methods=['GET'])
def download_invoice(booking_id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''SELECT b.id, e.event_type, b.booking_date, b.booking_time, b.estimated_cost, 
                          b.deposit_paid, b.payment_status, u.name AS user_name, u.email AS user_email 
                          FROM bookings b 
                          JOIN events e ON b.event_id = e.id 
                          JOIN users u ON b.user_id = u.id 
                          WHERE b.id = %s AND b.user_id = %s''', 
                       (booking_id, session['id']))
        booking = cursor.fetchone()

        if booking:
            rendered_html = render_template('invoice_template.html', booking=booking)
            return Response(
                rendered_html,
                mimetype="text/html",
                headers={"Content-Disposition": f"attachment;filename=invoice_{booking_id}.html"}
            )
        else:
            flash('Invoice not found!', 'danger')
            return redirect(url_for('booking_history'))
    return redirect(url_for('login'))

import csv
from io import StringIO

@app.route('/download_invoice_csv/<int:booking_id>', methods=['GET'])
def download_invoice_csv(booking_id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''SELECT b.id, e.event_type, b.booking_date, b.booking_time, b.estimated_cost, 
                          b.deposit_paid, b.payment_status, u.name AS user_name, u.email AS user_email 
                          FROM bookings b 
                          JOIN events e ON b.event_id = e.id 
                          JOIN users u ON b.user_id = u.id 
                          WHERE b.id = %s AND b.user_id = %s''', 
                       (booking_id, session['id']))
        booking = cursor.fetchone()

        if booking:
            # Create CSV in memory
            output = StringIO()
            csv_writer = csv.writer(output)
            
            # Write headers
            csv_writer.writerow(["Invoice ID", "Customer Name", "Email", "Event Type", "Booking Date", "Booking Time", "Estimated Cost", "Deposit Paid", "Remaining Amount"])
            
            # Write data
            csv_writer.writerow([
                booking["id"], booking["user_name"], booking["user_email"], 
                booking["event_type"], booking["booking_date"], booking["booking_time"], 
                booking["estimated_cost"], booking["deposit_paid"], 
                booking["estimated_cost"] - booking["deposit_paid"]
            ])
            
            output.seek(0)

            return Response(
                output.getvalue(),
                mimetype="text/csv",
                headers={"Content-Disposition": f"attachment;filename=invoice_{booking_id}.csv"}
            )
        else:
            flash('Invoice not found!', 'danger')
            return redirect(url_for('booking_history'))
    return redirect(url_for('login'))



@app.route('/my_bookings')
def my_bookings():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT b.id, e.event_type, b.booking_date, b.payment_status FROM bookings b JOIN events e ON b.event_id = e.id WHERE b.user_id = %s', (session['id'],))
        bookings = cursor.fetchall()
        return render_template('my_bookings.html', bookings=bookings)
    return redirect(url_for('login'))

@app.route('/cancel_booking/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE FROM bookings WHERE id = %s AND user_id = %s', (booking_id, session['id']))
        mysql.connection.commit()
        flash('Booking cancelled successfully!', 'success')
    return redirect(url_for('my_bookings'))

# Payment Module
@app.route('/make_payment/<int:booking_id>', methods=['GET', 'POST'])
def make_payment(booking_id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM bookings WHERE id = %s AND user_id = %s', (booking_id, session['id']))
        booking = cursor.fetchone()
        
        if not booking:
            flash('Invalid booking!', 'danger')
            return redirect(url_for('booking_history'))
        
        if request.method == 'POST':
            payment_method = request.form['payment_method']
            amount = request.form['amount']
            payment_status = 'Completed'
            
            cursor.execute('UPDATE bookings SET payment_status = %s WHERE id = %s', (payment_status, booking_id))
            cursor.execute('INSERT INTO payments (user_id, booking_id, amount, payment_method, status) VALUES (%s, %s, %s, %s, %s)', 
                           (session['id'], booking_id, amount, payment_method, payment_status))
            mysql.connection.commit()
            flash('Payment successful!', 'success')
            return redirect(url_for('booking_history'))
        
        return render_template('make_payment.html', booking=booking)
    return redirect(url_for('login'))

# Payment Module
@app.route('/process_payment', methods=['POST'])
def process_payment():
    if 'loggedin' in session:
        details = request.form
        booking_id = details['booking_id']
        amount = details['amount']
        payment_status = "Completed"
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE bookings SET payment_status = %s WHERE id = %s', (payment_status, booking_id))
        cursor.execute('INSERT INTO payments (user_id, booking_id, amount, status) VALUES (%s, %s, %s, %s)', (session['id'], booking_id, amount, payment_status))
        mysql.connection.commit()
        cursor.close()
        flash('Payment processed successfully!', 'success')
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))



# Gallery View
@app.route('/gallery', methods=['GET', 'POST'])
def gallery():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        search_query = request.args.get('search', '')
        
        if search_query:
            cursor.execute("""
                SELECT * FROM gallery WHERE event_type LIKE %s OR venue LIKE %s""",
                (f"%{search_query}%", f"%{search_query}%"))
        else:
            cursor.execute("SELECT * FROM gallery")
        images = cursor.fetchall()
        
        if request.method == 'POST':
            if 'file' not in request.files:
                flash('No file selected!', 'danger')
                return redirect(url_for('gallery'))
            file = request.files['file']
            if file.filename == '':
                flash('No file selected!', 'danger')
                return redirect(url_for('gallery'))
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            event_type = request.form.get('event_type', 'General')
            venue = request.form.get('venue', 'Unknown')
            cursor.execute('INSERT INTO gallery (user_id, image_path, event_type, venue) VALUES (%s, %s, %s, %s)', 
                           (session['id'], filename, event_type, venue))
            mysql.connection.commit()
            flash('Image uploaded successfully!', 'success')
            return redirect(url_for('gallery'))
        
        return render_template('gallery.html', images=images, search_query=search_query)
    return redirect(url_for('login'))


# @app.route('/delete_gallery/<int:image_id>', methods=['POST'])
# def delete_gallery(image_id):
#     if 'loggedin' in session:
#         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#         cursor.execute('SELECT image_path FROM gallery WHERE id = %s AND user_id = %s', (image_id, session['id']))
#         image = cursor.fetchone()
        
#         if image:
#             image_path = os.path.join(app.config['UPLOAD_FOLDER'], image['image_path'])
#             if os.path.exists(image_path):
#                 os.remove(image_path)
#             cursor.execute('DELETE FROM gallery WHERE id = %s AND user_id = %s', (image_id, session['id']))
#             mysql.connection.commit()
#             flash('Image deleted successfully!', 'success')
#         else:
#             flash('Image not found or unauthorized access!', 'danger')
#     return redirect(url_for('gallery'))



# # Event Management
# @app.route('/events', methods=['GET', 'POST'])
# def manage_events():
#     if 'loggedin' in session and session['email'] == 'admin@gmail.com':
#         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#         if request.method == 'POST':
#             event_type = request.form['event_type']
#             description = request.form['description']
#             price_range = request.form['price_range']
#             available_venues = request.form['available_venues']
#             service_providers = request.form['service_providers']
#             cursor.execute('INSERT INTO events (event_type, description, price_range, available_venues, service_providers) VALUES (%s, %s, %s, %s, %s)', (event_type, description, price_range, available_venues, service_providers))
#             mysql.connection.commit()
#             flash('Event added successfully!', 'success')
#         cursor.execute('SELECT * FROM events')
#         events = cursor.fetchall()
#         return render_template('manage_events.html', events=events)
#     return redirect(url_for('login'))

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['email'] = account['email']
            return redirect(url_for('admin_dashboard') if account['email'] == 'admin@gmail.com' else 'dashboard')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        return render_template('dashboard.html', email=session['email'])
    return redirect(url_for('login'))

# Admin Dashboard
@app.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():
    if 'loggedin' in session and session['email'] == 'admin@gmail.com':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT COUNT(*) AS user_count FROM users')
        user_count = cursor.fetchone()['user_count']
        
        cursor.execute('SELECT COUNT(*) AS booking_count FROM bookings')
        booking_count = cursor.fetchone()['booking_count']
        
        cursor.execute('SELECT COUNT(*) AS payment_count FROM payments')
        payment_count = cursor.fetchone()['payment_count']
        
        cursor.execute('SELECT COUNT(*) AS gallery_count FROM gallery')
        gallery_count = cursor.fetchone()['gallery_count']
        
        cursor.execute('SELECT * FROM users LIMIT 5')
        recent_users = cursor.fetchall()
        
        cursor.execute('SELECT * FROM bookings ORDER BY booking_date DESC LIMIT 5')
        recent_bookings = cursor.fetchall()
        
        cursor.execute('SELECT * FROM payments ORDER BY id DESC LIMIT 5')
        recent_payments = cursor.fetchall()
        
        return render_template('admin_dashboard.html', user_count=user_count, booking_count=booking_count, payment_count=payment_count, gallery_count=gallery_count, recent_users=recent_users, recent_bookings=recent_bookings, recent_payments=recent_payments)
    return redirect(url_for('login'))

# Export Reports to CSV
@app.route('/export_users_csv')
def export_users_csv():
    if 'loggedin' in session and session['email'] == 'admin@gmail.com':
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id, name, email, phone, address FROM users')
        users = cursor.fetchall()
        output = [['ID', 'Name', 'Email', 'Phone', 'Address']]
        output.extend(users)
        
        def generate():
            for row in output:
                yield ','.join(map(str, row)) + '\n'
        
        return Response(generate(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=users_report.csv'})
    return redirect(url_for('login'))

# # Gallery Management
# @app.route('/gallery', methods=['GET', 'POST'])
# def gallery():
#     if 'loggedin' in session:
#         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#         cursor.execute('SELECT * FROM gallery')
#         images = cursor.fetchall()
#         return render_template('gallery.html', images=images)
#     return redirect(url_for('login'))

@app.route('/admin/bookings', methods=['GET'])
def admin_bookings():
    if 'loggedin' in session and session['email'] == 'admin@gmail.com':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        search_query = request.args.get('search', '')
        
        if search_query:
            cursor.execute("""
                SELECT b.id, u.name AS user_name, e.event_type, b.booking_date,b.deposit_paid, b.payment_status 
                FROM bookings b 
                JOIN users u ON b.user_id = u.id 
                JOIN events e ON b.event_id = e.id 
                WHERE u.name LIKE %s OR e.event_type LIKE %s""", (f"%{search_query}%", f"%{search_query}%"))
        else:
            cursor.execute("""
                SELECT b.id, u.name AS user_name, e.event_type, b.booking_date,b.deposit_paid, b.payment_status 
                FROM bookings b 
                JOIN users u ON b.user_id = u.id 
                JOIN events e ON b.event_id = e.id""")
        
        bookings = cursor.fetchall()
        return render_template('admin_bookings.html', bookings=bookings, search_query=search_query)
    return redirect(url_for('login'))

@app.route('/admin/mark_booking_paid/<int:booking_id>', methods=['POST'])
def mark_booking_paid(booking_id):
    if 'loggedin' in session and session['email'] == 'admin@gmail.com':
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE bookings SET payment_status = "Completed" WHERE id = %s', (booking_id,))
        cursor.execute('INSERT INTO payments (user_id, booking_id, amount, status) SELECT user_id, id, 0, "Completed" FROM bookings WHERE id = %s', (booking_id,))
        mysql.connection.commit()
        flash('Booking marked as paid successfully!', 'success')
    return redirect(url_for('admin_bookings'))

@app.route('/admin/delete_booking/<int:booking_id>', methods=['POST'])
def delete_booking(booking_id):
    if 'loggedin' in session and session['email'] == 'admin@gmail.com':
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE FROM bookings WHERE id = %s', (booking_id,))
        mysql.connection.commit()
        flash('Booking deleted successfully!', 'success')
    return redirect(url_for('admin_bookings'))

@app.route('/admin/payments', methods=['GET'])
def admin_payments():
    if 'loggedin' in session and session['email'] == 'admin@gmail.com':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        search_query = request.args.get('search', '')
        
        if search_query:
            cursor.execute("""
                SELECT p.id, u.name AS user_name, e.event_type, p.amount, p.status 
                FROM payments p 
                JOIN users u ON p.user_id = u.id 
                JOIN bookings b ON p.booking_id = b.id 
                JOIN events e ON b.event_id = e.id 
                WHERE u.name LIKE %s OR e.event_type LIKE %s""", (f"%{search_query}%", f"%{search_query}%"))
        else:
            cursor.execute("""
                SELECT p.id, u.name AS user_name, e.event_type, p.amount, p.status 
                FROM payments p 
                JOIN users u ON p.user_id = u.id 
                JOIN bookings b ON p.booking_id = b.id 
                JOIN events e ON b.event_id = e.id""")
        
        payments = cursor.fetchall()
        return render_template('admin_payments.html', payments=payments, search_query=search_query)
    return redirect(url_for('login'))

@app.route('/admin/mark_payment_completed/<int:payment_id>', methods=['POST'])
def mark_payment_completed(payment_id):
    if 'loggedin' in session and session['email'] == 'admin@gmail.com':
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE payments SET status = "Completed" WHERE id = %s', (payment_id,))
        mysql.connection.commit()
        flash('Payment marked as completed successfully!', 'success')
    return redirect(url_for('admin_payments'))

@app.route('/admin/delete_payment/<int:payment_id>', methods=['POST'])
def delete_payment(payment_id):
    if 'loggedin' in session and session['email'] == 'admin@gmail.com':
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE FROM payments WHERE id = %s', (payment_id,))
        mysql.connection.commit()
        flash('Payment deleted successfully!', 'success')
    return redirect(url_for('admin_payments'))

@app.route('/admin/gallery', methods=['GET', 'POST'])
def admin_gallery():
    if 'loggedin' in session and session['email'] == 'admin@gmail.com':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        search_query = request.args.get('search', '')
        
        if search_query:
            cursor.execute("SELECT * FROM gallery WHERE event_type LIKE %s OR venue LIKE %s", (f"%{search_query}%", f"%{search_query}%"))
        else:
            cursor.execute("SELECT * FROM gallery")
        images = cursor.fetchall()
        
        if request.method == 'POST':
            if 'file' not in request.files:
                flash('No file selected!', 'danger')
                return redirect(url_for('admin_gallery'))
            file = request.files['file']
            if file.filename == '':
                flash('No file selected!', 'danger')
                return redirect(url_for('admin_gallery'))
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            event_type = request.form.get('event_type', 'General')
            venue = request.form.get('venue', 'Unknown')
            cursor.execute('INSERT INTO gallery (user_id, image_path, event_type, venue) VALUES (%s, %s, %s, %s)', 
                           (session['id'], filename, event_type, venue))
            mysql.connection.commit()
            flash('Media uploaded successfully!', 'success')
            return redirect(url_for('admin_gallery'))
        
        return render_template('admin_gallery.html', images=images, search_query=search_query)
    return redirect(url_for('login'))

@app.route('/admin/delete_gallery/<int:image_id>', methods=['POST'])
def delete_gallery(image_id):
    if 'loggedin' in session and session['email'] == 'admin@gmail.com':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT image_path FROM gallery WHERE id = %s', (image_id,))
        image = cursor.fetchone()
        
        if image:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image['image_path'])
            if os.path.exists(image_path):
                os.remove(image_path)
            cursor.execute('DELETE FROM gallery WHERE id = %s', (image_id,))
            mysql.connection.commit()
            flash('Media deleted successfully!', 'success')
        else:
            flash('Media not found!', 'danger')
    return redirect(url_for('admin_gallery'))


# User Management
@app.route('/admin/users', methods=['GET'])
def admin_users():
    if 'loggedin' in session and session['email'] == 'admin@gmail.com':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT id, name, email, phone, address FROM users')
        users = cursor.fetchall()
        return render_template('admin_users.html', users=users)
    return redirect(url_for('login'))

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'loggedin' in session and session['email'] == 'admin@gmail.com':
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
        mysql.connection.commit()
        flash('User deleted successfully!', 'success')
    return redirect(url_for('admin_users'))

@app.route('/upload_gallery', methods=['POST'])
def upload_gallery():
    if 'loggedin' in session:
        if 'file' not in request.files:
            return redirect(url_for('gallery'))
        file = request.files['file']
        if file.filename == '':
            return redirect(url_for('gallery'))
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO gallery (user_id, image_path) VALUES (%s, %s)', (session['id'], filename))
        mysql.connection.commit()
        cursor.close()
        flash('Image uploaded successfully!', 'success')
        return redirect(url_for('gallery'))
    return redirect(url_for('login'))

# Logout
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)