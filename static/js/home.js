//#region Google Analytics（谷歌分析）的代码，用于网站访问统计
window.dataLayer = window.dataLayer || [];
function gtag() {
  dataLayer.push(arguments);
}
gtag("js", new Date());

gtag("config", "G-ZK9F0GE4SE");
//#endregion

const knownUsernames = new Set(); // 所有已知用户名（用于判断 @谁 是否是有效用户）
let socket = null;
const username = document.getElementById("username").dataset.username;
const role = document.getElementById("username").dataset.role;
window.username = username;
window.userRole = role;
document.getElementById("display-username").textContent = username;
const chatBox = document.getElementById("chat-box");
const messageInput = document.getElementById("message");
const loadMoreBtn = document.getElementById("load-more");
let messageOffset = 0; // 当前历史消息加载偏移量
const limitPerLoad = 10; // 每次最多加载多少条历史记录
let validCommands = new Set(); // 可用指令合集

let thinkingMsgElement = null; // 保存正在思考的消息 DOM

// 渲染身份组样式(包括字体颜色和徽章添加)
function renderIdentity(el, role, isSelf = false) {
  const { color, badge } = getIdentityStyle(role, isSelf);
  el.style.color = color;
  if (badge) {
    const badgeEl = document.createElement("span");
    badgeEl.innerHTML = `<span style="font-size: 0.9em;">${badge}</span>`;
    badgeEl.style.marginLeft = "6px";
    badgeEl.style.lineHeight = "1";
    badgeEl.style.position = "relative";
    el.insertAdjacentElement("afterend", badgeEl);
  }
}
function getIdentityStyle(role, isSelf = false) {
  // 自己：固定绿色，但保留徽章
  if (isSelf) {
    const badgeMap = {
      super_admin: "👑",
      admin: "🎯",
      guest: "👤",
    };
    const badge = badgeMap[role] || "";
    return { color: "#10b981", badge };
  }

  // 其他人：正常身份样式
  if (role === "system") return { color: "purple", badge: "🪄" };
  if (role === "super_admin") return { color: "red", badge: "👑" };
  if (role === "admin") return { color: "orange", badge: "🎯" };
  if (role === "guest") return { color: "gray", badge: "👤" };

  return { color: "#3b82f6", badge: "" }; // 默认普通用户
}

// 插入 “AI思考中”
function insertThinkingMessage() {
  if (thinkingMsgElement) return; // 避免重复添加

  const tempData = {
    username: "系统",
    message: "正在思考中...",
    role: "system",
    timestamp: "",
    isAI: true, // 新增标记，与AI指令保持一致
    isThinking: true, // 思考中标记
  };

  const tempDiv = appendMessage(tempData);
  thinkingMsgElement = tempDiv;
}

