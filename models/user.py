from .db import db

from datetime import datetime
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    firebase_uid = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    fname = db.Column(db.String(64), nullable=True)
    lname = db.Column(db.String(64), nullable=True)
    is_pro = db.Column(db.Boolean, default=False)
    prompt_count = db.Column(db.Integer, default=0)
    last_prompt_reset = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    chat_history = db.relationship('ChatHistory', backref='user', lazy=True)

    @property
    def full_name(self):
        parts = []
        if self.fname:
            parts.append(self.fname)
        if self.lname:
            parts.append(self.lname)
        return ' '.join(parts) if parts else None

    @property
    def initials(self):
        first = (self.fname or '').strip()
        last = (self.lname or '').strip()
        if first or last:
            return ((first[:1] or '') + (last[:1] or '')).upper()
        return 'AI'