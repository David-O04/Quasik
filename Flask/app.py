from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import asyncpg
import json

app = Flask(__name__)

# secret key for flash messages
app.secret_key = 'super_secret_key'

# credentials for simple authentication
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

# Allowed file extensions
ALLOWED_EXTENSIONS = {'json'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

async def insert_data_into_db(data):
    conn = await get_db_connection()
    try:
        for entry in data:
            # Insert each entry into the database
            await conn.execute(
                """
                INSERT INTO audit_logs 
                (insert_id, log_name, audit_type, authentication_info, 
                authorization_info, method_name, request, request_metadata, 
                resource_name, service_name, status, principal_email) 
                VALUES 
                ($1, $2, $3, $4::jsonb, $5::jsonb[], $6, $7::jsonb, $8::jsonb, $9, $10, $11::jsonb, $12)
                """,
                entry['insertId'],
                entry['logName'],
                entry['protoPayload']['@type'],
                json.dumps(entry['protoPayload'].get('authenticationInfo', {})),
                json.dumps(entry['protoPayload'].get('authorizationInfo', [])),
                entry['protoPayload'].get('methodName', ''),
                json.dumps(entry['protoPayload'].get('request', {})),
                json.dumps(entry['protoPayload'].get('requestMetadata', {})),
                entry['protoPayload'].get('resourceName', ''),
                entry['protoPayload'].get('serviceName', ''),
                json.dumps(entry['protoPayload'].get('status', {})),
                entry['protoPayload'].get('authenticationInfo', {}).get('principalEmail', '')
            )
    except Exception as e:
        # Handle exceptions
        flash(f"An error occurred: {e}")
    finally:
        await conn.close()

# Route to fetch data from PostgreSQL
@app.route('/fetch_data_for_d3')
async def fetch_data_for_d3():
    conn = await get_db_connection()
    try:
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
            flash('Invalid credentials!')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('index.html')

@app.route('/')
def root():
    return redirect(url_for('login'))

# Flask route for File Uploads
@app.route('/upload_json', methods=['GET', 'POST'])
async def upload_json():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            data = json.load(file)
            await insert_data_into_db(data)
            flash('File uploaded successfully!')
            return redirect(url_for('dashboard'))
    else:
        return render_template('upload_json.html')

if __name__ == '__main__':
    app.run(debug=True)
