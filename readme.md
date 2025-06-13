<p align="center">
  <img src="static/assets/img/logo.webp" width="120" alt="logo">
</p>

<h1 align="center">Fink-chat</h1>
<p align="center">Flask 框架下的简易聊天网站</p>

<p align="center">
  <img src="https://img.shields.io/badge/文档-📘-blue?style=flat-square">
  <img src="https://img.shields.io/badge/语言-中文-blue?style=flat-square">
  <img src="https://img.shields.io/github/stars/finkkk/fink_chat?style=flat-square">
  <img src="https://img.shields.io/github/v/release/finkkk/fink_chat?label=release&style=flat-square&cacheSeconds=60">
</p>

# Flask 聊天网站项目

这是一个基于 Flask + Flask-SocketIO 构建的简易实时聊天网站，支持用户注册、登录、保持会话状态以及多人聊天功能。前后端通过 WebSocket 实现实时通信，使用 SQLite 存储用户和消息数据。

---

## 🔧 项目功能概览

### ✅ 用户系统
- 用户注册 / 登录 / 退出
- 登录状态保持（基于 Flask Session）
- 自动登录、记住密码（localStorage）

### 💬 聊天系统
- 实时多人消息广播（Flask-SocketIO）
- 历史消息加载（最近消息 + 分页加载更多）
- 消息持久化到 SQLite 数据库
- 用户 @功能（支持点击用户名快速 @）
- 被 @ 时高亮并播放提示音
- 游客登录模式（只读聊天内容，禁用功能）
- 聊天界面欢迎语、时间提示、消息时间戳

### 🧰 工具与指令
- 工具栏快捷指令入口（投票、掷骰子、查时间）
- 自定义指令系统（如 `/ask` `/ai` `/help`）
- 模块化指令编写（每个指令文件独立）
- 指令鉴权系统：按用户身份分配权限
- AI 指令思考中动画、限频、卡片提示等 UX 设计

### 📢 公告与在线用户
- 浮窗公告栏（动态内容支持 JSON 配置）
- 公告状态保存（本地已读状态）
- 实时在线用户列表动态更新（去重、展示昵称）

### 🔒 用户权限控制
- 游客禁止发言、禁用工具栏、无法查看投票详情
- 用户身份识别（admin / user / guest）
- 消息身份标识 + 角色前缀渲染

### 📊 投票系统（模块化支持）
- 支持发起投票、投票、查看结果
- 每人仅能投一票，禁止重复投票
- 实时投票同步更新（广播机制）
- 投票详情弹窗显示进度条、票数、状态判断
- 系统消息广播新投票事件 + 投票结果更新卡片

### 🌐 前端体验
- 纯 HTML + JS 构建，无前端框架依赖
- 聊天消息滑入动画
- 投票状态实时刷新
- 消息输入框支持指令卡片提示（如 `/ask`）
- 支持 PWA 安装（离线访问、缓存图标）
- 页面响应式适配（移动端、桌面端）

### 📈 其他功能
- Google Analytics 站点访问统计
- 聊天室时间查询 `/time`
- 自定义用户欢迎语
- 客户端弹出式提醒（showAlert）
---

## 🛠 技术栈

| 层级        | 技术                      |
|-------------|---------------------------|
| 后端        | Python 3.x, Flask         |
| 实时通信    | Flask-SocketIO, Eventlet  |
| 数据库      | SQLite, Flask-SQLAlchemy  |
| API支持     | Flask-CORS                |
| 模板引擎    | Jinja2                    |
| 前端        | HTML / CSS / JavaScript   |
| 前端通信    | Socket.IO.js              |
| 本地存储    | localStorage              |
| 安装体验    | PWA（Progressive Web App）|
| 分析统计    | Google Analytics          |

---

## 📂 项目适用场景

- 在线聊天室 / 班级群 / 内网讨论系统
- 简洁可控的投票系统
- 实时广播 & WebSocket 教学演示项目
- Flask 全栈开发学习项目

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
