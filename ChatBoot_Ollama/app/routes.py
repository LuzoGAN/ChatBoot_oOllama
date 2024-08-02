from flask import render_template_string, session
from flask_socketio import join_room, leave_room
from app import app, socketio
from models.documents import get_response_from_model
import uuid

@app.route('/')
def index():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    user_id = session['user_id']
    return render_template_string(open('app/templates/index.html').read(), user_id=user_id)

@socketio.on('send_message', namespace='/chat')
def handle_send_message(json):
    content = json['content']
    user_id = json['user_id']
    get_response_from_model(content, user_id)

@socketio.on('join', namespace='/chat')
def on_join(data):
    user_id = data['user_id']
    join_room(user_id)
    print(f'User {user_id} has joined the room')

@socketio.on('disconnect', namespace='/chat')
def on_disconnect():
    user_id = session.get('user_id')
    if user_id:
        leave_room(user_id)
        print(f'User {user_id} has left the room')
