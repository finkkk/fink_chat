# ====== 导入依赖 ======
from flask import Flask, request, jsonify, session, redirect, url_for, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from config import APP_VERSION, APP_UPDATED, GUEST_USERNAME, ADMIN_USERNAMES, SUPER_ADMIN_USERNAMES
import json


# ====== 初始化 Flask 应用 ======
app = Flask(__name__,static_folder='static')
app.permanent_session_lifetime = timedelta(days=30) # Session 保留时间：30 天

# Flask 配置项
app.config['SECRET_KEY'] = 'your-secret-key' # 加密密钥 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db' # 数据库路径
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # 禁用事件系统提升性能

# CORS 跨域配置 & SocketIO 初始化（使用 eventlet）
CORS(app, supports_credentials=True)
# 使用 eventlet，开发和部署都一样
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet', manage_session=True)
db = SQLAlchemy(app)


# ====== 数据模型定义 ======
class User(db.Model):
    # 用户表：存储用户名和密码哈希
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

class Message(db.Model):
    # 消息表：存储聊天记录
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# ====== 初始化数据库 ======
with app.app_context():
    db.create_all()


# ====== 注册接口 ======
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'error': '用户名已存在'}), 400
    hashed = generate_password_hash(password)
    db.session.add(User(username=username, password_hash=hashed))
    db.session.commit()
    return jsonify({'success': True, 'message': '注册成功'})


# ====== 登录接口 ======
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'success': False, 'error': '用户名或密码错误'}), 400
    session['username'] = username
    session.permanent = True  
    return jsonify({'success': True, 'message': '登录成功', 'username': username})


# ====== 游客登录接口 ======
@app.route('/guest-login')
def guest_login():
    # 游客模式登录
    session['username'] = GUEST_USERNAME
    session.permanent = True
    return redirect('/home')


# ====== 验证权限并分配身份 ======
def get_user_role(username):
    if username == GUEST_USERNAME:
        return "guest"
    elif username in SUPER_ADMIN_USERNAMES:
        return "super_admin"
    elif username in ADMIN_USERNAMES:
        return "admin"
    else:
        return "user"


# ====== 用户主页 ======
@app.route('/home')
def user_page():
    if 'username' not in session:
        return redirect('/')
    username = session['username']
    role = get_user_role(username)  
    return render_template('home.html',
                           username=username,
                           version=APP_VERSION,
                           updated=APP_UPDATED,
                           role=role)  # 带上身份


# ====== 退出登录 ======
@app.route('/logout')
def logout():
    # 清除 session 退出登录
    session.pop('username', None)
    return redirect('/')


# ====== 登录注册页 ======
@app.route('/')
def index():
    # 首页：登录/注册界面
    return render_template('index.html', version=APP_VERSION, updated=APP_UPDATED)


# ====== Socket.IO 聊天逻辑 ======
# 保存 socket.id 与用户名的映射
user_sid_map = {}
# 实时在线用户列表
online_users = set()
# 获取用户身份的方法
def get_user_info(username):
    return {
        "username": username,
        "role": get_user_role(username)
    }
# 连接逻辑
@socketio.on('connect')
def handle_connect():
    # 新连接时发送最近 50 条消息
    print(f"Socket 连接建立: {request.sid}")
    messages = Message.query.order_by(Message.timestamp.desc()).limit(50).all()
    messages = reversed(messages)  # 先倒序再恢复正序
    history = [{
        'username': m.username,
        'message': m.message,
        'timestamp': m.timestamp.isoformat(),
        'role': get_user_role(m.username)  
    } for m in messages]
    emit('chat_history', history)
# 加载更多历史记录信息
@socketio.on('load_more_history')
def handle_load_more(data):
    # 加载更多历史消息（分页）
    offset = int(data.get('offset', 0))
    limit = int(data.get('limit', 10))
    messages = Message.query.order_by(Message.timestamp.desc()).offset(offset).limit(limit).all()
    messages = reversed(messages)  # 倒序显示
    result = [{
        'username': m.username,
        'message': m.message,
        'timestamp': m.timestamp.isoformat(),
        'role': get_user_role(m.username) 
    } for m in messages]
    emit('chat_history', result)
# 绑定/传输用户名数据
@socketio.on('bind_username')
def bind_username(data):
    username = data.get('username')
    if username:
        user_sid_map[request.sid] = username
        online_users.add(username)
        print(f'绑定用户: {username} <==> {request.sid}')
        emit('online_users', [get_user_info(u) for u in online_users], broadcast=True)

# 断连逻辑
@socketio.on('disconnect')
def handle_disconnect():
    username = user_sid_map.pop(request.sid, None)
    if username and username in online_users:
        online_users.remove(username)
        emit('online_users', [get_user_info(u) for u in online_users], broadcast=True)
    print(f"断开连接: {request.sid} 用户: {username}")
# 发送信息逻辑
@socketio.on('send_message')
def handle_send(data):
    # 处理用户发送的消息并广播
    username = user_sid_map.get(request.sid, '匿名用户')

    # 如果是游客，不能发消息
    if get_user_role(username) == "guest":
        emit('receive_message', {
            'username': '系统',
            'message': '⚠️ 游客无法发送消息，请注册登录。',
            'timestamp': datetime.utcnow().isoformat()
        }, room=request.sid)
        return

    message = data.get('message', '').strip()
    if not message:
        return

    # 存储消息
    msg_obj = Message(username=username, message=message)
    db.session.add(msg_obj)
    db.session.commit()

    # 广播消息
    emit('receive_message', {
        'username': username,
        'message': message,
        'timestamp': msg_obj.timestamp.isoformat(),
        'role': get_user_role(username)  # 加上这行
}, broadcast=True)


# ====== 所有用户名列表（用于 @ 高亮） ======
@app.route("/usernames")
def get_all_usernames():
    users = User.query.with_entities(User.username).all()
    return jsonify([u.username for u in users])


# ====== 弹出公告栏 逻辑 ======
@app.route("/announcement")
def get_announcement():
    # 读取 announcement.json 内容并返回
    try:
        with open("announcement.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": "公告读取失败", "details": str(e)}), 500


# ====== SEO 文件服务 ======
@app.route("/robots.txt")
def robots():
    return app.send_static_file("robots.txt")

@app.route("/sitemap.xml")
def sitemap():
    return app.send_static_file("sitemap.xml")


# ====== 启动应用 ======
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)

