# sockets/poll_events.py
from models import Poll, Option, Message, db, User, Vote
from config import SYSTEM_USERNAME
from datetime import datetime, timezone
from flask_socketio import emit
from flask import request
from session_state import user_sid_map
import json


def register_poll_events(socketio):
    @socketio.on("create_poll")
    def handle_create_poll_socket(data):
        username = data.get("username")
        question = (data.get("question") or "").strip()
        if not question:
            emit("poll_create_result", {"error": "标题不能为空"}, room=request.sid)
            return
        options = [o.strip() for o in data.get("options", []) if o.strip()]

        if not username or not question or len(options) < 2:
            return

        # 创建投票和选项
        poll = Poll(question=question, creator=username)
        db.session.add(poll)
        db.session.flush()
        for txt in options:
            db.session.add(Option(poll_id=poll.id, text=txt))
        db.session.commit()

        now = datetime.now(timezone.utc)

        #  广播系统消息（附带 poll_id）
        socketio.emit(
            "receive_message",
            {
                "username": SYSTEM_USERNAME,
                "role": "poll_broadcast",
                "creator": username,
                "message": question,
                "poll_id": poll.id,
                "timestamp": now.isoformat(),
            },
        )

        #  存入数据库（可不含 poll_id，仅用于记录）
        db.session.add(
            Message(
                username=SYSTEM_USERNAME,
                message=json.dumps(
                    {
                        "creator": username,
                        "message": question,
                        "poll_id": poll.id,
                    }
                ),
                role="poll_broadcast",
                timestamp=now,
            )
        )
        db.session.commit()

        # 返回 poll_id 给发起人（可选）
        emit("poll_created", {"poll_id": poll.id})

    @socketio.on("list_polls")
    def handle_list_polls():
        username = user_sid_map.get(request.sid)
        user = User.query.filter_by(username=username).first() if username else None
        polls = Poll.query.order_by(Poll.created_at.desc()).all()
        data = []
        for p in polls:
            total = sum(opt.votes for opt in p.options)

            #  正确判断是否投票
            user_voted = False
            if user:
                user_voted = Vote.query.filter_by(poll_id=p.id, user_id=user.id).first() is not None

            data.append(
                {
                    "poll_id": p.id,
                    "message": p.question,
                    "creator": p.creator,
                    "user_voted": user_voted,
                    "created_at": p.created_at.isoformat(),
                    "total_votes": total,
                }
            )

        emit("poll_list_result", data, room=request.sid)

    @socketio.on("get_poll_detail")
    def handle_poll_detail(data):
        poll_id = data.get("poll_id")
        poll = Poll.query.get(poll_id)
        if not poll:
            emit("poll_detail_result", {"error": "投票不存在"}, room=request.sid)
            return
        


        username = user_sid_map.get(request.sid)
        user = User.query.filter_by(username=username).first() if username else None
        user_voted = False
        if user:
            user_voted = Vote.query.filter_by(poll_id=poll.id, user_id=user.id).first() is not None

        emit(
            "poll_detail_result",
            {
                "poll_id": poll.id,
                "message": poll.question,
                "creator": poll.creator,
                "created_at": poll.created_at.isoformat(),
                "user_voted": user_voted,
                "total_votes": sum(o.votes for o in poll.options),
                "options": [
                    {"text": o.text, "votes": o.votes, "option_id": o.id}
                    for o in poll.options
                ],
            },
            room=request.sid,
        )

    @socketio.on("vote_poll")
    def handle_vote_poll(data):
        poll_id = data.get("poll_id")
        option_id = data.get("option_id")

        username = user_sid_map.get(request.sid)
        if not username:
            emit("poll_vote_result", {"error": "未登录"}, room=request.sid)
            return

        poll = Poll.query.get(poll_id)
        if not poll:
            emit("poll_vote_result", {"error": "投票不存在"}, room=request.sid)
            return
        if poll.is_ended:
            emit("poll_vote_result", {"error": "投票已结束"}, room=request.sid)
            return

        opt = Option.query.filter_by(id=option_id, poll_id=poll_id).first()
        if not opt:
            emit("poll_vote_result", {"error": "选项不存在"}, room=request.sid)
            return

        user = User.query.filter_by(username=username).first()
        if not user:
            emit("poll_vote_result", {"error": "用户异常"}, room=request.sid)
            return
        if Vote.query.filter_by(poll_id=poll_id, user_id=user.id).first():
            emit("poll_vote_result", {"error": "你已投过票"}, room=request.sid)
            return

        vote = Vote(
            poll_id=poll_id, user_id=user.id, option_idx=poll.options.index(opt)
        )
        db.session.add(vote)
        opt.votes += 1
        db.session.commit()

        #  成功回调给前端，触发刷新等操作
        emit("poll_vote_result", {"success": True}, room=request.sid)
