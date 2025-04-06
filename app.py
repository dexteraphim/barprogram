import webview
import threading
import os
from flask import Flask, render_template
from extensions import db
from models import Member

app = Flask(__name__, static_folder = 'static', template_folder = 'templates', instance_path = r'C:\Users\Bar\Desktop\Barprogram')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)

with app.app_context():
    db.create_all()

def start_flask():
    app.run(debug=False, port=5000)

@app.route('/')
def transactions():
    members = Member.query.all()
    return render_template('transactions.html', members=members)

@app.route('/members')
def members():
    return render_template('members.html')
    
if __name__ == '__main__':
    threading.Thread(target=start_flask, daemon=True).start()
    webview.create_window("Barprogram", "http://127.0.0.1:5000")
    webview.start()