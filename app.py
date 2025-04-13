from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import threading
import time

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ventify.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model for Messages
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Create Database
with app.app_context():
    db.create_all()

# Home Route
@app.route('/')
def home():
    return render_template('index.html')

# API to Get Messages (only last 2 minutes)
@app.route('/get_messages')
def get_messages():
    two_minutes_ago = datetime.utcnow() - timedelta(minutes=2)
    messages = Message.query.filter(Message.timestamp > two_minutes_ago).all()
    return jsonify([{"content": msg.content} for msg in messages])


# API to Post Message
@app.route('/post_message', methods=['POST'])
def post_message():
    content = request.json.get("content")
    if content:
        new_msg = Message(content=content)
        db.session.add(new_msg)
        db.session.commit()
    return jsonify({"success": True})

# Background Task to Delete Messages Older than 2 Minutes
def delete_old_messages():
    while True:
        with app.app_context():
            two_minutes_ago = datetime.utcnow() - timedelta(minutes=2)
            Message.query.filter(Message.timestamp < two_minutes_ago).delete()
            db.session.commit()
        time.sleep(600)  # Run every 2 minutes

# Run the background task
threading.Thread(target=delete_old_messages, daemon=True).start()

if __name__ == '__main__':
    app.run(debug=True)