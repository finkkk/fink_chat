# routes/auth.py
from flask import Blueprint, request, jsonify, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from config import GUEST_USERNAME

auth_bp = Blueprint("auth", __name__)


# ====== 注册接口 ======
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    if User.query.filter_by(username=username).first():
        return jsonify({"success": False, "error": "用户名已存在"}), 400
    hashed = generate_password_hash(password)
    db.session.add(User(username=username, password_hash=hashed))
    db.session.commit()
    return jsonify({"success": True, "message": "注册成功"})


# ====== 登录接口 ======
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"success": False, "error": "用户名或密码错误"}), 400
    session["username"] = username
    session.permanent = True
    return jsonify({"success": True, "message": "登录成功", "username": username})


# ====== 游客登录接口 ======
@auth_bp.route("/guest-login")
def guest_login():
    from app import user_sid_map

    # 获取当前在线的所有游客名
    all_online_guests = {
        name for name in user_sid_map.values() if name.startswith(GUEST_USERNAME)
    }
    # 找一个未使用的编号
    for i in range(1, 1000):
        guest_name = f"{GUEST_USERNAME}#{i}"
        if guest_name not in all_online_guests:
            session["username"] = guest_name
            session.permanent = True
            return redirect("/home")

    return "游客爆满，请稍后再试", 500


# ====== 退出登录 ======
@auth_bp.route("/logout")
def logout():
    # 清除 session 退出登录
    session.pop("username", None)
    return redirect("/")
