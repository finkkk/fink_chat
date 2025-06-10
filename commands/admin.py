from config import SYSTEM_USERNAME


# ====== 指令处理函数 ======


# 测试指令 仅管理员可用
def cmd_testadmin(username, args):
    return {
        "username": SYSTEM_USERNAME,
        "message": f"🎯 管理员 {username} 发起了一次权限测试！",
    }


# 测试指令 仅超级管理员可用
def cmd_testsuper(username, args):
    return {
        "username": SYSTEM_USERNAME,
        "message": f"👑 超级管理员 {username} 模拟执行了关机操作。",
    }


# ====== 指令注册字典 ======


ADMIN_COMMANDS = {
    "/testadmin": {
        "desc": "管理员测试用指令",
        "func": cmd_testadmin,
        "broadcast": False,
        "save": False,
        "permission": ["admin", "super_admin"],
    },
    "/testsuper": {
        "desc": "超级管理员测试用指令",
        "func": cmd_testsuper,
        "broadcast": False,
        "save": False,
        "permission": ["super_admin"],
    },
}
