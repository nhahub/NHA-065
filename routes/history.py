# routes/history.py
from flask import Blueprint, jsonify, request
from models.db import db
from models.user import User
from models.chat_history import ChatHistory
from utils.firebase_auth import verify_firebase_token, get_request_uid
from sqlalchemy import func

history_bp = Blueprint('history', __name__)


@history_bp.route('/api/history', methods=['GET'])
@verify_firebase_token
def get_history():
    """Get all conversations for the authenticated user (grouped)."""
    uid = get_request_uid()
    user = User.query.filter_by(firebase_uid=uid).first()
    
    if not user:
        return jsonify({'success': True, 'conversations': []})

    # Group by conversation_id and get the latest message from each
    conversations = db.session.query(
        ChatHistory.conversation_id,
        func.max(ChatHistory.created_at).label('last_updated'),
        func.count(ChatHistory.id).label('message_count')
    ).filter_by(
        user_id=user.id
    ).group_by(
        ChatHistory.conversation_id
    ).order_by(
        func.max(ChatHistory.created_at).desc()
    ).limit(50).all()
    
    # Get first user message from each conversation for preview
    conversation_list = []
    for conv in conversations:
        first_message = ChatHistory.query.filter_by(
            user_id=user.id,
            conversation_id=conv.conversation_id
        ).order_by(ChatHistory.created_at.asc()).first()
        
        conversation_list.append({
            'conversation_id': conv.conversation_id,
            'preview': (first_message.user_message or "New Chat")[:50] + "...",
            'message_count': conv.message_count,
            'last_updated': conv.last_updated.isoformat(),
            'timestamp': conv.last_updated.isoformat()
        })
    
    return jsonify({'success': True, 'conversations': conversation_list})

@history_bp.route('/api/history/<conversation_id>', methods=['GET'])
@verify_firebase_token
def get_conversation(conversation_id):
    """Get all messages in a specific conversation."""
    uid = get_request_uid()
    user = User.query.filter_by(firebase_uid=uid).first()
    
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    messages = ChatHistory.query.filter_by(
        user_id=user.id,
        conversation_id=conversation_id
    ).order_by(ChatHistory.created_at.asc()).all()
    
    if not messages:
        return jsonify({'success': False, 'error': 'Conversation not found'}), 404
    
    conversation_data = []
    for msg in messages:
        item = {
            'id': msg.id,
            'user_message': msg.user_message,
            'ai_response': msg.ai_response,
            'message_type': msg.message_type,
            'timestamp': msg.created_at.isoformat()
        }
        if msg.message_type == 'image':
            item.update({
                'image_prompt': msg.image_prompt,
                'image_path': msg.image_path
            })
        conversation_data.append(item)
    
    return jsonify({
        'success': True,
        'conversation_id': conversation_id,
        'messages': conversation_data
    })


@history_bp.route('/api/history/<int:history_id>', methods=['DELETE'])
@verify_firebase_token
def delete_history_item(history_id):
    """Delete a specific chat history item."""
    uid = get_request_uid()
    
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    history_item = ChatHistory.query.filter_by(id=history_id, user_id=user.id).first()
    
    if not history_item:
        return jsonify({'success': False, 'error': 'History item not found'}), 404
    
    db.session.delete(history_item)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'History item deleted'})


@history_bp.route('/api/history', methods=['DELETE'])
@verify_firebase_token
def clear_all_history():
    """Clear all chat history for the authenticated user."""
    uid = get_request_uid()
    
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        return jsonify({'success': True, 'message': 'No history to clear'})
    
    deleted_count = ChatHistory.query.filter_by(user_id=user.id).delete()
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': f'{deleted_count} history item(s) cleared'
    })


@history_bp.route('/api/history/search', methods=['GET'])
@verify_firebase_token
def search_history():
    """Search chat history by keyword."""
    uid = get_request_uid()
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'success': False, 'error': 'Search query required'}), 400
    
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        return jsonify({'success': True, 'history': []})
    
    # Search in user_message, ai_response, and image_prompt
    entries = ChatHistory.query.filter_by(user_id=user.id).filter(
        db.or_(
            ChatHistory.user_message.ilike(f'%{query}%'),
            ChatHistory.ai_response.ilike(f'%{query}%'),
            ChatHistory.image_prompt.ilike(f'%{query}%'),
            ChatHistory.prompt.ilike(f'%{query}%')
        )
    ).order_by(ChatHistory.created_at.desc()).limit(50).all()
    
    history = []
    for e in entries:
        item = {
            'id': e.id,
            'user_message': e.user_message or e.prompt or "Generated image",
            'ai_response': e.ai_response,
            'message_type': e.message_type or 'text',
            'timestamp': e.created_at.isoformat() if e.created_at else None,
            'preview': (e.user_message or e.ai_response or "")[:50] + "..."
        }
        if e.message_type == 'image':
            item.update({
                'image_prompt': e.image_prompt,
                'image_path': e.image_path
            })
        history.append(item)
    
    return jsonify({'success': True, 'history': history, 'query': query})


@history_bp.route('/api/history/stats', methods=['GET'])
@verify_firebase_token
def get_history_stats():
    """Get statistics about user's chat history."""
    uid = get_request_uid()
    
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        return jsonify({'success': True, 'stats': {
            'total_messages': 0,
            'text_messages': 0,
            'image_messages': 0
        }})
    
    total = ChatHistory.query.filter_by(user_id=user.id).count()
    text_count = ChatHistory.query.filter_by(user_id=user.id, message_type='text').count()
    image_count = ChatHistory.query.filter_by(user_id=user.id, message_type='image').count()
    
    # Get first message date
    first_message = ChatHistory.query.filter_by(user_id=user.id).order_by(ChatHistory.created_at.asc()).first()
    
    return jsonify({
        'success': True,
        'stats': {
            'total_messages': total,
            'text_messages': text_count,
            'image_messages': image_count,
            'first_message_date': first_message.created_at.isoformat() if first_message else None,
            'user_email': user.email,
            'is_pro': user.is_pro
        }
    })


@history_bp.route('/api/history/export', methods=['GET'])
@verify_firebase_token
def export_history():
    """Export all chat history as JSON."""
    uid = get_request_uid()
    
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        return jsonify({'success': True, 'history': []})
    
    entries = ChatHistory.query.filter_by(user_id=user.id).order_by(ChatHistory.created_at.desc()).all()
    
    history = []
    for e in entries:
        item = {
            'id': e.id,
            'user_message': e.user_message,
            'ai_response': e.ai_response,
            'prompt': e.prompt,
            'image_prompt': e.image_prompt,
            'image_path': e.image_path,
            'message_type': e.message_type,
            'timestamp': e.created_at.isoformat() if e.created_at else None
        }
        history.append(item)
    
    return jsonify({
        'success': True,
        'export_date': ChatHistory.query.first().created_at.isoformat() if ChatHistory.query.first() else None,
        'user_email': user.email,
        'total_items': len(history),
        'history': history
    })

@history_bp.route('/api/history/conversation/<conversation_id>', methods=['DELETE'])
@verify_firebase_token
def delete_conversation(conversation_id):
    """Delete an entire conversation and all its messages."""
    uid = get_request_uid()
    
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    # Delete all messages in this conversation
    deleted_count = ChatHistory.query.filter_by(
        user_id=user.id,
        conversation_id=conversation_id
    ).delete()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Deleted conversation with {deleted_count} messages',
        'deleted_count': deleted_count
    })