// 初始化 Socket.IO 并设置事件监听
function initSocket() {
  socket = io({ withCredentials: true });

  // 处理连接逻辑
  socket.on("connect", () => {
    // 向后端绑定用户名和角色
    socket.emit("bind_username", {
      username: window.username,
      role: window.userRole,
    });
  });

  // 接收历史消息（首次或点击“加载更多”）
  socket.on("chat_history", (messages) => {
    if (!messages || messages.length === 0) {
      loadMoreBtn.disabled = true;
      loadMoreBtn.textContent = "没有更多消息";
      return;
    }

    messages.reverse().forEach((msg) => {
      
      appendMessage(msg, true); //  统一处理
    });

    messageOffset += messages.length;

    // 首次加载滚动到底部
    if (messageOffset === messages.length) {
      chatBox.scrollTop = chatBox.scrollHeight;
    }
  });

  socket.on("receive_message", (data) => {
    if (thinkingMsgElement && data.role === "system") {
      thinkingMsgElement.remove(); // 删除“思考中”原始块
      thinkingMsgElement = null;

      appendMessage(data); // 用真实消息重新渲染，走完整样式逻辑
      return;
    }

    appendMessage(data);
    playMentionSound(data);
  });

  // 更新显示在线用户列表人数
  socket.on("online_users", (userList) => {
    const filtered = userList;

    // 排序规则
    filtered.sort((a, b) => {
      const getPriority = (u) => {
        if (u.username === window.username) return 0;
        if (u.role === "super_admin") return 1;
        if (u.role === "admin") return 2;
        return 3; // 普通用户
      };
      return getPriority(a) - getPriority(b);
    });

    // 渲染
    const container = document.getElementById("online-user-list");
    container.innerHTML = filtered
      .map(({ username, role }) => {
        const label = username === window.username ? "（你）" : "";
        const isSelf = username === window.username;
        const { color, badge } = getIdentityStyle(role, isSelf);

        return `
        <div style="
          background: #ffffff;
          border-radius: 12px;
          padding: 10px 14px;
          margin-bottom: 10px;
          box-shadow: 0 2px 6px rgba(0,0,0,0.1);
          display: flex;
          align-items: center;
          justify-content: space-between;
          font-weight: 600;
          font-size: 15px;
          color: ${color};
          transition: transform 0.2s ease;
        ">
          <span>${username}${label}</span>
          ${badge ? `<span style="font-size: 18px;">${badge}</span>` : ""}
        </div>
      `;
      })
      .join("");

    // 更新按钮人数（包含游客在内的总数）
    const btn = document.getElementById("online-count-btn");
    btn.textContent = `当前在线人数：${userList.length}`;
  });
}

// 高亮消息中有效 @用户名 的文字
function highlightMentions(msg) {
  return msg.replace(/@([\u4e00-\u9fa5\w\-]+)/g, (match, uname) => {
    if (knownUsernames.has(uname)) {
      return `<span style="color: #f472b6; font-weight: bold;">@${uname}</span>`;
    }
    return match;
  });
}

// 若消息中包含 @自己，则播放提示音
function playMentionSound(data) {
  if (data.message && data.message.includes(`@${window.username}`)) {
    const audio = new Audio("/static/assets/audio/notify.mp3");
    audio.play().catch(() => {}); // 避免浏览器自动播放限制报错
  }
}

// 若消息中包含 @自己，则让该消息块背景短暂高亮
function highlightIfMentioned(msgDiv, data) {
  if (data.message && data.message.includes(`@${window.username}`)) {
    msgDiv.style.transition = "background-color 0.8s ease";
    msgDiv.style.backgroundColor = "#ffe4ec";
    setTimeout(() => {
      msgDiv.style.backgroundColor = "transparent";
    }, 1500);
  }
}

