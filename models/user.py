# models/user.py
from . import db

# 定义用户信息数据库
class User(db.Model):
    # 用户表：存储用户名和密码哈希
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)