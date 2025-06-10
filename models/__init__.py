# models/__init__.py
from flask_sqlalchemy import SQLAlchemy

# 先实例化 db
db = SQLAlchemy()

# 再导入模型
from .user    import User  # noqa: E402, F401
from .message import Message  # noqa: E402, F401
