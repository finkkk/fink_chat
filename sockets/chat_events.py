# sockets/chat_events.py
from flask import request
from flask_socketio import emit
from datetime import datetime, timezone
from models import db, Message, Poll, User, Vote
from config import SYSTEM_USERNAME
from commands import handle_command
from routes.view import get_user_role
from session_state import user_sid_map, online_users
from json.decoder import JSONDecodeError
import json


def get_user_info(username):
    return {"username": username, "role": get_user_role(username)}


def register_chat_events(socketio):
    def send_system_message(text):
        socketio.emit(
            "receive_message",
            {
                "username": "a",
                "message": text,
                "role": "system",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    @socketio.on("connect")
    def handle_connect():
        print(f"Socket 连接建立: {request.sid}")
        messages = Message.query.order_by(Message.timestamp.desc()).limit(30).all()
        messages.reverse()
        history = [build_message_payload(m, request.sid) for m in messages]
        socketio.emit("chat_history", history, room=request.sid)

    @socketio.on("load_more_history")
    def handle_load_more(data):
        before = data.get("before")
        limit = int(data.get("limit", 10))
        query = Message.query.order_by(Message.timestamp.desc())
        if before:
            try:
                before_dt = datetime.fromisoformat(before)
                query = query.filter(Message.timestamp < before_dt)
            except Exception as e:
                print("时间解析失败：", e)
        messages = query.limit(limit).all()
        messages.reverse()
        result = [build_message_payload(m, request.sid) for m in messages]
        socketio.emit("chat_history", result, room=request.sid)

    @socketio.on("bind_username")
    def bind_username(data):
        username = data.get("username")
        if username:
            user_sid_map[request.sid] = username
            online_users.add(username)
            print(f"绑定用户: {username} <==> {request.sid}")
            socketio.emit("online_users", [get_user_info(u) for u in online_users])

    @socketio.on("disconnect")
    def handle_disconnect():
        username = user_sid_map.pop(request.sid, None)
        if username and username in online_users:
            online_users.remove(username)
            socketio.emit("online_users", [get_user_info(u) for u in online_users])
        print(f"断开连接: {request.sid} 用户: {username}")

    @socketio.on("send_message")
    def handle_send(data):
        username = user_sid_map.get(request.sid, "匿名用户")
        role = get_user_role(username)

        if role == "guest":
            socketio.emit(
                "receive_message",
                {
                    "username": SYSTEM_USERNAME,
                    "message": "⚠️ 游客无法发送消息，请注册登录。",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
                room=request.sid,
            )
            return

        message = data.get("message", "").strip()
        if not message:
            return

        if message.startswith("/ask"):
            msg_obj = Message(username=username, message=message, role=role)
            db.session.add(msg_obj)
            db.session.commit()
            socketio.emit(
                "receive_message",
                {
                    "username": username,
                    "message": message,
                    "timestamp": msg_obj.timestamp.isoformat(),
                    "role": role,
                },
            )

        if message.startswith("/"):
            parts = message.split()
            command = parts[0]
            args = parts[1:]
            result = handle_command(command, args, username, role=role)
            result["role"] = "system"
            result["timestamp"] = datetime.now(timezone.utc).isoformat()
            if result.get("save"):
                msg_obj = Message(
                    username=SYSTEM_USERNAME, message=result["message"], role="system"
                )
                db.session.add(msg_obj)
                db.session.commit()
                result["timestamp"] = msg_obj.timestamp.isoformat()
            else:
                result.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
            if result.get("broadcast"):
                socketio.emit("receive_message", result)
            else:
                socketio.emit("receive_message", result, room=request.sid)
            return

        msg_obj = Message(
            username=username,
            message=message,
            role=role,
            timestamp=datetime.now(timezone.utc),
        )
        db.session.add(msg_obj)
        db.session.commit()
        socketio.emit(
            "receive_message",
            {
                "username": username,
                "message": message,
                "timestamp": msg_obj.timestamp.isoformat(),
                "role": role,
            },
        )


def build_message_payload(m, sid):
    if m.role == "poll_broadcast":
        try:
            payload = json.loads(m.message)
        except JSONDecodeError:
            payload = {"question": m.message, "creator": "未知", "poll_id": None}
        poll = Poll.query.get(payload.get("poll_id"))
        ended = poll.is_ended if poll else False
        username = user_sid_map.get(sid)
        user = User.query.filter_by(username=username).first() if username else None
        user_voted = (
            Vote.query.filter_by(poll_id=poll.id, user_id=user.id).first() is not None
            if user and poll
            else False
        )
        return {
            "username": m.username,
            "role": m.role,
            "message": payload.get("question", ""),
            "creator": payload.get("creator", "未知"),
            "poll_id": payload.get("poll_id"),
            "ended": ended,
            "user_voted": user_voted,
            "timestamp": m.timestamp.isoformat(),
        }
    return {
        "username": m.username,
        "message": m.message,
        "timestamp": m.timestamp.isoformat(),
        "role": m.role or get_user_role(m.username),
    }
