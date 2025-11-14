# routes/chat.py
from flask import Blueprint, request, jsonify
from models.db import db
from models.user import User
from models.chat_history import ChatHistory
from utils.firebase_auth import verify_firebase_token
from utils.helpers import check_and_reset_daily_limit
from utils.mistral_chat import MistralChatManager

chat_bp = Blueprint('chat', __name__)
mistral_chat = MistralChatManager()

@chat_bp.route('/api/chat', methods=['POST'])
@verify_firebase_token
def chat_with_ai():
    data = request.json
    user_message = data.get('message', '').strip()
    if not user_message:
        return jsonify({'success': False, 'error': 'Message required'}), 400

    uid = request.firebase_user['uid']
    email = request.firebase_user.get('email')

    with db.session.no_autoflush:
        user = User.query.filter_by(firebase_uid=uid).first()
        if not user:
            user = User(firebase_uid=uid, email=email or f'user_{uid}@unknown')
            db.session.add(user)
            db.session.commit()

        reset_occurred = check_and_reset_daily_limit(user)
        db.session.refresh(user)

    response_text, is_image, image_prompt = mistral_chat.chat(user_message, data.get('conversation_history', []))

    if is_image and image_prompt:
        if not user.is_pro and user.prompt_count >= 5:
            limit_msg = "Free limit reached (5/day). Upgrade to Pro!"
            entry = ChatHistory(user_id=user.id, user_message=user_message, ai_response=limit_msg, message_type='text')
            db.session.add(entry)
            db.session.commit()
            return jsonify({'success': True, 'response': limit_msg + " [Upgrade](/upgrade)", 'needs_upgrade': True})

        friendly = mistral_chat.generate_acknowledgment(user_message)
        entry = ChatHistory(user_id=user.id, user_message=user_message, ai_response=friendly,
                            image_prompt=image_prompt, message_type='image')
        db.session.add(entry)
        db.session.commit()

        return jsonify({
            'success': True, 'response': friendly, 'is_image_request': True,
            'image_prompt': image_prompt, 'needs_generation': True,
            'chat_entry_id': entry.id, 'remaining_prompts': None if user.is_pro else (5 - user.prompt_count)
        })

    entry = ChatHistory(user_id=user.id, user_message=user_message, ai_response=response_text, message_type='text')
    db.session.add(entry)
    db.session.commit()

    return jsonify({'success': True, 'response': response_text, 'is_image_request': False})