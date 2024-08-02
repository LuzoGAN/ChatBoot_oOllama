from flask import Flask
from flask_socketio import SocketIO
from flask_session import Session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'

# Initialize session
Session(app)

# Initialize SocketIO
socketio = SocketIO(app, manage_session=False)

from app import routes
