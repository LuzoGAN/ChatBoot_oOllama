from flask_socketio import emit

def send_response_to_user(user_id: str, response_chunk: str):
    emit('response_chunk', {'data': response_chunk}, room=user_id)
