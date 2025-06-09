# commands.py
from datetime import datetime
from config import SYSTEM_USERNAME
import random

# ======指令处理函数======

# 查询指令使用指南
def cmd_help(username, args, role="user"):
    lines = ["📖 可用指令列表："]
    for cmd, info in AVAILABLE_COMMANDS.items():
        allowed_roles = info.get("permission", ["user", "admin", "super_admin"])
        if role in allowed_roles:
            lines.append(f"👉 {cmd}：{info['desc']}")
    return {
        "username": SYSTEM_USERNAME,
        "message": "\n".join(lines)
    }

# 摇骰子
def cmd_roll(username, args):
    dice = random.randint(1, 6)
    return {
        'username': SYSTEM_USERNAME,
        'message': f'🎲 {username} 掷出了一个 {dice}！'
    }

# 查询时间
def cmd_time(username, args):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    return {
        'username': SYSTEM_USERNAME,
        'message': f'🕐 当前服务器时间：{now}'
    }

# 测试@指令
def cmd_hit(username, args):
    if not args or not args[0].startswith("@"):
        return {
            "username": SYSTEM_USERNAME,
            "message": "⚠️ 请使用格式：/hit @某人",
            "style": "error"
        }

    target = args[0]
    action = " ".join(args[1:]) or "一个大逼兜"

    return {
        "username": SYSTEM_USERNAME,
        "message": f'😛 {username} 给了 {target} {action}！'
    }

# 测试指令 仅管理员可用
def cmd_testadmin(username, args):
    return {
        "username": SYSTEM_USERNAME,
        "message": f'🎯 管理员 {username} 发起了一次权限测试！',
        "style": "success"
    }

# 测试指令 仅超级管理员可用
def cmd_testsuper(username, args):
    return {
        "username": SYSTEM_USERNAME,
        "message": f'👑 超级管理员 {username} 模拟执行了关机操作。',
        "style": "success"
    }

# 指令注册字典
AVAILABLE_COMMANDS = {
    "/help": {
        "desc": "查看指令说明",
        "func": cmd_help,
        "broadcast": False,                             # 是否广播给所有人
        "save": False,                                  # 是否保存到历史记录
        "permission": ["user", "admin", "super_admin"]  # 所有人可用
    },

    "/roll": {
        "desc": "掷骰子(1~6)",
        "func": cmd_roll,
        "broadcast": True,       
        "save": True,
        "permission": ["user", "admin", "super_admin"]
    },

    "/time": {
        "desc": "显示当前时间(UTC时间:0时区)",
        "func": cmd_time,
        "broadcast": False,       
        "save": False,
        "permission": ["user", "admin", "super_admin"]
    },

    "/hit": {
        "desc": "使用方法/hit @用户名 (xx给了xx一个大逼兜)",
        "func": cmd_hit,
        "broadcast": True,
        "save": True,
        "permission": ["user", "admin", "super_admin"]
    },


    "/testadmin": {
        "desc": "管理员测试用指令",
        "func": cmd_testadmin,
        "broadcast": False,
        "save": False,
        "permission": ["admin", "super_admin"]
    },

    "/testsuper": {
        "desc": "超级管理员测试用指令",
        "func": cmd_testsuper,
        "broadcast": False,
        "save": False,
        "permission": ["super_admin"]
    },
}

def handle_command(command, args, username, role="user"):
    cmd_conf = AVAILABLE_COMMANDS.get(command)
    if not cmd_conf:
        return {
            'username': SYSTEM_USERNAME,
            'message': f'❓ 未知指令: {command}',
            'style': 'error',
            'broadcast': True,
            'save': False
        }

    # ===== 权限检查 =====
    allowed = cmd_conf.get("permission", ["user", "admin", "super_admin"])
    if role not in allowed:
        return {
            'username': SYSTEM_USERNAME,
            'message': f'⛔ 你没有权限使用该指令: {command}',
            'style': 'error',
            'broadcast': False,
            'save': False
        }

    if command == "/help":
        result = cmd_conf['func'](username, args, role=role)
    else:
        result = cmd_conf['func'](username, args)
    result['broadcast'] = cmd_conf.get('broadcast', True)
    result['save'] = cmd_conf.get('save', False)
    return result