// 渲染并插入单条消息，prepend=true 表示向上插入（历史记录）
function appendMessage(data, prepend = false) {
  // ✨ 标准化 role 字段，去除空格和换行
  if (data.role && typeof data.role === "string") {
    data.role = data.role.trim();
  }

  const msgDiv = document.createElement("div");

  if (data.role === "poll_broadcast") {
    const msgDiv = renderPollBroadcastCard(data);
    insertMessage(msgDiv, prepend); //  修复位置错误
    return;
  }

  // 若是查询时间的指令就自动计算UTC加上本地时区
  if (
    data.message.startsWith("🕐") &&
    data.role === "system" &&
    data.timestamp
  ) {
    const local = new Date(data.timestamp);
    const timeStr = local.toLocaleString(undefined, {
      year: "numeric",
      month: "numeric",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
    data.message += ` ${timeStr}`;
  }

  // 将 ISO 格式时间转换成本地时间字符串
  let timeStr = "";
  if (data.timestamp) {
    try {
      let rawTime = data.timestamp || "";
      if (rawTime && !rawTime.endsWith("Z") && !rawTime.includes("+")) {
        rawTime += "Z"; // 仅当无时区时补
      }
      const local = new Date(rawTime);
      timeStr = local.toLocaleString(undefined, {
        year: "numeric",
        month: "numeric",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        hour12: false,
      });
    } catch {}
  }

  const isSelf = data.username === window.username && data.role !== "system";

  const { color: nameColor, badge } = getIdentityStyle(data.role, isSelf);

  msgDiv.innerHTML = `
  <div style="display: flex; justify-content: space-between; align-items: flex-start;">
    <div style="flex: 1;">
      <span class="username" style="color:${nameColor}; font-weight:bold; cursor: pointer;" onclick="atUser('${
    data.username
  }')">
        ${data.username}
      </span>${badge ? `<span style="margin-left: 4px;">${badge}</span>` : ""}: 
      <span style="color: ${data.color || "inherit"};">
        ${highlightMentions(data.message || "").replace(/\n/g, "<br>")}
      </span>
    </div>
    <span style="font-size:12px; color:#aaa; white-space: nowrap; margin-left: 8px;">${timeStr}</span>
  </div>
`;
  // 若输入的是错误指令则执行的css样式
  if (data.style === "error") {
    msgDiv.style.color = "#ef4444"; // 红色字体
  }

  // 如果是系统指令消息
  if (data.role === "system") {
    // 根据起始的徽章判断是否为AI指令
    const isAI = data.message.startsWith("🤖") || data.isAI; // 直接判断是否以🤖开头  isAI为 AI思考中的标识

    // 在appendMessage中：
    if (data.isThinking) {
      msgDiv.innerHTML = `
  <div class="thinking-message">
      <div class="thinking-spinner"></div>
      ${data.message}
  </div>`;
    }

    msgDiv.style.background = "#e0f2fe"; // 更明显的浅蓝背景
    msgDiv.style.borderRadius = "6px";
    msgDiv.style.padding = "10px 0px";
    msgDiv.style.margin = "4px 0";
    msgDiv.style.fontStyle = "normal"; // 不用斜体了
    msgDiv.style.width = "100%"; // 撑满宽度
    msgDiv.style.boxSizing = "border-box"; // 包含 padding

    // 颜色方案优化（根据最新需求调整）#1e3a8a
    msgDiv.style.color = isAI ? "#7c3aed" : "#00b06d"; // AI紫色/默认绿色
    msgDiv.style.borderLeft = isAI ? "3px solid #7c3aed" : "3px solid #00b06d"; // 左侧边框强化区分
  }

  // 添加动画类（仅对新消息）
  if (!prepend) {
    msgDiv.classList.add("new-message");

    // 动画结束后移除类（避免影响布局计算）
    msgDiv.addEventListener(
      "animationend",
      () => {
        msgDiv.classList.remove("new-message");
      },
      { once: true }
    );
  }

  // 插入到消息框中
  if (prepend) {
    chatBox.insertBefore(msgDiv, chatBox.firstChild);
  } else {
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
  }
  // 如果该消息是 @ 自己的，高亮提示
  if (data.role !== "system") {
    highlightIfMentioned(msgDiv, data);
  }

  return msgDiv; // 返回新建的元素
}
// 点击用户名时自动补齐 @用户名 到输入栏中
function atUser(name) {
  const input = document.getElementById("message");
  const atText = `@${name} `;

  // 如果已经包含，不重复添加@信息
  if (!input.value.includes(atText)) {
    const span = document.createElement("span");
    span.style.color = "#f472b6"; // 粉色
    span.textContent = atText;
    input.value += input.value ? ` ${atText}` : atText;
    input.focus();
  }
}

function showAlert(message, type = "info", duration = 1800) {
  const el = document.getElementById("alert-banner");
  if (!el) return;
  // 设置内容和类型
  el.textContent = message;
  el.className = `alert-banner ${type} show`;
  // 自动隐藏
  setTimeout(() => {
    el.classList.remove("show");
  }, duration);
}

// 显示自定义 AI 提示
function showAIWarning() {
  showAlert("🤖 请等待 AI 思考完毕再发送！", "error");
}

function sendMessage(msgFromBtn = null) {
  const msg = msgFromBtn || messageInput.value.trim();
  if (!msg) return;

  // 检查是否正在思考中（包括AI思考和其他指令）
  if (thinkingMsgElement) {
    showAIWarning();
    return;
  }

  // 防止连续 AI 请求（前端限制）
  if ((msg.startsWith("/ask") || msg.startsWith("/ai")) && thinkingMsgElement) {
    showAIWarning();
    return;
  }

  if (msg.startsWith("/ask") || msg.startsWith("/ai")) {
    insertThinkingMessage();
  }

  socket.emit("send_message", { message: msg });
  // 如果是按钮传的值，就不清空输入框
  if (!msgFromBtn) {
    messageInput.value = "";

    // 清除 AI 卡片
    const tag = document.getElementById("ask-tag");
    if (tag) tag.remove();
    const input = document.getElementById("message");
    input.style.paddingLeft = "";
  }
}

// 退出登录，清除缓存，跳转 logout
function logout() {
  if (window.username === "游客") {
    localStorage.removeItem("savedUsername"); // 清除游客名
  }
  localStorage.removeItem("savedUsername");
  localStorage.removeItem("savedPassword");
  localStorage.setItem("autoLogin", "no");
  window.location.href = "/logout";
}

// 加载更多历史记录
function loadMore() {
  socket.emit("load_more_history", {
    offset: messageOffset,
    limit: limitPerLoad,
  });
}

// 支持回车快速发送
messageInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage();
});

