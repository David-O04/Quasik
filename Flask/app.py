from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from flask import Flask, request
from werkzeug.exceptions import RequestEntityTooLarge
import asyncpg
import json
import logging

app = Flask(__name__)

# secret key for flash messages
app.secret_key = b'\xa3\x8b\x1dO \xf8<\x1f\xb3\xfb\xefT\x85\xda\xa0Tw\xc8R\x88,$\x12\x16'

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Set maximum file upload size to 10MB
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return "File too large", 413

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
            # Extract relevant fields from the entry
            insert_id = entry.get('insertId', '')
            log_name = entry.get('logName', '')
            proto_payload = entry.get('protoPayload', {})
            audit_type = proto_payload.get('@type', '')
            authentication_info = json.dumps(proto_payload.get('authenticationInfo', {}))
            
            # Ensure authorization_info is an array of JSON objects
            authorization_info = proto_payload.get('authorizationInfo', [])
            if isinstance(authorization_info, dict):
                authorization_info = [authorization_info]
            authorization_info = [json.dumps(info) for info in authorization_info]  # Keep as list of strings

            method_name = proto_payload.get('methodName', '')
            request = json.dumps(proto_payload.get('request', {}))
            request_metadata = json.dumps(proto_payload.get('requestMetadata', {}))
            resource_name = proto_payload.get('resourceName', '')
            service_name = proto_payload.get('serviceName', '')
            status = json.dumps(proto_payload.get('status', {}))
            principal_email = proto_payload.get('authenticationInfo', {}).get('principalEmail', '')

            # Execute SQL query
            await conn.execute("""
                INSERT INTO audit_logs (insert_id, log_name, audit_type, authentication_info, authorization_info, 
                method_name, request, request_metadata, resource_name, service_name, status, principal_email) 
                VALUES ($1, $2, $3, $4, $5::jsonb[], $6, $7, $8, $9, $10, $11, $12)
                """,
                insert_id, log_name, audit_type, authentication_info, authorization_info,
                method_name, request, request_metadata, resource_name, service_name, status, principal_email
            )
    except Exception as e:
        print(f"An error occurred: {e}")
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
        logging.info("Received a file upload request")

        if 'file' not in request.files:
            logging.warning('No file part in the request')
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            logging.warning('No selected file')
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            data = json.load(file)
            logging.info(f"Data read from file {filename}: {data}")  # Log data read from file

            try:
                await insert_data_into_db(data)
                logging.info(f"File {filename} processed successfully")
            except Exception as e:
                logging.error(f"Error processing file {filename}: {e}")
                flash(f"Error processing file: {e}")

            return redirect(url_for('dashboard'))
        else:
            logging.warning(f"File {file.filename} is not allowed")
            flash('File type not allowed')
    else:
        return render_template('upload_json.html')


# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Set maximum file upload size to 10MB
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

# # Test data insertion manually
# @app.route('/test_insert')
# async def test_insert():
#     test_data = [
#         {
#             "insertId": "testInsertId",
#             "logName": "testLogName",
#             "protoPayload": {
#                 "@type": "type.googleapis.com/testType",
#                 "authenticationInfo": {"principalEmail": "test@email.com"},
#                 "methodName": "testMethod",
#                 "request": {},
#                 "requestMetadata": {},
#                 "resourceName": "testResource",
#                 "serviceName": "testService",
#                 "status": {}
#             }
#         }
#     ]
#     await insert_data_into_db(test_data)
#     return "Test data insertion attempted"
if __name__ == '__main__':
    app.run(debug=True)
