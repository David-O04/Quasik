from flask import Flask, jsonify, render_template, request, redirect, url_for
import asyncpg

app = Flask(__name__)

# Dummy credentials for demonstration
USERNAME = "admin"
PASSWORD = "password"

# Database connection function
async def get_db_connection():
    conn = await asyncpg.connect(
        host='localhost',  
        port=5434,         
        user='davoberi',   
        password='1234',   
        database='davoberi' 
    )
    return conn

# Route to fetch data from PostgreSQL
@app.route('/fetch_data_for_d3')
async def fetch_data_for_d3():
    conn = await get_db_connection()
    try:
        # SQL query to count the number of log entries for each service_name
        rows = await conn.fetch("SELECT service_name, COUNT(*) AS value FROM audit_logs GROUP BY service_name")
        data = [{"message": row['service_name'], "value": row['value']} for row in rows]
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        await conn.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid credentials!'
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # You can add further logic to check if the user is logged in
    return render_template('index.html')

@app.route('/')
def root():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
