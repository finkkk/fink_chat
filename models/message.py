# models/message.py
from . import db
from datetime import datetime,timezone

class Message(db.Model):
    # 消息表：存储聊天记录
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    role = db.Column(db.String(32), default="user") 