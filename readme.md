# Flask 聊天网站项目

这是一个基于 Flask + Flask-SocketIO 构建的简易实时聊天网站，支持用户注册、登录、保持会话状态以及多人聊天功能。前后端通过 WebSocket 实现实时通信，使用 SQLite 存储用户和消息数据。

## 🔧 项目功能

- 用户注册 / 登录 / 退出
- 登录状态保持（基于 Flask Session）
- 聊天页面展示欢迎语、历史消息加载
- 实时多人消息广播（Socket.IO）
- 消息持久化到 SQLite 数据库
- 简洁前端界面（纯 HTML + JS）

## 🛠 技术栈

- Python 3.x
- Flask
- Flask-SocketIO
- Flask-SQLAlchemy
- Flask-CORS
- SQLite（用户和聊天记录存储）

## 🚀 如何运行

### 1. 克隆项目

```bash
git clone https://github.com/finkkk/fink_chat.git
cd fink_chat
