# models/__init__.py
from .db import db
from .user import User
from .chat_history import ChatHistory

__all__ = ['db', 'User', 'ChatHistory']