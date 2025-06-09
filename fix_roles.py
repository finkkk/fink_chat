from app import app, db, Message, get_user_role
from config import SYSTEM_USERNAME  # ← 加上这行

with app.app_context():
    messages = Message.query.all()
    updated = 0
    for msg in messages:
        if msg.username == SYSTEM_USERNAME:
            correct_role = "system"  # ← 明确标记系统身份
        else:
            correct_role = get_user_role(msg.username)
        if msg.role != correct_role:
            msg.role = correct_role
            updated += 1
    db.session.commit()
    print(f"✅ 修复完成，共更新 {updated} 条消息的 role 字段")