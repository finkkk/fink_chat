# commands/common.py
import random
from datetime import datetime
from config import SYSTEM_USERNAME
from .admin import ADMIN_COMMANDS
from .ai import AI_COMMANDS


# ====== 指令处理函数 ======


# 查询指令使用指南
def cmd_help(username, args, role="user"):
    lines = ["📖 可用指令列表："]
    for group in (COMMON_COMMANDS, ADMIN_COMMANDS, AI_COMMANDS):
        for cmd, info in group.items():
            if role in info["permission"]:
                lines.append(f"👉 {cmd}：{info['desc']}")
    return {"username": SYSTEM_USERNAME, "message": "\n".join(lines)}


# 摇骰子
def cmd_roll(username, args):
    dice = random.randint(1, 6)
    return {
        "username": SYSTEM_USERNAME,
        "message": f"🎲 {username} 掷出了一个 {dice}！",
    }


# 查询时间
def cmd_time(username, args):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    return {"username": SYSTEM_USERNAME, "message": f"🕐 当前服务器时间：{now}"}


# 趣味交互指令
def cmd_hit(username, args):
    if not args or not args[0].startswith("@"):
        return {
            "username": SYSTEM_USERNAME,
            "message": "⚠️ 请使用格式：/hit @某人",
            "style": "error",
        }

    target = args[0]
    action = " ".join(args[1:]) or "一个大逼兜"

    return {
        "username": SYSTEM_USERNAME,
        "message": f"😛 {username} 给了 {target} {action}！",
    }


# ====== 指令注册字典 ======


COMMON_COMMANDS = {
    "/help": {
        "desc": "查看指令说明",
        "func": cmd_help,
        "broadcast": False,  # 是否广播给所有人
        "save": False,  # 是否保存到历史记录
        "permission": ["user", "admin", "super_admin"],  # 所有人可用
    },
    "/roll": {
        "desc": "掷骰子(1~6)",
        "func": cmd_roll,
        "broadcast": True,
        "save": True,
        "permission": ["user", "admin", "super_admin"],
    },
    "/time": {
        "desc": "显示当前时间(UTC时间:0时区)",
        "func": cmd_time,
        "broadcast": False,
        "save": False,
        "permission": ["user", "admin", "super_admin"],
    },
    "/hit": {
        "desc": "使用方法/hit @用户名 (xx给了xx一个大逼兜)",
        "func": cmd_hit,
        "broadcast": True,
        "save": True,
        "permission": ["user", "admin", "super_admin"],
    },
}
