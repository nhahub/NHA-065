# routes/generate.py
from flask import Blueprint, request, jsonify, send_from_directory
from models.db import db
from models.user import User
from models.chat_history import ChatHistory
from utils.model_manager import ModelManager
from utils.firebase_auth import verify_firebase_token
from utils.helpers import check_and_reset_daily_limit
from config import config
from datetime import datetime
import base64
import io
from PIL import Image
import os

generate_bp = Blueprint('generate', __name__)
model_manager = ModelManager()

# Import the shared user_reference_images from chat route
# This is a temporary solution - in production, use Redis or database
from routes.chat import user_reference_images

@generate_bp.route('/api/generate-from-chat', methods=['POST'])
@verify_firebase_token
def generate_from_chat():
    data = request.json
    image_prompt = data.get('image_prompt', '').strip()
    chat_entry_id = data.get('chat_entry_id')
    conversation_id = data.get('conversation_id')  # ✅ Get conversation_id from request

    if not image_prompt:
        return jsonify({'success': False, 'error': 'Prompt required'}), 400
    
    # ✅ CRITICAL: Ensure conversation_id is never None
    if not conversation_id:
        # Generate a fallback conversation_id if somehow missing
        import time
        import random
        import string
        timestamp = int(time.time() * 1000)
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
        conversation_id = f"conv_{timestamp}_{random_suffix}"
        print(f"⚠️  Warning: No conversation_id provided, generated fallback: {conversation_id}")

    uid = request.firebase_user['uid']
    user = User.query.filter_by(firebase_uid=uid).with_for_update().first()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    check_and_reset_daily_limit(user)
    if not user.is_pro and user.prompt_count >= 5:
        return jsonify({'success': False, 'error': 'Limit reached', 'remaining_prompts': 0}), 403

    try:
        # Check if user has a stored reference image from web search
        reference_image = user_reference_images.get(uid)
        use_ip_adapter_auto = reference_image is not None
        ip_adapter_scale_auto = 0.6 if reference_image else 0.5  # Higher influence for web references
        
        # Extract only the parameters needed for generation
        gen_params = {
            'use_lora': data.get('use_lora', False),
            'lora_filename': data.get('lora_filename'),
            'num_steps': data.get('num_steps'),
            'width': data.get('width'),
            'height': data.get('height'),
            'use_ip_adapter': data.get('use_ip_adapter', False) or use_ip_adapter_auto,
            'ip_adapter_scale': ip_adapter_scale_auto if reference_image else data.get('ip_adapter_scale', 0.5),
            'reference_image': reference_image if reference_image else data.get('reference_image')
        }
        
        # Remove None values
        gen_params = {k: v for k, v in gen_params.items() if v is not None}
        
        # Generate image with explicit parameters only
        image = model_manager.generate_image(prompt=image_prompt, **gen_params)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"logo_{timestamp}.{config.IMAGE_FORMAT.lower()}"
        path = os.path.join(config.OUTPUTS_DIR, filename)
        if config.SAVE_GENERATED_IMAGES:
            image.save(path, format=config.IMAGE_FORMAT)

        buffered = io.BytesIO()
        image.save(buffered, format=config.IMAGE_FORMAT)
        img_str = base64.b64encode(buffered.getvalue()).decode()

        if chat_entry_id:
            entry = ChatHistory.query.get(chat_entry_id)
            if entry and entry.user_id == user.id:
                entry.image_path = path
                entry.image_prompt = image_prompt
            else:
                entry = ChatHistory(
                    user_id=user.id,
                    user_message="Generated image",
                    ai_response="Image",
                    image_path=path,
                    image_prompt=image_prompt,
                    message_type='image',
                    conversation_id=conversation_id  # ✅ Add conversation_id
                )
                db.session.add(entry)
        else:
            entry = ChatHistory(
                user_id=user.id,
                user_message="Generated image",
                ai_response="Image",
                image_path=path,
                image_prompt=image_prompt,
                message_type='image',
                conversation_id=conversation_id  # ✅ Add conversation_id
            )
            db.session.add(entry)

        old_count = user.prompt_count
        user.prompt_count += 1
        db.session.commit()
        
        # Clear the reference image after successful generation to save memory
        if uid in user_reference_images:
            del user_reference_images[uid]

        # Build metadata with LoRA info if used
        metadata = {
            'model': config.BASE_MODEL_ID,
            'steps': gen_params.get('num_steps', config.DEFAULT_GENERATION_PARAMS['num_inference_steps']),
            'dimensions': f"{gen_params.get('width', 1024)}x{gen_params.get('height', 1024)}",
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Add LoRA info if used
        if gen_params.get('use_lora') and gen_params.get('lora_filename'):
            metadata['lora'] = gen_params.get('lora_filename')
            metadata['model'] = f"{config.BASE_MODEL_ID} + LoRA"
        
        # Add IP-Adapter info if used
        if gen_params.get('use_ip_adapter'):
            metadata['ip_adapter_scale'] = gen_params.get('ip_adapter_scale', 0.5)
        
        return jsonify({
            'success': True,
            'image': f"data:image/{config.IMAGE_FORMAT.lower()};base64,{img_str}",
            'filename': filename,
            'remaining_prompts': None if user.is_pro else (5 - user.prompt_count),
            'metadata': metadata,
            'debug': {'old_count': old_count, 'new_count': user.prompt_count}
        })

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@generate_bp.route('/outputs/<filename>')
def serve_output(filename):
    return send_from_directory(config.OUTPUTS_DIR, filename)