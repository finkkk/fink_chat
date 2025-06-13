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


# 获取用户身份的方法
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

    # 连接逻辑
    @socketio.on("connect")
    def handle_connect():
        print(f"Socket 连接建立: {request.sid}")
        messages = (
            Message.query.order_by(Message.timestamp.asc()).limit(50).all()
        )  #  升序

        history = []
        for m in messages:
            if m.role == "poll_broadcast":
                try:
                    payload = json.loads(m.message)
                except JSONDecodeError:
                    payload = {
                        "question": m.message,
                        "creator": "未知",
                        "poll_id": None,
                    }

                # 加入投票状态信息（如果 poll_id 合法）
                poll = Poll.query.get(payload.get("poll_id"))
                ended = poll.is_ended if poll else False

                # 获取当前用户名（从 request.sid 对应 user_sid_map）
                username = user_sid_map.get(request.sid)
                user = (
                    User.query.filter_by(username=username).first()
                    if username
                    else None
                )
                user_voted = False
                if user and poll:
                    user_voted = (
                        Vote.query.filter_by(poll_id=poll.id, user_id=user.id).first()
                        is not None
                    )

                history.append(
                    {
                        "username": m.username,
                        "role": m.role,
                        "message": payload.get("message", ""),
                        "creator": payload.get("creator", "未知"),
                        "poll_id": payload.get("poll_id"),
                        "ended": ended,
                        "user_voted": user_voted,
                        "timestamp": m.timestamp.isoformat(),
                    }
                )
            else:
                history.append(
                    {
                        "username": m.username,
                        "message": m.message,
                        "timestamp": m.timestamp.isoformat(),
                        "role": m.role or get_user_role(m.username),
                    }
                )

        emit("chat_history", history)

    # 加载更多历史记录信息
    @socketio.on("load_more_history")
    def handle_load_more(data):
        offset = int(data.get("offset", 0))
        limit = int(data.get("limit", 10))

        messages = (
            Message.query.order_by(Message.timestamp.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )  #  保留升序 + 正常分页

        result = []
        for m in messages:
            if m.role == "poll_broadcast":
                try:
                    payload = json.loads(m.message)
                except JSONDecodeError:
                    payload = {
                        "question": m.message,
                        "creator": "未知",
                        "poll_id": None,
                    }

                # 加入投票状态信息（如果 poll_id 合法）
                poll = Poll.query.get(payload.get("poll_id"))
                ended = poll.is_ended if poll else False

                # 获取当前用户名（从 request.sid 对应 user_sid_map）
                username = user_sid_map.get(request.sid)
                user = (
                    User.query.filter_by(username=username).first()
                    if username
                    else None
                )
                user_voted = False
                if user and poll:
                    user_voted = (
                        Vote.query.filter_by(poll_id=poll.id, user_id=user.id).first()
                        is not None
                    )

                result.append(
                    {
                        "username": m.username,
                        "role": m.role,
                        "message": payload.get("question", ""),
                        "creator": payload.get("creator", "未知"),
                        "poll_id": payload.get("poll_id"),
                        "ended": ended,
                        "user_voted": user_voted,
                        "timestamp": m.timestamp.isoformat(),
                    }
                )
            else:
                result.append(
                    {
                        "username": m.username,
                        "message": m.message,
                        "timestamp": m.timestamp.isoformat(),
                        "role": m.role or get_user_role(m.username),
                    }
                )

        emit("chat_history", result)

    # 绑定/传输用户名数据
    @socketio.on("bind_username")
    def bind_username(data):
        username = data.get("username")
        if username:
            user_sid_map[request.sid] = username
            online_users.add(username)
            print(f"绑定用户: {username} <==> {request.sid}")
            emit(
                "online_users", [get_user_info(u) for u in online_users], broadcast=True
            )

    # 断连逻辑
    @socketio.on("disconnect")
    def handle_disconnect():
        username = user_sid_map.pop(request.sid, None)
        if username and username in online_users:
            online_users.remove(username)
            emit(
                "online_users", [get_user_info(u) for u in online_users], broadcast=True
            )
        print(f"断开连接: {request.sid} 用户: {username}")

    # 发送消息逻辑
    @socketio.on("send_message")
    def handle_send(data):
        username = user_sid_map.get(request.sid, "匿名用户")
        role = get_user_role(username)

        # 游客不能发言
        if role == "guest":
            emit(
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

        # ===== AI指令特殊处理 =====
        if message.startswith("/ask"):
            # 保存并广播用户原始指令
            msg_obj = Message(username=username, message=message, role=role)
            db.session.add(msg_obj)
            db.session.commit()
            emit(
                "receive_message",
                {
                    "username": username,
                    "message": message,
                    "timestamp": msg_obj.timestamp.isoformat(),
                    "role": role,
                },
                broadcast=True,
            )

        # ===== 判断是否是指令 =====
        if message.startswith("/"):
            parts = message.split()
            command = parts[0]
            args = parts[1:]

            # 执行指令
            result = handle_command(command, args, username, role=role)
            result["role"] = "system"
            result["timestamp"] = datetime.now(timezone.utc).isoformat()

            # 保存到数据库
            if result.get("save"):
                msg_obj = Message(
                    username=SYSTEM_USERNAME, message=result["message"], role="system"
                )
                db.session.add(msg_obj)
                db.session.commit()
                result["timestamp"] = msg_obj.timestamp.isoformat()
            else:
                # 没保存的也统一加 timestamp（兜底）
                result.setdefault("timestamp", datetime.now(timezone.utc).isoformat())

            # 广播 or 回给自己
            if result.get("broadcast"):
                emit("receive_message", result, broadcast=True)
            else:
                emit("receive_message", result, room=request.sid)
            return

        # ===== 普通消息处理 =====
        msg_obj = Message(
            username=username,
            message=message,
            role=role,
            timestamp=datetime.now(timezone.utc),  #  每次生成新的时间戳
        )
        db.session.add(msg_obj)
        db.session.commit()
        emit(
            "receive_message",
            {
                "username": username,
                "message": message,
                "timestamp": msg_obj.timestamp.isoformat(),
                "role": role,
            },
            broadcast=True,
        )
