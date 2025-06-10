# sockets/__init__.py
from .chat_events import register_chat_events

def register_sockets(socketio):
    register_chat_events(socketio)