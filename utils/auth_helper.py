# utils/auth_helper.py
from config import GUEST_USERNAME, SUPER_ADMIN_USERNAMES, ADMIN_USERNAMES


# ====== 验证权限并分配身份 ======
def get_user_role(username):
    if username.startswith(GUEST_USERNAME):  # 所有游客#x 都识别为 guest
        return "guest"
    elif username in SUPER_ADMIN_USERNAMES:
        return "super_admin"
    elif username in ADMIN_USERNAMES:
        return "admin"
    else:
        return "user"
