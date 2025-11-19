# routes/chat.py
from flask import Blueprint, request, jsonify
from models.db import db
from models.user import User
from models.chat_history import ChatHistory
from utils.firebase_auth import verify_firebase_token
from utils.helpers import check_and_reset_daily_limit
from utils.mistral_chat import MistralChatManager
from utils.logo_agent import LogoReferenceAgent
from PIL import Image
import requests
import io

chat_bp = Blueprint('chat', __name__)
mistral_chat = MistralChatManager()
logo_agent = LogoReferenceAgent()

# Store reference images for each user (in production, use Redis or database)
user_reference_images = {}  # uid -> PIL.Image

@chat_bp.route('/api/chat', methods=['POST'])
@verify_firebase_token
def chat_with_ai():
    data = request.json
    user_message = data.get('message', '').strip()
    use_web_search = data.get('use_web_search', False)
    conversation_id = data.get('conversation_id')
    
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

    # Check for photo search if web search is enabled
    if use_web_search:
        # Check if there's a pending photo request (confirmation/refinement)
        if uid in mistral_chat.pending_photo_requests:
            user_msg_lower = user_message.lower().strip()
            
            # Check if user selected a specific image by index
            import re
            index_match = re.search(r'use image (\d+)', user_msg_lower)
            selected_index = int(index_match.group(1)) if index_match else 0
            
            # Confirmation keywords
            if any(keyword in user_msg_lower for keyword in ['yes', 'correct', 'use image', 'this is correct', 'looks good', 'perfect', 'use it', '✅']):
                photo_data = mistral_chat.pending_photo_requests.pop(uid)
                results = photo_data.get('results', [])
                
                if results and selected_index < len(results):
                    selected_photo = results[selected_index]
                    
                    # Download and store the image as reference for IP-Adapter
                    try:
                        image_url = selected_photo.get('image_url')
                        hostname = selected_photo.get('hostname', 'web')
                        
                        # Download image with headers to avoid blocking
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                        response = requests.get(image_url, timeout=15, headers=headers, stream=True)
                        response.raise_for_status()
                        
                        # Open and validate image
                        reference_img = Image.open(io.BytesIO(response.content))
                        reference_img = reference_img.convert('RGB')
                        
                        # Validate image size
                        if reference_img.size[0] < 50 or reference_img.size[1] < 50:
                            raise ValueError(f"Image too small: {reference_img.size}")
                        
                        # Store in memory
                        user_reference_images[uid] = reference_img
                        
                        return jsonify({
                            'success': True,
                            'response': f"Perfect! I've saved this logo from **{hostname}** as your reference image. 🎨\n\nNow, please describe the logo you want me to create!",
                            'is_image_request': False,
                            'photo_confirmed': True
                        })
                    except Exception as e:
                        return jsonify({
                            'success': True,
                            'response': f"I had trouble downloading the image. Please try searching again or describe your logo directly! 🎨",
                            'is_image_request': False
                        })
            
            # Refinement/rejection keywords
            elif any(keyword in user_msg_lower for keyword in ['no', 'different', 'search again', '❌', 'wrong']):
                original_query = mistral_chat.pending_photo_requests[uid].get('query', '')
                mistral_chat.pending_photo_requests.pop(uid)
                
                # Extract new search terms or use original
                new_query = mistral_chat.extract_photo_search_query(user_message) or f"{original_query} alternative"
                
                # Search again
                try:
                    photo_result = logo_agent.search_for_photo(new_query)
                    if photo_result.get('success'):
                        preview_text = logo_agent.format_photo_preview(photo_result)
                        mistral_chat.pending_photo_requests[uid] = photo_result
                        
                        return jsonify({
                            'success': True,
                            'response': preview_text,
                            'is_image_request': False,
                            'awaiting_photo_confirmation': True,
                            'photo_result': photo_result
                        })
                    else:
                        return jsonify({
                            'success': True,
                            'response': f"❌ {photo_result.get('error', 'Search failed')}",
                            'is_image_request': False
                        })
                except Exception as e:
                    return jsonify({
                        'success': True,
                        'response': f"❌ Error searching for photo: {str(e)}",
                        'is_image_request': False
                    })
        
        # Check if this is a NEW photo search request
        elif mistral_chat.is_photo_search_request(user_message):
            search_query = mistral_chat.extract_photo_search_query(user_message)
            
            if search_query:
                try:
                    photo_result = logo_agent.search_for_photo(search_query)
                    
                    if photo_result.get('success'):
                        preview_text = logo_agent.format_photo_preview(photo_result)
                        mistral_chat.pending_photo_requests[uid] = photo_result
                        
                        return jsonify({
                            'success': True,
                            'response': preview_text,
                            'is_image_request': False,
                            'awaiting_photo_confirmation': True,
                            'photo_result': photo_result
                        })
                    else:
                        return jsonify({
                            'success': True,
                            'response': f"❌ {photo_result.get('error', 'Photo search failed')}",
                            'is_image_request': False
                        })
                except Exception as e:
                    # Fall through to normal Mistral response
                    pass

    response_text, is_image, image_prompt, logo_data = mistral_chat.chat(user_message, data.get('conversation_history', []), user_id=uid, use_web_search=use_web_search)

    if is_image and image_prompt:
        if not user.is_pro and user.prompt_count >= 5:
            limit_msg = "Free limit reached (5/day). Upgrade to Pro!"
            entry = ChatHistory(user_id=user.id, user_message=user_message, ai_response=limit_msg, message_type='text')
            db.session.add(entry)
            db.session.commit()
            return jsonify({'success': True, 'response': limit_msg + " [Upgrade](/upgrade)", 'needs_upgrade': True})

        friendly = mistral_chat.generate_acknowledgment(user_message)
        entry = ChatHistory(
            user_id=user.id, 
            user_message=user_message, 
            ai_response=response_text, 
            message_type='text',
            conversation_id=conversation_id  # Save conversation ID
        )
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