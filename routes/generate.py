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

@generate_bp.route('/api/generate-from-chat', methods=['POST'])
@verify_firebase_token
def generate_from_chat():
    data = request.json
    image_prompt = data.get('image_prompt', '').strip()
    chat_entry_id = data.get('chat_entry_id')

    if not image_prompt:
        return jsonify({'success': False, 'error': 'Prompt required'}), 400

    uid = request.firebase_user['uid']
    user = User.query.filter_by(firebase_uid=uid).with_for_update().first()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    check_and_reset_daily_limit(user)
    if not user.is_pro and user.prompt_count >= 5:
        return jsonify({'success': False, 'error': 'Limit reached', 'remaining_prompts': 0}), 403

    try:
        # Extract only the parameters needed for generation
        gen_params = {
            'use_lora': data.get('use_lora', False),
            'lora_filename': data.get('lora_filename'),
            'num_steps': data.get('num_steps'),
            'width': data.get('width'),
            'height': data.get('height'),
            'use_ip_adapter': data.get('use_ip_adapter', False),
            'ip_adapter_scale': data.get('ip_adapter_scale', 0.5),
            'reference_image': data.get('reference_image')
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
                    message_type='image'
                )
                db.session.add(entry)
        else:
            entry = ChatHistory(
                user_id=user.id,
                user_message="Generated image",
                ai_response="Image",
                image_path=path,
                image_prompt=image_prompt,
                message_type='image'
            )
            db.session.add(entry)

        old_count = user.prompt_count
        user.prompt_count += 1
        db.session.commit()

        return jsonify({
            'success': True,
            'image': f"data:image/{config.IMAGE_FORMAT.lower()};base64,{img_str}",
            'filename': filename,
            'remaining_prompts': None if user.is_pro else (5 - user.prompt_count),
            'metadata': {
                'model': config.BASE_MODEL_ID,
                'steps': gen_params.get('num_steps', config.DEFAULT_GENERATION_PARAMS['num_inference_steps']),
                'dimensions': f"{gen_params.get('width', 1024)}x{gen_params.get('height', 1024)}",
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
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