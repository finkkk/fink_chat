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
      guest: "👀",
    };
    const badge = badgeMap[role] || "";
    return { color: "#10b981", badge };
  }

  // 其他人：正常身份样式
  if (role === "system") return { color: "purple", badge: "🪄" };
  if (role === "super_admin") return { color: "red", badge: "👑" };
  if (role === "admin") return { color: "orange", badge: "🎯" };
  if (role === "guest") return { color: "gray", badge: "👀" };

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
    console.log("已连接到服务器");
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
    messages.reverse().forEach((msg) => appendMessage(msg, true));
    messageOffset += messages.length;
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

  // 将 ISO 格式时间转换成本地时间字符串
  let timeStr = "";
  if (data.timestamp) {
    try {
      const local = new Date(data.timestamp + "Z");
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
    msgDiv.style.borderRadius = "4px";
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

// 显示自定义 AI 提示
function showAIWarning() {
  const warnEl = document.getElementById("ai-warning");
  if (!warnEl) return;
  warnEl.style.display = "block";

  // 自动隐藏（1.8 秒后）
  setTimeout(() => {
    warnEl.style.display = "none";
  }, 1800);
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
  // 游客禁止发言逻辑
  if (role === "guest") {
    const input = document.getElementById("message");
    const button = document.querySelector("#chat-input button");

    input.disabled = true;
    input.placeholder = "游客无法发送消息";
    button.textContent = "注册";
    button.onclick = () => (window.location.href = "/");
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
