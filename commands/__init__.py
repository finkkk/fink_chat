# commands/__init__.py
from .common import COMMON_COMMANDS
from .admin  import ADMIN_COMMANDS
from .ai     import AI_COMMANDS
from config  import SYSTEM_USERNAME
from datetime import datetime,timezone

# ====== 合并所有命令 ======
AVAILABLE_COMMANDS = {
    **COMMON_COMMANDS,
    **ADMIN_COMMANDS,
    **AI_COMMANDS
}

# ====== 统一处理指令的方法 ======
def handle_command(command, args, username, role="user"):
    cmd_conf = AVAILABLE_COMMANDS.get(command)
    if not cmd_conf:
        return {
            'username': SYSTEM_USERNAME,
            'message': f'❓ 未知指令: {command}',
            'style': 'error',
            'is_ai_command': False,  # 报错属于非AI指令
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

    # ===== 调用对应函数 =====
    if command == "/help":
        result = cmd_conf['func'](username, args, role=role)
    else:
        result = cmd_conf['func'](username, args)

    # 添加统一字段
    result.update({
        'broadcast': cmd_conf.get('broadcast', True),
        'save': cmd_conf.get('save', False)
    })

    result.setdefault("timestamp", datetime.now(timezone.utc).isoformat())

    return result