// 打开在线用户列表浮窗
function openOnlineList() {
  document.getElementById("online-overlay").style.display = "block";
  document.getElementById("online-modal").style.display = "block";
  document.body.style.overflow = "hidden";
}

// 关闭在线用户列表浮窗
function closeOnlineList() {
  document.getElementById("online-overlay").style.display = "none";
  document.getElementById("online-modal").style.display = "none";
  document.body.style.overflow = "";
}

// 检查是否需要展示公告栏
function checkAnnouncement() {
  fetch("/announcement")
    .then((res) => res.json())
    .then((data) => {
      const savedId = localStorage.getItem("announcement_seen_id");
      if (savedId !== data.id) {
        document.getElementById("announcement-title").textContent = data.title;
        document.getElementById("announcement-content").textContent =
          data.content;
        document.getElementById("announcement-modal").style.display = "block";
        document.getElementById("announcement-overlay").style.display = "block"; // 显示遮罩
        document.body.style.overflow = "hidden"; // 禁止页面滚动
        window.currentAnnouncementId = data.id;
      }
    });
}

// 关闭公告栏
function closeAnnouncement() {
  document.getElementById("announcement-modal").style.display = "none";
  document.getElementById("announcement-overlay").style.display = "none"; // 隐藏遮罩
  document.body.style.overflow = ""; // 恢复滚动
}

// 记录已阅读过该ID的公告栏信息
function acknowledgeAnnouncement() {
  localStorage.setItem("announcement_seen_id", window.currentAnnouncementId);
  closeAnnouncement();
}

// 监听输入内容 若是指令相关则渲染不同颜色提示
messageInput.addEventListener("input", () => {
  const val = messageInput.value.trim();
  if (val.startsWith("/")) {
    const firstWord = val.split(/\s+/)[0];
    if (validCommands.has(firstWord)) {
      messageInput.style.color = "#22c55e"; // 绿色
      messageInput.style.borderColor = "#22c55e";
    } else {
      messageInput.style.color = "#ef4444"; // 红色
      messageInput.style.borderColor = "#ef4444";
    }
  } else {
    messageInput.style.color = "";
    messageInput.style.borderColor = "";
  }
});

