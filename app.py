from flask import Flask, request, jsonify, session, redirect, url_for, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app, supports_credentials=True)
# 使用 eventlet，开发和部署都一样
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet', manage_session=True)
db = SQLAlchemy(app)

# ====== 数据模型 ======
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ====== 创建表 ======
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
    return jsonify({'success': True, 'message': '登录成功', 'username': username})

# ====== 用户主页 ======
@app.route('/home')
def user_page():
    if 'username' not in session:
        return redirect('/')
    return render_template('home.html', username=session['username'])

# ====== 退出登录 ======
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

# ====== 首页 ======
@app.route('/')
def index():
    return render_template('index.html')

# ====== Socket.IO 聊天逻辑 ======

# 保存 socket.id 与用户名的映射
user_sid_map = {}

@socketio.on('connect')
def handle_connect():
    print(f"Socket 连接建立: {request.sid}")
    messages = Message.query.order_by(Message.timestamp.desc()).limit(50).all()
    messages = reversed(messages)  # 先倒序再恢复正序
    history = [{'username': m.username, 'message': m.message} for m in messages]
    emit('chat_history', history)

@socketio.on('load_more_history')
def handle_load_more(data):
    offset = int(data.get('offset', 0))
    limit = int(data.get('limit', 10))
    messages = Message.query.order_by(Message.timestamp.desc()).offset(offset).limit(limit).all()
    messages = reversed(messages)  # 倒序显示
    result = [{'username': m.username, 'message': m.message} for m in messages]
    emit('chat_history', result)

@socketio.on('bind_username')
def bind_username(data):
    username = data.get('username')
    if username:
        user_sid_map[request.sid] = username
        print(f'绑定用户: {username} <==> {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    username = user_sid_map.pop(request.sid, None)
    print(f"断开连接: {request.sid} 用户: {username}")

@socketio.on('send_message')
def handle_send(data):
    username = user_sid_map.get(request.sid, '匿名用户')
    message = data.get('message', '').strip()
    if not message:
        return

    msg_obj = Message(username=username, message=message)
    db.session.add(msg_obj)
    db.session.commit()

    emit('receive_message', {'username': username, 'message': message}, broadcast=True)

# ====== 启动应用 ======
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)

