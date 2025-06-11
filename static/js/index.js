//#region Google Analytics（谷歌分析）的代码，用于网站访问统计
window.dataLayer = window.dataLayer || [];
function gtag() {
  dataLayer.push(arguments);
}
gtag("js", new Date());

gtag("config", "G-ZK9F0GE4SE");
//#endregion

// 获取页面上的提示信息显示元素（红色或绿色提示）
const messageEl = document.getElementById("message");

// 注册账号函数，向后端发送用户名和密码
function register() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();
  // 简单表单校验
  if (!username || !password) {
    messageEl.style.color = "red";
    messageEl.textContent = "用户名和密码不能为空";
    return;
  }
  // 向后端发送注册请求
  fetch("/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
    credentials: "include",
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.error) {
        messageEl.style.color = "red";
        messageEl.textContent = data.error;
      } else {
        messageEl.style.color = "green";
        messageEl.textContent = data.message;
      }
    })
    .catch((err) => {
      messageEl.style.color = "red";
      messageEl.textContent = "请求失败，请检查服务器";
      console.error(err);
    });
}

// 游客登录，清除保存信息并跳转后端接口
function guestLogin() {
  // 清除任何自动登录和记住密码信息
  localStorage.removeItem("savedPassword");
  localStorage.setItem("autoLogin", "no");
  // 跳转到 Flask 的游客登录接口
  window.location.href = "/guest-login";
}

// 登录函数
function login() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();

  if (!username || !password) {
    messageEl.style.color = "red";
    messageEl.textContent = "用户名和密码不能为空";
    return;
  }

  // 向后端发送登录请求
  fetch("/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
    credentials: "include",
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.error) {
        messageEl.style.color = "red";
        messageEl.textContent = data.error;
      } else {
        messageEl.style.color = "green";
        messageEl.textContent = data.message;

        // 始终保存用户名
        localStorage.setItem("savedUsername", username);

        // 记住密码选项
        const remember = document.getElementById("rememberPass").checked;
        if (remember) {
          localStorage.setItem("savedPassword", password);
        } else {
          localStorage.removeItem("savedPassword");
        }

        // 自动登录选项 信息保存
        const autoLogin = document.getElementById("autoLogin").checked;
        localStorage.setItem("autoLogin", autoLogin ? "yes" : "no");
        // 延迟跳转主页
        setTimeout(() => {
          window.location.href = "/home";
        }, 500);
      }
    })
    .catch((err) => {
      messageEl.style.color = "red";
      messageEl.textContent = "请求失败，请检查服务器";
      console.error(err);
    });
}

// 页面加载后自动填充表单并处理自动登录逻辑
window.addEventListener("DOMContentLoaded", () => {
  const savedUsername = localStorage.getItem("savedUsername");
  const savedPassword = localStorage.getItem("savedPassword");
  const autoLogin = localStorage.getItem("autoLogin");
  // 自动填充用户名
  if (savedUsername) {
    document.getElementById("username").value = savedUsername;
  }
  // 自动填充密码 + 勾选记住密码
  if (savedPassword) {
    document.getElementById("password").value = savedPassword;
    document.getElementById("rememberPass").checked = true;
  }
  // 如果开启自动登录且用户名密码都存在 → 自动登录
  if (autoLogin === "yes" && savedUsername && savedPassword) {
    document.getElementById("autoLogin").checked = true;
    login(); // 自动登录
  } else {
    document.getElementById("autoLogin").checked = false;
  }
  // 兜底逻辑：如果已登录就跳转主页
  if (autoLogin === "yes") {
    fetch("/home", {
      method: "GET",
      credentials: "include",
    }).then((res) => {
      if (!res.redirected) {
        window.location.href = "/home";
      }
    });
  }
});

// 注册 Service Worker 用于离线缓存支持
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/static/service-worker.js")
      .then((reg) => console.log("ServiceWorker 注册成功:", reg.scope))
      .catch((err) => console.log("ServiceWorker 注册失败:", err));
  });
}