// 页面加载时处理(包括但不限于 检查公告 并检查身份 若是游客关闭输入栏发送消息的权限 获取可用指令合集等)
window.addEventListener("DOMContentLoaded", () => {
  checkAnnouncement();

  fetch("/commands")
    .then((res) => res.json())
    .then((cmds) => {
      validCommands = new Set(cmds);
    });

  fetch("/usernames")
    .then((res) => res.json())
    .then((names) => {
      names.forEach((name) => knownUsernames.add(name));
      initSocket(); // ← 加载完用户名后再连接 socket
    });

  const role = window.userRole;
  const nameEl = document.getElementById("display-username");
  renderIdentity(nameEl, role); // 用统一函数处理身份徽章和颜色
  // 游客禁止发言 + 禁用功能逻辑
  if (role === "guest") {
    const input = document.getElementById("message");
    const button = document.querySelector("#chat-input-send-btn");

    // 🔒 1. 禁止输入和发送
    input.disabled = true;
    input.placeholder = "游客无法发送消息";
    button.textContent = "注册";
    button.onclick = () => (window.location.href = "/");

    // 🔒 2. 禁用工具栏按钮
    const toolButtons = document.querySelectorAll("#tool-bar button");
    toolButtons.forEach((btn) => {
      btn.disabled = true;
      btn.style.opacity = "0.5";
      btn.style.cursor = "not-allowed";
      btn.title = "请先登录使用此功能";
    });

    // 🔒 3. 禁用所有“查看详情”按钮
    document.addEventListener("click", (e) => {
      if (e.target.matches(".poll-broadcast-card button")) {
        e.preventDefault();
        showAlert("请先注册并登录后查看详情", "error");
      }
    });

    // 🔔 4. 顶部提示（可选）
    showAlert("👤 当前为游客身份，部分功能已锁定", "info");
  }
});

// 注册 PWA Service Worker
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/static/service-worker.js")
      .then((reg) => console.log("ServiceWorker 注册成功:", reg.scope))
      .catch((err) => console.log("ServiceWorker 注册失败:", err));
  });
}

const toggleBtn = document.getElementById("tool-toggle-btn");
const toolBar = document.getElementById("tool-bar");
const toolIcon = document.getElementById("tool-icon");
// 切换工具栏显示
toggleBtn.addEventListener("click", () => {
  const isOpen = toolBar.style.display === "flex";
  toolBar.style.display = isOpen ? "none" : "flex";
  toolIcon.classList.toggle("rotated", !isOpen);
});
// 点击外部隐藏工具栏
document.addEventListener("click", (e) => {
  if (!toolBar.contains(e.target) && !toggleBtn.contains(e.target)) {
    toolBar.style.display = "none";
    toolIcon.classList.remove("rotated");
  }
});

function sendToolCommand(cmd) {
  sendMessage(cmd);
  closeToolBar();
}

function closeToolBar() {
  document.getElementById("tool-bar").style.display = "none";
  toolIcon.classList.toggle("rotated", false);
}

// 当按下AI提问按钮触发的函数
function insertAskPrefix() {
  const input = document.getElementById("message");

  // 如果已经有 /ask，跳过
  if (!input.value.startsWith("/ask ")) {
    input.value = `/ask ${input.value}`.trimStart();
  }

  renderAskTag(); // 渲染提示卡片
  input.focus();
  closeToolBar();
}

// 当按下AI提问按钮后 渲染一个AI卡片来代替/ask 文本
function renderAskTag() {
  const input = document.getElementById("message");
  input.style.paddingLeft = "57px";

  // 若已有则不重复加
  if (document.getElementById("ask-tag")) return;

  const tag = document.createElement("div");
  tag.id = "ask-tag";
  tag.innerHTML = "🤖 <strong style='color:#1e3a8a;'>提问AI</strong>";
  tag.style.position = "absolute";
  tag.style.left = "53px";
  tag.style.top = "50%";
  tag.style.transform = "translateY(-50%)";
  tag.style.background = "#e0e7ff";
  tag.style.borderRadius = "6px";
  tag.style.fontSize = "13px";
  tag.style.padding = "3px 8px";
  tag.style.color = "#1e3a8a";
  tag.style.fontWeight = "bold";
  tag.style.pointerEvents = "none";

  // 包含输入框的 div 要是 relative
  input.parentElement.style.position = "relative";
  input.parentElement.appendChild(tag);
}

