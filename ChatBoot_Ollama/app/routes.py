from flask import render_template_string
from app import app, socketio
from models.documents import get_response_from_model

@app.route('/')
def index():
    return render_template_string(open('app/templates/index.html').read())

@socketio.on('send_message')
def handle_send_message(json):
    content = json['content']
    get_response_from_model(content)
