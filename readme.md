<p align="center">
  <img src="https://user-images.githubusercontent.com/xxx/xxx.png" width="120" alt="logo">
</p>

<h1 align="center">fas-rs</h1>
<p align="center">Frame aware scheduling for android</p>

<p align="center">
  <a href="#readme"><img src="https://img.shields.io/badge/README-%F0%9F%93%9A-blue?style=flat-square"></a>
  <img src="https://img.shields.io/badge/ENGLISH-blue?style=flat-square">
  <img src="https://img.shields.io/github/stars/yourname/fas-rs?style=flat-square">
  <img src="https://img.shields.io/github/workflow/status/yourname/fas-rs/CI?label=CI%20BUILD&style=flat-square">
  <img src="https://img.shields.io/badge/Release-v4.9.0-blue?style=flat-square">
  <img src="https://img.shields.io/badge/Downloads-121K-brightgreen?style=flat-square">
  <a href="https://t.me/your_telegram_group"><img src="https://img.shields.io/badge/Telegram-GROUP-blue?style=flat-square&logo=telegram"></a>
</p>

# Flask 聊天网站项目

这是一个基于 Flask + Flask-SocketIO 构建的简易实时聊天网站，支持用户注册、登录、保持会话状态以及多人聊天功能。前后端通过 WebSocket 实现实时通信，使用 SQLite 存储用户和消息数据。

---

## 🔧 项目功能

- 用户注册 / 登录 / 退出
- 登录状态保持（基于 Flask Session）
- 聊天页面展示欢迎语、历史消息加载
- 实时多人消息广播（Socket.IO）
- 消息持久化到 SQLite 数据库
- 用户数据加密
- 支持自动登录和记住密码
- 简洁前端界面（纯 HTML + JS）
- PWA支持

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

---

## 🔧 部署脚本说明

- 本项目附带一个通用部署脚本 deploy.sh，用于在服务器或本地快速执行：

- 自动拉取最新 GitHub 代码
- 自动安装依赖(只安装新增依赖)
- 提示您重启服务(此处需要您自行添加重启指令)
- 示例使用：

```bash
./deploy.sh
```

- ⚠️ 注意：deploy.sh 不包含 sudo 或自动重启服务，请手动执行以下指令：

```bash
sudo supervisorctl restart fink_chat
```

---

## 🛡️ 私人部署脚本建议

- 如果你在服务器中希望自动完成所有操作（如自动重启、使用 sudo），建议创建自己的部署脚本：

```bash
cp deploy.sh deploy-server.sh
```

- PS:该脚本(deploy-server.sh)已在.gitignore 中添加忽略，这样你服务器上的 deploy-server.sh 将不会被 Git 管理，不会被公开上传至GitHub，也不会在 git pull 时被覆盖，保护私人部署安全。
- 创建完毕deploy-server.sh脚本后请记得在末尾手动加上重启指令(以supervisorctl为例)：

```bash
sudo supervisorctl restart fink_chat
```

- 示例使用：

```bash
./deploy-server.sh
```
---