document.getElementById("message").addEventListener("keydown", (e) => {
  const input = e.target;

  // 条件：按的是退格 + 有卡片 + 输入框以 /ask 开头
  if (
    e.key === "Backspace" &&
    input.value.startsWith("/ask ") &&
    input.selectionStart <= 5 // 光标在 /ask 后面位置
  ) {
    // 阻止默认删除行为
    e.preventDefault();

    // 删除 /ask 和卡片
    input.value = input.value.replace(/^\/ask\s*/, "");
    input.style.paddingLeft = "";
    const tag = document.getElementById("ask-tag");
    if (tag) tag.remove();
  }
});

// —— 1. 引用 DOM —— //
const listOverlay = document.getElementById("poll-list-overlay");
const listModal = document.getElementById("poll-list-modal");
const listCloseBtn = document.getElementById("poll-list-close");
const listNewBtn = document.getElementById("poll-list-new-btn");
const pollListContainer = document.getElementById("poll-list-container");

const createOverlay = document.getElementById("poll-create-overlay");
const createModal = document.getElementById("poll-create-modal");
const createCancelBtn = document.getElementById("poll-create-cancel");
const pollCreateOptionList = document.getElementById("poll-create-option-list");
const pollCreateAddBtn = document.getElementById("poll-create-add-option");
const pollCreateRemoveBtn = document.getElementById(
  "poll-create-remove-option"
);
const pollCreateSubmitBtn = document.getElementById("poll-create-submit");
const pollCreateInput = document.getElementById("poll-create-question");

const detailOverlay = document.getElementById("poll-detail-overlay");
const detailModal = document.getElementById("poll-detail-modal");
const detailClose = detailModal.querySelector(".close");
const detailBack = detailModal.querySelector(".back");
const detailTitle = document.getElementById("poll-detail-title");
const detailStatus = document.getElementById("poll-detail-card-status");
const detailOptsUl = detailModal.querySelector(".poll-detail-options");

// 假设给工具栏投票按钮加了个 id="tool-poll-btn"
const toolPollBtn = document.getElementById("tool-poll-btn");

// —— 2. 通用显示／隐藏函数 —— //
function show(overlay, modal) {
  overlay.style.display = "block";
  modal.style.display = "flex";
}
function hide(overlay, modal) {
  overlay.style.display = "none";
  modal.style.display = "none";
}

// —— 3. 四个动作函数 —— //
function openPollList() {
  show(listOverlay, listModal);
  loadPollList();
  closeToolBar();
}
function openPollCreate() {
  hide(listOverlay, listModal);
  show(createOverlay, createModal);
}

function closePollCreate() {
  show(listOverlay, listModal);
  hide(createOverlay, createModal);
}
function backToPollList() {
  hide(createOverlay, createModal);
  hide(detailOverlay, detailModal);
  show(listOverlay, listModal);
  loadPollList();
}
// —— 事件绑定 —— //
// 工具栏“投票”按钮 → 打开列表
toolPollBtn.addEventListener("click", openPollList);

// 列表浮窗底部“＋”按钮 → 打开创建
listNewBtn.addEventListener("click", openPollCreate);

// 创建浮窗“取消”或点击遮罩 → 返回列表
createCancelBtn.addEventListener("click", backToPollList);
createOverlay.addEventListener("click", backToPollList);

// 列表浮窗的关闭（×）和遮罩
listCloseBtn.addEventListener("click", () => hide(listOverlay, listModal));
listOverlay.addEventListener("click", () => hide(listOverlay, listModal));

// —— 增减选项按钮逻辑 —— //
function handleAddOption() {
  const items = pollCreateOptionList.querySelectorAll(
    ".poll-create-option-item"
  );
  if (items.length >= 6) {
    showAlert("最多6个选项！", "error");
    return;
  }
  const idx = items.length + 1;
  const div = document.createElement("div");
  div.className = "poll-create-option-item";
  div.innerHTML = `<input type="text" maxlength="8" placeholder="选项${idx}" />`;
  pollCreateOptionList.appendChild(div);
}

