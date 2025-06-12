# routes/polls.py
from flask import Blueprint, request, jsonify, session
from models import db, Poll, Option, Vote,User

polls_bp = Blueprint("polls", __name__, url_prefix="/api/polls")


# 列表：公开接口
@polls_bp.route("", methods=["GET"])
def list_polls():
    polls = Poll.query.order_by(Poll.created_at.desc()).all()
    data = []
    for p in polls:
        total = sum(opt.votes for opt in p.options)
        data.append(
            {
                "poll_id": p.id,
                "question": p.question,
                "creator": p.creator,
                "created_at": p.created_at.isoformat(),
                "ended": p.is_ended,  # 动态计算
                "total_votes": total,
            }
        )
    return jsonify(data)


# 详情：公开接口
@polls_bp.route("/<int:poll_id>", methods=["GET"])
def get_poll(poll_id):
    p = Poll.query.get_or_404(poll_id)

    # —— 1. 查当前用户有没有投过这票 —— #
    username = session.get('username')
    user_voted = False
    if username:
        user = User.query.filter_by(username=username).first()
        if user and Vote.query.filter_by(poll_id=poll_id, user_id=user.id).first():
            user_voted = True


    opts = [{"option_id": o.id, "text": o.text, "votes": o.votes} for o in p.options]
    return jsonify(
        {
            "poll_id": p.id,
            "question": p.question,
            "creator": p.creator,
            "created_at": p.created_at.isoformat(),
            "ended": p.is_ended,
            'user_voted': user_voted,
            "total_votes": sum(o.votes for o in p.options),
            "options": opts,
        }
    ), 200


# 创建：检查 session 登录
@polls_bp.route("", methods=["POST"])
def create_poll():
    username = session.get("username")
    if not username:
        return jsonify({"error": "请先登录"}), 401

    js = request.get_json() or {}
    q = (js.get("question") or "").strip()
    opts = [o.strip() for o in js.get("options", []) if o.strip()]
    if not q or len(opts) < 2 or len(opts) > 6:
        return jsonify({"error": "标题非空，选项数量须在2~6之间"}), 400

    poll = Poll(question=q, creator=username)
    db.session.add(poll)
    db.session.flush()
    for txt in opts:
        db.session.add(Option(poll_id=poll.id, text=txt))
    db.session.commit()
    return jsonify({"poll_id": poll.id}), 201


# 投票：同样检查 session
@polls_bp.route("/<int:poll_id>/vote", methods=["POST"])
def vote_poll(poll_id):
    username = session.get("username")
    if not username:
        return jsonify({"error": "请先登录"}), 401

    js = request.get_json() or {}
    opt_id = js.get("option_id")
    p = Poll.query.get_or_404(poll_id)
    if p.is_ended:
        return jsonify({"error": "投票已结束"}), 400

    # 查找选项
    opt = Option.query.filter_by(id=opt_id, poll_id=poll_id).first_or_404()
    # 查重：假设 Vote 存储了 user_id，可先查 user 表获取 id
    from models import User

    user = User.query.filter_by(username=username).first()
    if Vote.query.filter_by(poll_id=poll_id, user_id=user.id).first():
        return jsonify({"error": "你已投过票"}), 400

    vote = Vote(poll_id=poll_id, user_id=user.id, option_idx=p.options.index(opt))
    db.session.add(vote)
    opt.votes += 1
    db.session.commit()
    return jsonify({"success": True}), 200
