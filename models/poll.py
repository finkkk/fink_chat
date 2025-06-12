# models/poll.py
from . import db
from datetime import datetime, timezone,timedelta


# 定义投票数据库
class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)
    creator = db.Column(db.String(80), nullable=False)
    created_at  = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    options = db.relationship("Option", backref="poll", cascade="all, delete-orphan")
    @property
    def is_ended(self):
        ca = self.created_at
        # 如果读出来是 naive，就手动补个 UTC tzinfo
        if ca.tzinfo is None:
            ca = ca.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) >= ca + timedelta(days=3)
    

    
class Option(db.Model):
    __tablename__ = 'option'
    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey("poll.id"), nullable=False)
    text = db.Column(db.String(50), nullable=False)
    votes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))


class Vote(db.Model):
    __tablename__ = 'vote'
    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey("poll.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    option_idx = db.Column(db.Integer, nullable=False) # 0-based 选项索引
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    __table_args__ = (db.UniqueConstraint("poll_id", "user_id", name="uix_poll_user"),)
