from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
import webbrowser
from threading import Timer
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for sessions

# Replace with your actual credentials
VALID_USERNAME = "tanunaik9623@gmail.com"
VALID_PASSWORD = "tanu2408"

def open_browser():
    webbrowser.open("http://127.0.0.1:5000")

def init_db():
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS stock (
        Product_Id TEXT PRIMARY KEY,
        Product_Name TEXT,
        Sell_Price REAL,
        Quantity INTEGER
    )''')
    conn.commit()
    conn.close()

# ---------------- LOGIN SYSTEM ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == VALID_USERNAME and password == VALID_PASSWORD:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return "Invalid credentials. Please try again."

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# ---------------- PRODUCT MANAGEMENT ----------------
@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    c.execute('SELECT * FROM stock')
    products = c.fetchall()
    
    total_cost = sum(float(p[2]) * int(p[3]) for p in products)
    total_products = len(products)
    
    conn.close()
    return render_template('index.html', products=products, total_cost=total_cost, total_products=total_products)

@app.route('/add', methods=['POST'])
def add_product():
    if 'username' not in session:
        return redirect(url_for('login'))

    product_id = request.form['product_id']
    product_name = request.form['product_name']
    sell_price = request.form['sell_price']
    quantity = request.form['quantity']
    
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    c.execute('INSERT INTO stock (Product_Id, Product_Name, Sell_Price, Quantity) VALUES (?, ?, ?, ?)',
              (product_id, product_name, sell_price, quantity))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/update', methods=['POST'])
def update_product():
    if 'username' not in session:
        return redirect(url_for('login'))

    product_id = request.form['product_id']
    product_name = request.form['product_name']
    sell_price = request.form['sell_price']
    quantity = request.form['quantity']
    
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    c.execute('UPDATE stock SET Product_Name=?, Sell_Price=?, Quantity=? WHERE Product_Id=?',
              (product_name, sell_price, quantity, product_id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<product_id>')
def delete_product(product_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    c.execute('DELETE FROM stock WHERE Product_Id=?', (product_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/generate-receipt')
def generate_receipt():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("SELECT Product_Name, Sell_Price, Quantity FROM stock")
    products = cursor.fetchall()
    conn.close()

    total = sum(float(p[1]) * int(p[2]) for p in products)

    receipt_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Receipt</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; }}
            th {{ background-color: #4CAF50; color: white; }}
            .total {{ font-weight: bold; text-align: right; }}
        </style>
    </head>
    <body>
        <h1>🧾 Receipt</h1>
        <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <table>
            <tr>
                <th>Product Name</th>
                <th>Price ($)</th>
                <th>Quantity</th>
                <th>Line Total ($)</th>
            </tr>
    """
    for p in products:
        line_total = float(p[1]) * int(p[2])
        receipt_html += f"""
            <tr>
                <td>{p[0]}</td>
                <td>{float(p[1]):.2f}</td>
                <td>{int(p[2])}</td>
                <td>{line_total:.2f}</td>
            </tr>
        """
    receipt_html += f"""
        </table>
        <p class="total">Grand Total: ${total:.2f}</p>
        <button onclick="window.print()">🖨️ Print Receipt</button>
         <a href="/">Back</a>
    </body>
    </html>
    """
    return receipt_html

if __name__ == '__main__':
    init_db()
    Timer(1, open_browser).start()
    app.run(debug=True, host='0.0.0.0', port=5000)
