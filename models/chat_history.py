from .db import db
from datetime import datetime

class ChatHistory(db.Model):
    __tablename__ = 'chat_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # User's message
    user_message = db.Column(db.Text, nullable=False)
    
    # AI's response (can be text or indication of image generation)
    ai_response = db.Column(db.Text, nullable=True)
    
    # Image-related fields
    image_prompt = db.Column(db.Text, nullable=True)  # The refined prompt used for generation
    image_path = db.Column(db.String(255), nullable=True)  # Path to generated image
    
    # Message type: 'text' or 'image'
    message_type = db.Column(db.String(20), default='text')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)