function handleRemoveOption() {
  const items = pollCreateOptionList.querySelectorAll(
    ".poll-create-option-item"
  );
  if (items.length <= 2) {
    showAlert("最少2个选项！", "error");
    return;
  }
  pollCreateOptionList.removeChild(items[items.length - 1]);
}

// —— 绑定点击事件 —— //
pollCreateAddBtn.addEventListener("click", handleAddOption);
pollCreateRemoveBtn.addEventListener("click", handleRemoveOption);

function renderPollList(polls) {
  // 清空旧内容
  pollListContainer.innerHTML = "";

  polls.forEach((poll) => {
    const card = document.createElement("div");
    card.className = "poll-list-card";
    card.addEventListener("click", () => openPollDetail(poll.poll_id));

    const title = document.createElement("div");
    title.className = "poll-list-card-title";
    title.textContent = poll.message;
    ``;

    const meta = document.createElement("div");
    meta.className = "poll-list-card-meta";

    const author = document.createElement("span");
    author.className = "poll-list-card-author";
    author.innerHTML = `由 <span style="color:#3b82f6; font-weight:bold;">${poll.creator}</span> 发起`;

    const status = document.createElement("span");
    status.className = "poll-detail-card-status";

    // 状态判断
    let label = "";
    let color = "";

    if (poll.ended) {
      label = "已结束";
      color = "#888"; // 灰色
    } else if (poll.user_voted) {
      label = "你已投票";
      color = "#facc15"; // 黄色
    } else {
      label = "进行中";
      color = "#22c55e"; // 绿色
    }

    status.textContent = `${label} · ${poll.total_votes} 人参与`;
    status.style.color = color;
    status.style.fontWeight = "bold";

    meta.append(author, status);
    card.append(title, meta);
    pollListContainer.appendChild(card);
  });
}

// —— 刷新并渲染投票列表 —— //
function loadPollList() {
  socket.off("poll_list_result");
  socket.emit("list_polls");
  socket.once("poll_list_result", renderPollList);
}

// —— 提交新投票 —— //
function handlePollCreateSubmit() {
  const question = pollCreateInput.value.trim();
  const options = Array.from(pollCreateOptionList.querySelectorAll("input"))
    .map((i) => i.value.trim())
    .filter((v) => v);

  // 验证
  if (!question) {
    return showAlert("请输入投票标题", "error");
  }
  if (options.length < 2) {
    return showAlert("至少要两个选项", "error");
  }
  if (options.length > 6) {
    return showAlert("最多 6 个选项", "error");
  }

  pollCreateSubmitBtn.disabled = true;

  // 发送 socket 创建投票
  socket.emit("create_poll", {
    username: window.username,
    question,
    options,
  });

  // 监听 socket 返回 poll_id 后的回调
  socket.once("poll_created", ({ poll_id }) => {
    showAlert("创建成功！", "success");

    // 关闭创建浮窗，打开列表并刷新
    closePollCreate();
    openPollList();
    loadPollList();

    // 清空表单
    pollCreateInput.value = "";
    pollCreateOptionList
      .querySelectorAll(".poll-create-option-item")
      .forEach((div, i) => {
        div.querySelector("input").value = "";
        if (i >= 2) div.remove();
      });

    pollCreateSubmitBtn.disabled = false;
  });
}

// —— 事件绑定 —— //
pollCreateSubmitBtn.addEventListener("click", handlePollCreateSubmit);

function openPollDetail(pollId) {
  socket.off("poll_detail_result");
  socket.emit("get_poll_detail", { poll_id: pollId });
  socket.once("poll_detail_result", (data) => {
    renderPollDetail(data);
  });
}

