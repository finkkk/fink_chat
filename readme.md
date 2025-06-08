# Flask 聊天网站项目

这是一个基于 Flask + Flask-SocketIO 构建的简易实时聊天网站，支持用户注册、登录、保持会话状态以及多人聊天功能。前后端通过 WebSocket 实现实时通信，使用 SQLite 存储用户和消息数据。

---

## 🔧 项目功能

- 用户注册 / 登录 / 退出
- 登录状态保持（基于 Flask Session）
- 聊天页面展示欢迎语、历史消息加载
- 实时多人消息广播（Socket.IO）
- 消息持久化到 SQLite 数据库
- 简洁前端界面（纯 HTML + JS）

---

## 🛠 技术栈

- Python 3.x
- Flask
- Flask-SocketIO
- Flask-SQLAlchemy
- Flask-CORS
- SQLite（用户和聊天记录存储）

---

## 🚀 如何运行

### 1. 克隆项目

```bash
git clone https://github.com/finkkk/fink_chat.git
cd fink_chat
```

### 2. 创建虚拟环境（推荐）

```bash
python -m venv venv
```

激活虚拟环境：

Windows：

```bash
venv\Scripts\activate
```

macOS / Linux：

```bash
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 启动项目（开发模式）

```bash
python app.py
```

你应该会看到输出：

 * Running on http://0.0.0.0:5000/

### 5. 打开浏览器访问

http://localhost:5000

你将看到登录注册界面。注册一个用户后进入聊天室，即可实时通信。

---

## 📌 注意事项

- 首次运行会自动创建 SQLite 数据库：instance/users.db
- 前端 Socket 地址请使用 io({ withCredentials: true }) 自动匹配当前服务器
- 推荐开发时使用：

```bash
debug=True, use_reloader=False
async_mode='threading'
```

- 请勿在生产环境下使用 debug=True
- .gitignore 已忽略虚拟环境、数据库和缓存文件