from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import asyncpg
from aiohttp import web
from aiohttp.web import Response, Request
from aiohttp.client import ClientSession
import aiohttp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://davoberi:1234@localhost/davoberi'
db = SQLAlchemy(app)

# class LogEntry(db.Model):
#     __tablename__ = 'audit_logs'
#     insert_id = db.Column(db.String(255), primary_key=True)
#     log_name = db.Column(db.String(255))
#     audit_type = db.Column(db.String(255))
#     # authentication_info = db.Column(db.JSONB)
#     principal_email = db.Column(db.String(255))
#     service_name = db.Column(db.String(255))
#     method_name = db.Column(db.String(255))
#     # request_metadata = db.Column(db.JSONB)
#     # status = db.Column(db.JSONB)


# route to fetch data for D3.js
@app.route('/fetch_data_for_d3')
def fetch_data_for_d3():
    return True
    # Query database for log entries
    # logs = LogEntry.query.all()

    # return jsonify(data)

# home route where I render the template
@app.route('/')
def home():
    return render_template('index.html')

async def fetch_data_for_d3(request: Request):
    url = 'http://127.0.0.1:5000/fetch_data_for_d3'  
    async with ClientSession() as session:
        async with session.get(url) as response:
            data_content = await response.json()
            return jsonify(data_content)

@app.route('/fetch_data_for_d3')
def fetch_data():
    return jsonify([
        {"timestamp": "2023-01-01T12:00:00", "message": "Log message 1", "value": 10},
        {"timestamp": "2023-01-01T12:15:00", "message": "Log message 2", "value": 20},
        {"timestamp": "2023-01-01T12:30:00", "message": "Log message 3", "value": 15},
    ])

if __name__ == '__main__':
    app.run(debug=True)
