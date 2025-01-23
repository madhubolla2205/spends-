from flask import Flask, request, jsonify, render_template
import sqlite3
import pandas as pd
import os

app = Flask(__name__)

# Database setup
db_file = "transactions.db"
if not os.path.exists(db_file):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute('''CREATE TABLE transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    description TEXT,
                    category TEXT,
                    amount REAL
                )''')
    conn.commit()
    conn.close()

# Helper: Categorize transactions
def categorize_transaction(description):
    categories = {
        "groceries": ["supermarket", "grocery"],
        "utilities": ["electric", "water", "internet"],
        "entertainment": ["movie", "netflix", "spotify"],
    }
    for category, keywords in categories.items():
        if any(keyword in description.lower() for keyword in keywords):
            return category
    return "other"

# Route: Home
@app.route('/')
def index():
    return render_template("index.html")

# Route: Upload statement
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Parse CSV file
    df = pd.read_csv(file)
    df["category"] = df["description"].apply(categorize_transaction)

    # Save to database
    conn = sqlite3.connect(db_file)
    df.to_sql("transactions", conn, if_exists="append", index=False)
    conn.close()

    return jsonify({"message": "File uploaded and processed successfully"})

# Route: Get chart data
@app.route('/chart-data', methods=['GET'])
def chart_data():
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("SELECT category, SUM(amount) FROM transactions GROUP BY category")
    data = c.fetchall()
    conn.close()

    chart_data = {"labels": [row[0] for row in data], "values": [row[1] for row in data]}
    return jsonify(chart_data)

if __name__ == "__main__":
    app.run(debug=True)