// —— 投票 —— //
function votePoll(pollId, optionId) {
  if (!pollId || !optionId) return;

  socket.emit("vote_poll", { poll_id: pollId, option_id: optionId });

  socket.once("poll_vote_result", (res) => {
    if (res.success) {
      showAlert("投票成功！", "success");

      //  立即刷新详情页
      refreshPollDetail(pollId);

      //  立即刷新列表页
      socket.off("poll_list_result");
      socket.emit("list_polls");
      socket.once("poll_list_result", renderPollList);
    } else {
      showAlert(res.error || "投票失败", "error");
    }
  });
}

// —— 绑定关闭/返回 —— //
detailClose.addEventListener("click", () => hide(detailOverlay, detailModal));
detailBack.addEventListener("click", backToPollList);
detailOverlay.addEventListener("click", () => hide(detailOverlay, detailModal));

// —— 全局挂载（方便 Card 点击回调） —— //
window.openPollDetail = openPollDetail;

function renderPollBroadcastCard(data) {
  const msgDiv = document.createElement("div");
  msgDiv.setAttribute("data-poll-id", data.poll_id);
  msgDiv.className = "poll-broadcast-card";

  const title = document.createElement("div");
  title.innerHTML = `🗳️ <strong style="color:#1e3a8a;">${data.creator}</strong> 发起了投票<strong>${data.message}</strong>`;
  msgDiv.appendChild(title);

  const button = document.createElement("button");
  button.textContent = "查看详情";
  button.onclick = () => openPollDetail(data.poll_id);
  msgDiv.appendChild(button);

  return msgDiv;
}

function renderPollDetail(data) {
  detailOptsUl.innerHTML = "";

  try {
    if (data.error) {
      showAlert(data.error, "error");
      return;
    }

    // 设置标题
    detailTitle.textContent = `🗳️ ${data.message}`;

    // 设置状态文本和颜色
    if (data.ended) {
      detailStatus.textContent = "（已结束）";
      detailStatus.style.color = "#888";
    } else if (data.user_voted) {
      detailStatus.textContent = "（你已投票）";
      detailStatus.style.color = "#facc15";
    } else {
      detailStatus.textContent = "（进行中）";
      detailStatus.style.color = "#22c55e";
    }

    // 清空旧选项
    detailOptsUl.innerHTML = "";

    data.options.forEach((opt) => {
      const li = document.createElement("li");
      const btn = document.createElement("button");
      btn.className = "poll-detail-option-btn";

      const spanText = document.createElement("span");
      spanText.className = "poll-detail-option-text";
      spanText.textContent = opt.text;
      btn.append(spanText);

      const shouldShowResult = data.ended || data.user_voted;

      const bar = document.createElement("div");
      bar.className = "progress-bar";
      bar.style.display = shouldShowResult ? "block" : "none";

      const fill = document.createElement("div");
      fill.className = "progress-fill";
      const pct = data.total_votes
        ? Math.round((opt.votes / data.total_votes) * 100) + "%"
        : "0%";
      fill.style.width = pct;
      bar.append(fill);
      btn.append(bar);

      const count = document.createElement("span");
      count.className = "vote-count";
      count.textContent = `${opt.votes} 票`;
      count.style.display = shouldShowResult ? "inline" : "none";
      btn.append(count);

      if (!data.ended) {
        btn.addEventListener("click", () =>
          votePoll(data.poll_id, opt.option_id)
        );
      }

      li.append(btn);
      detailOptsUl.append(li);
    });

    show(detailOverlay, detailModal);
    hide(listOverlay, listModal);
    hide(createOverlay, createModal);
  } catch (err) {
    console.error(err);
    showAlert("加载投票详情失败", "error");
  }
}

function refreshPollDetail(pollId) {
  socket.off("poll_detail_result"); // 清理监听
  socket.emit("get_poll_detail", { poll_id: pollId });

  socket.once("poll_detail_result", (data) => {
    if (data.error) {
      showAlert(data.error, "error");
      return;
    }

    renderPollDetail(data); //  正确传入完整 poll 数据对象
  });
}

function insertMessage(msgDiv, prepend = false) {
  if (prepend) {
    chatBox.insertBefore(msgDiv, chatBox.firstChild);
  } else {
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
  }
}
