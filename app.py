from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- DB ----------------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL,
        expiry_date TEXT,
        discount_price REAL,
        image_url TEXT,
        lat REAL,
        lng REAL,
        shop_name TEXT,
        shop_phone TEXT
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# ---------------- Discount ----------------
def calculate_discount(expiry_date):
    expiry = datetime.strptime(expiry_date, "%Y-%m-%d")
    days_left = (expiry - datetime.now()).days

    if days_left <= 1:
        return 50
    elif days_left <= 3:
        return 30
    elif days_left <= 5:
        return 15
    else:
        return 5

# ---------------- Home ----------------
@app.route("/")
def home():
    return "Kirana App Running 🚀"

# ---------------- Add Product ----------------
@app.route("/add-product", methods=["POST"])
def add_product():

    name = request.form["name"]
    price = float(request.form["price"])
    expiry_date = request.form["expiry_date"]
    lat = float(request.form["lat"])
    lng = float(request.form["lng"])

    file = request.files["image"]
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    discount = calculate_discount(expiry_date)
    discount_price = price * (1 - discount / 100)

    # dummy shop (for now)
    shop_name = "Local Kirana Store"
    shop_phone = "9999999999"

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute('''
    INSERT INTO products (
        name, price, expiry_date, discount_price,
        image_url, lat, lng, shop_name, shop_phone
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        name,
        price,
        expiry_date,
        discount_price,
        "uploads/" + filename,
        lat,
        lng,
        shop_name,
        shop_phone
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Product added!"})

# ---------------- Get Products ----------------
@app.route("/products")
def get_products():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM products")
    rows = c.fetchall()

    conn.close()

    products = []
    for row in rows:
        products.append({
            "id": row[0],
            "name": row[1],
            "price": row[2],
            "expiry_date": row[3],
            "discount_price": row[4],
            "image_url": row[5],
            "lat": row[6],
            "lng": row[7],
            "shop_name": row[8],
            "shop_phone": row[9]
        })

    return jsonify(products)

# ---------------- Images ----------------
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)