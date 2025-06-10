# ====== 导入依赖 ======
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from datetime import timedelta

# ====== 导入本项目模块 ======
from models import db,User, Message  # noqa: F401
from routes import register_routes
from sockets import register_sockets

# ====== 初始化 Flask 应用 ======
app = Flask(__name__, static_folder="static")
app.permanent_session_lifetime = timedelta(days=30)  # Session 保留时间：30 天

# ====== Flask 配置项 ======
app.config["SECRET_KEY"] = "your-secret-key"  # 加密密钥
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"  # 数据库路径
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # 禁用事件系统提升性能
CORS(app, supports_credentials=True) # CORS 跨域配置 & SocketIO 初始化（使用 eventlet）

# ====== socketIO 配置项 ======
socketio = SocketIO(
    app, cors_allowed_origins="*", async_mode="eventlet", manage_session=True
)
register_sockets(socketio)

# ====== 数据库 配置项 ======
db.init_app(app)
with app.app_context():
    db.create_all()

# ====== HTTP路由 配置项 ======
register_routes(app)

# ====== 启动应用 ======
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
