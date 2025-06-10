# routes/system.py
from flask import Blueprint, jsonify
from models import User
import json
from commands import AVAILABLE_COMMANDS

system_bp = Blueprint('system', __name__)

# ====== 弹出公告栏 逻辑 ======
@system_bp.route("/announcement")
def get_announcement():
    # 读取 announcement.json 内容并返回
    try:
        with open("announcement.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": "公告读取失败", "details": str(e)}), 500


# ====== 所有用户名列表（用于 @ 高亮） ======
@system_bp.route("/usernames")
def get_all_usernames():
    users = User.query.with_entities(User.username).all()
    return jsonify([u.username for u in users])


# ====== 获取所有指令合集 ======
@system_bp.route("/commands")
def get_commands():
    return jsonify(list(AVAILABLE_COMMANDS.keys()))

