from flask import Flask, jsonify, render_template
import asyncpg

app = Flask(__name__)

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

async def fetch_data():
    conn = await get_db_connection()
    try:
        rows = await conn.fetch("SELECT * FROM audit_logs")  # Adjust query as needed
        return [dict(row) for row in rows]
    finally:
        await conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/fetch_data_for_d3')
async def fetch_data_for_d3():
    try:
        data = await fetch_data()
        return jsonify(data)
    except Exception as e:
        app.logger.error(f"Error fetching data: {e}")
        return jsonify({"error": "Error fetching data"}), 500

if __name__ == '__main__':
    app.run(debug=True)
