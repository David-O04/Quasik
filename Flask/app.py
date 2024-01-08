from flask import Flask, jsonify, render_template
import asyncpg
import json
import os
from collections import Counter

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

# Route for processing log data from JSON files
@app.route('/fetch_data_for_d3')
def fetch_data_for_d3():
    log_directory = "logs"
    severity_counter = Counter()

    # Process each log file
    for filename in os.listdir(log_directory):
        if filename.endswith(".json"):
            with open(os.path.join(log_directory, filename), 'r') as file:
                log_data = json.load(file)
                for entry in log_data:
                    severity = entry.get("severity", "Unknown")
                    severity_counter[severity] += 1

    # Convert the counter to the format expected by D3.js
    processed_data = [{"message": severity, "value": count} for severity, count in severity_counter.items()]
    return jsonify(processed_data)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
