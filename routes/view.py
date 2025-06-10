# routes/view.py
from flask import Blueprint, render_template, session, redirect

from config import APP_VERSION, APP_UPDATED
from utils.auth_helper import get_user_role

view_bp = Blueprint('view', __name__)


# ====== 登录注册页 ======
@view_bp.route("/")
def index():
    # 首页：登录/注册界面
    return render_template("index.html", version=APP_VERSION, updated=APP_UPDATED)


# ====== 用户主页 ======
@view_bp.route("/home")
def user_page():
    if "username" not in session:
        return redirect("/")
    username = session["username"]
    role = get_user_role(username)
    return render_template(
        "home.html",
        username=username,
        version=APP_VERSION,
        updated=APP_UPDATED,
        role=role,
    )  # 带上身份
