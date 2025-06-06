# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # Replace with your MySQL username
    'password': 'your_password',  # Replace with your MySQL password
    'database': 'contact_db'  # Replace with your database name
}

# Route to render the contact page
@app.route('/')
def home():
    return render_template('contact.html')

# Route to handle form submission
@app.route('/contact', methods=['POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        try:
            # Connect to the database
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Insert data into the contact table
            insert_query = """
            INSERT INTO contacts (name, email, message)
            VALUES (%s, %s, %s)
            """
            cursor.execute(insert_query, (name, email, message))
            conn.commit()

            flash('Message sent successfully!', 'success')
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)