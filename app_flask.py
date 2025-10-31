"""
Zypher AI Logo Generator - Flask Backend
ChatGPT-style interface with modern API
"""
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
from datetime import datetime
from PIL import Image
import io
import base64
import json
from models import db, User
from utils.firebase_auth import verify_firebase_token, get_request_uid

# Add utils to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from utils.model_manager import ModelManager
from utils.chat_history import ChatHistoryManager
from utils.firebase_auth import verify_firebase_token, initialize_firebase
from utils.mistral_chat import MistralChatManager
import models


app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
CORS(app)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
models.db.init_app(app)

# Initialize Firebase admin if configured
initialize_firebase()

# Create DB tables if they don't exist (simple auto-create for development)
with app.app_context():
    try:
        models.db.create_all()
    except Exception as e:
        # ignore creation errors in constrained environments
        print('Warning: could not create DB tables:', e)

# Initialize managers
model_manager = ModelManager()
chat_history = ChatHistoryManager()
mistral_chat = MistralChatManager()


@app.route('/')
def index():
    """Serve the main ChatGPT-style interface"""
    return render_template('index.html')


@app.route('/login')
def login_page():
    return render_template('login.html')


@app.route('/signup')
def signup_page():
    return render_template('signup.html')


@app.route('/photos/<path:filename>')
def serve_photos(filename):
    """Serve files from the top-level photos/ folder (allows using existing F:/.../photos/favicon.ico)."""
    photos_dir = os.path.join(config.BASE_DIR, 'photos')
    return send_from_directory(photos_dir, filename)


@app.route('/api/firebase-config', methods=['GET'])
def firebase_config():
    """Return frontend Firebase client config from environment (non-secret)"""
    try:
        return jsonify({'success': True, 'config': config.FIREBASE_CLIENT_CONFIG})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Ensure user table has fname/lname columns (SQLite-friendly)
def ensure_user_columns():
    try:
        from sqlalchemy import text
        with app.app_context():
            conn = models.db.engine.connect()
            result = conn.execute(text("PRAGMA table_info('users')"))
            cols = [row['name'] if isinstance(row, dict) else row[1] for row in result]
            # Add fname and lname if missing
            if 'fname' not in cols:
                try:
                    conn.execute(text("ALTER TABLE users ADD COLUMN fname TEXT"))
                except Exception:
                    pass
            if 'lname' not in cols:
                try:
                    conn.execute(text("ALTER TABLE users ADD COLUMN lname TEXT"))
                except Exception:
                    pass
            # Add last_prompt_reset if missing (store as TEXT for broad DB compatibility)
            if 'last_prompt_reset' not in cols:
                try:
                    conn.execute(text("ALTER TABLE users ADD COLUMN last_prompt_reset TEXT"))
                except Exception:
                    pass
            conn.close()
    except Exception:
        pass


# Profile endpoints for getting/updating user's display name
@app.route('/api/user/profile', methods=['GET'])
@verify_firebase_token
def get_user_profile():
    try:
        firebase_user = getattr(request, 'firebase_user', None)
        if not firebase_user:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        uid = firebase_user.get('uid')
        with app.app_context():
            user = models.User.query.filter_by(firebase_uid=uid).first()
            if not user:
                return jsonify({'success': True, 'profile': {'fname': None, 'lname': None, 'email': firebase_user.get('email'), 'is_pro': False, 'prompt_count': 0}})
            return jsonify({'success': True, 'profile': {'fname': user.fname, 'lname': user.lname, 'email': user.email, 'is_pro': bool(user.is_pro), 'prompt_count': int(user.prompt_count)}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/user/profile', methods=['POST'])
@verify_firebase_token
def update_user_profile():
    try:
        data = request.get_json() or {}
        fname = data.get('fname')
        lname = data.get('lname')
        firebase_user = getattr(request, 'firebase_user', None)
        if not firebase_user:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        uid = firebase_user.get('uid')
        with app.app_context():
            user = models.User.query.filter_by(firebase_uid=uid).first()
            if not user:
                user = models.User(firebase_uid=uid, email=firebase_user.get('email') or f'user_{uid}@unknown')
                models.db.session.add(user)
            user.fname = fname
            user.lname = lname
            models.db.session.commit()
            return jsonify({'success': True, 'profile': {'fname': user.fname, 'lname': user.lname, 'email': user.email}})
    except Exception as e:
        models.db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/upgrade')
def upgrade_page():
    """Render a simple upgrade page describing Free vs Pro plans."""
    return render_template('upgrade.html')

@app.route('/get-user-email', methods=['GET'])
@verify_firebase_token
def get_user_email():
    try:
        uid = get_request_uid()
        user = models.User.query.filter_by(firebase_uid=uid).first()
        if not user:
            # Fallback for new users not yet in DB
            firebase_user = getattr(request, 'firebase_user', {})
            return jsonify({'success': True, 'email': firebase_user.get('email', 'Not found')})
        
        return jsonify({'success': True, 'email': user.email})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/payment/success', methods=['POST'])
@verify_firebase_token
def payment_success():
    try:
        firebase_user = getattr(request, 'firebase_user', None)
        if not firebase_user:
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        
        uid = firebase_user.get('uid')
        email = firebase_user.get('email', f'user_{uid}@unknown')
        
        with app.app_context():
            user = models.User.query.filter_by(firebase_uid=uid).first()
            if not user:
                user = models.User(firebase_uid=uid, email=email)
                db.session.add(user)
                db.session.commit()  # Commit creation before updating is_pro
            
            user.is_pro = True
            db.session.commit()
        
        return jsonify({'success': True, 'message': 'Upgrade successful'})
    
    except Exception as e:
        db.session.rollback()
        print(f"Error during payment success: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/api/chat', methods=['POST'])
@verify_firebase_token
def chat_with_ai():
    """
    Chat with Mistral AI - handles both normal conversation and image generation detection
    """
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        conversation_history = data.get('conversation_history', [])
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        # Get authenticated user
        firebase_user = getattr(request, 'firebase_user', None)
        if not firebase_user:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        uid = firebase_user.get('uid')
        email = firebase_user.get('email')
        
        # Get or create user record
        with app.app_context():
            user = models.User.query.filter_by(firebase_uid=uid).first()
            if not user:
                user = models.User(firebase_uid=uid, email=email or f'user_{uid}@unknown')
                models.db.session.add(user)
                models.db.session.commit()
            
            # Reset prompt count check BEFORE checking limits
            try:
                now = datetime.utcnow()
                needs_reset = False
                last = user.last_prompt_reset
                
                if not last:
                    needs_reset = True
                else:
                    try:
                        if isinstance(last, str):
                            last_dt = datetime.fromisoformat(last)
                        else:
                            last_dt = last
                        if (now - last_dt).total_seconds() >= 24 * 3600:
                            needs_reset = True
                    except Exception:
                        needs_reset = True
                
                if needs_reset:
                    user.prompt_count = 0
                    user.last_prompt_reset = now
                    models.db.session.commit()
            except Exception as e:
                print(f"Reset check error: {e}")
                pass
        
        # Chat with Mistral AI
        response_text, is_image_request, image_prompt = mistral_chat.chat(
            user_message, 
            conversation_history
        )
        
        # If Mistral detected an image generation request
        if is_image_request and image_prompt:
            # Check user limits BEFORE allowing generation
            with app.app_context():
                user = models.User.query.filter_by(firebase_uid=uid).first()
                
                # Check limits - BLOCK if at limit
                if not user.is_pro and (user.prompt_count or 0) >= 5:
                    return jsonify({
                        'success': True,
                        'response': "🎨 I'd love to help you create that! However, you've reached your free tier limit of 5 image generations per day. Upgrade to Pro for unlimited generations! [Upgrade to Pro](/upgrade)",
                        'is_image_request': True,
                        'needs_upgrade': True,
                        'needs_generation': False  # 🎯 Don't allow generation
                    })
            
            # Generate a friendly, personalized acknowledgment using Mistral
            friendly_response = mistral_chat.generate_acknowledgment(user_message)
            
            # Return immediate acknowledgment with generation status
            return jsonify({
                'success': True,
                'response': friendly_response,
                'is_image_request': True,
                'image_prompt': image_prompt,
                'status': 'generating',
                'needs_generation': True  # Allow generation
            })
        
        # Normal chat response (no image generation)
        return jsonify({
            'success': True,
            'response': response_text,
            'is_image_request': False
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/generate-from-chat', methods=['POST'])
@verify_firebase_token
def generate_from_chat():
    """
    Generate image from chat-detected prompt
    This is called after the user gets the "Generating..." message
    """
    try:
        data = request.json
        image_prompt = data.get('image_prompt', '').strip()
        
        if not image_prompt:
            return jsonify({
                'success': False,
                'error': 'Image prompt is required'
            }), 400
        
        # Get generation settings from request (with defaults)
        use_lora = data.get('use_lora', False)
        lora_filename = data.get('lora_filename', None)
        num_steps = data.get('num_steps', 4)
        width = data.get('width', 1024)
        height = data.get('height', 1024)
        use_ip_adapter = data.get('use_ip_adapter', False)
        ip_adapter_scale = data.get('ip_adapter_scale', 0.5)
        
        # Get authenticated user
        firebase_user = getattr(request, 'firebase_user', None)
        if not firebase_user:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        uid = firebase_user.get('uid')
        
        # Get user record
        with app.app_context():
            user = models.User.query.filter_by(firebase_uid=uid).first()
            if not user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
            
            # Double-check limits before actual generation
            # Reset check
            try:
                now = datetime.utcnow()
                needs_reset = False
                last = user.last_prompt_reset
                
                if not last:
                    needs_reset = True
                else:
                    try:
                        if isinstance(last, str):
                            last_dt = datetime.fromisoformat(last)
                        else:
                            last_dt = last
                        if (now - last_dt).total_seconds() >= 24 * 3600:
                            needs_reset = True
                    except Exception:
                        needs_reset = True
                
                if needs_reset:
                    user.prompt_count = 0
                    user.last_prompt_reset = now
                    models.db.session.commit()
            except Exception as e:
                print(f"Reset check error: {e}")
                pass
            
            # BLOCK generation if at limit
            if not user.is_pro and (user.prompt_count or 0) >= 5:
                return jsonify({
                    'success': False,
                    'error': 'Free tier limit reached (5 images per day). Please upgrade to Pro for unlimited generations.'
                }), 403
        
        # Generate the image with user settings
        try:
            image = model_manager.generate_image(
                prompt=image_prompt,
                use_lora=use_lora,
                lora_filename=lora_filename,
                num_inference_steps=num_steps,
                width=width,
                height=height
            )
            
            # Save image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"logo_{timestamp}.{config.IMAGE_FORMAT.lower()}"
            image_path = os.path.join(config.OUTPUTS_DIR, filename)
            
            if config.SAVE_GENERATED_IMAGES:
                image.save(image_path, format=config.IMAGE_FORMAT)
            
            # Convert to base64
            buffered = io.BytesIO()
            image.save(buffered, format=config.IMAGE_FORMAT)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Save to history
            try:
                chat_history.add_entry(image_prompt, image_path, False)
            except Exception:
                pass
            
            # Save to database AND increment count in ONE transaction
            try:
                with app.app_context():
                    # Refresh user object to avoid stale data
                    user = models.User.query.filter_by(firebase_uid=uid).first()
                    
                    entry = models.ChatHistory(user_id=user.id, prompt=image_prompt, image_path=image_path)
                    models.db.session.add(entry)
                    
                    # Increment count
                    user.prompt_count = (user.prompt_count or 0) + 1
                    
                    # Commit both together
                    models.db.session.commit()
                    
                    print(f"✅ User {user.email} prompt count: {user.prompt_count}/5")
            except Exception as e:
                print(f"❌ Database error: {e}")
                models.db.session.rollback()
            
            # Build model description
            model_parts = []
            if use_lora:
                lora_name = lora_filename or "Custom LoRA"
                model_parts.append(f"LoRA: {lora_name}")
            else:
                model_parts.append("Base Flux Schnell")
            if use_ip_adapter:
                model_parts.append(f"IP-Adapter ({ip_adapter_scale:.1%})")
            model_desc = " + ".join(model_parts)
            
            # Return success with image
            return jsonify({
                'success': True,
                'image': f"data:image/{config.IMAGE_FORMAT.lower()};base64,{img_str}",
                'filename': filename,
                'path': image_path,
                'metadata': {
                    'model': model_desc,
                    'lora_used': lora_filename if use_lora else None,
                    'steps': num_steps,
                    'dimensions': f'{width}×{height}',
                    'ip_adapter': use_ip_adapter,
                    'ip_adapter_scale': ip_adapter_scale if use_ip_adapter else None,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            })
            
        except Exception as e:
            print(f"Generation error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/generate', methods=['POST'])
@verify_firebase_token
def generate_logo():
    """
    Generate logo from prompt with optional reference image
    Endpoint: POST /api/generate
    Content-Type: multipart/form-data or application/json
    
    Form Data / JSON Body: {
        "prompt": "string",
        "use_lora": boolean,
        "num_steps": int,
        "width": int,
        "height": int,
        "use_ip_adapter": boolean (optional),
        "ip_adapter_scale": float (optional, 0.0-1.0),
        "reference_image": file (optional, for multipart/form-data)
    }
    """
    try:
        # Handle both JSON and form data
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Form data with file upload
            prompt = request.form.get('prompt', '').strip()
            use_lora = request.form.get('use_lora', 'false').lower() == 'true'
            lora_filename = request.form.get('lora_filename', None)
            num_steps = int(request.form.get('num_steps', 4))
            width = int(request.form.get('width', 1024))
            height = int(request.form.get('height', 1024))
            use_ip_adapter = request.form.get('use_ip_adapter', 'false').lower() == 'true'
            ip_adapter_scale = float(request.form.get('ip_adapter_scale', 0.5))
            
            # Get reference image if uploaded
            reference_image = None
            if use_ip_adapter and 'reference_image' in request.files:
                file = request.files['reference_image']
                if file and file.filename:
                    reference_image = Image.open(file.stream).convert('RGB')
        else:
            # JSON data
            data = request.json
            prompt = data.get('prompt', '').strip()
            use_lora = data.get('use_lora', False)
            lora_filename = data.get('lora_filename', None)
            num_steps = data.get('num_steps', 4)
            width = data.get('width', 1024)
            height = data.get('height', 1024)
            use_ip_adapter = data.get('use_ip_adapter', False)
            ip_adapter_scale = data.get('ip_adapter_scale', 0.5)
            
            # Handle base64 encoded reference image
            reference_image = None
            if use_ip_adapter and 'reference_image_base64' in data:
                import base64
                img_data = base64.b64decode(data['reference_image_base64'].split(',')[1])
                reference_image = Image.open(io.BytesIO(img_data)).convert('RGB')
        
        if not prompt:
            return jsonify({
                'success': False,
                'error': 'Prompt is required'
            }), 400

        # Associate request with authenticated Firebase user
        firebase_user = getattr(request, 'firebase_user', None)
        if firebase_user is None:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        uid = firebase_user.get('uid')
        email = firebase_user.get('email')

        # Get or create local User record
        with app.app_context():
            user = models.User.query.filter_by(firebase_uid=uid).first()
            if not user:
                user = models.User(firebase_uid=uid, email=email or f'user_{uid}@unknown')
                models.db.session.add(user)
                models.db.session.commit()

            # Reset prompt_count if it's been more than 24 hours since last reset
            try:
                now = datetime.utcnow()
                needs_reset = False
                last = user.last_prompt_reset
                if not last:
                    needs_reset = True
                else:
                    try:
                        # handle string stored in TEXT column or a datetime object
                        if isinstance(last, str):
                            last_dt = datetime.fromisoformat(last)
                        else:
                            last_dt = last
                        if (now - last_dt).total_seconds() >= 24 * 3600:
                            needs_reset = True
                    except Exception:
                        # if parse fails, reset to be safe
                        needs_reset = True

                if needs_reset:
                    user.prompt_count = 0
                    user.last_prompt_reset = now
                    models.db.session.commit()
            except Exception:
                # don't block request on reset failures
                pass

            # Enforce free-user prompt limit (example: 5 prompts). is_admin removed — pro is the only unlimited plan.
            if not user.is_pro and (user.prompt_count or 0) >= 5:
                return jsonify({'success': False, 'error': 'Free user limit reached. Upgrade to Pro.'}), 403
        
        # Generate image
        image = model_manager.generate_image(
            prompt=prompt,
            use_lora=use_lora,
            lora_filename=lora_filename,
            reference_image=reference_image if use_ip_adapter else None,
            ip_adapter_scale=ip_adapter_scale if use_ip_adapter else 0.5,
            num_inference_steps=num_steps,
            width=width,
            height=height
        )
        
        # Save image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"logo_{timestamp}.{config.IMAGE_FORMAT.lower()}"
        image_path = os.path.join(config.OUTPUTS_DIR, filename)
        
        if config.SAVE_GENERATED_IMAGES:
            image.save(image_path, format=config.IMAGE_FORMAT)
        
        # Convert image to base64 for response
        buffered = io.BytesIO()
        image.save(buffered, format=config.IMAGE_FORMAT)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Add to chat history (legacy JSON manager)
        try:
            chat_history.add_entry(prompt, image_path, use_lora)
        except Exception:
            pass

        # Also persist per-user entry in the SQL database
        try:
            with app.app_context():
                entry = models.ChatHistory(user_id=user.id, prompt=prompt, image_path=image_path)
                models.db.session.add(entry)
                # increment prompt count for user
                user.prompt_count = (user.prompt_count or 0) + 1
                models.db.session.commit()
        except Exception:
            # don't fail the whole request if DB write fails
            models.db.session.rollback()
        
        # Build model description
        model_parts = []
        if use_lora:
            lora_name = lora_filename or "Custom LoRA"
            model_parts.append(f"LoRA: {lora_name}")
        else:
            model_parts.append("Base Flux Schnell")
        if use_ip_adapter:
            model_parts.append(f"IP-Adapter ({ip_adapter_scale:.1%})")
        model_desc = " + ".join(model_parts)
        
        # Return response
        return jsonify({
            'success': True,
            'image': f"data:image/{config.IMAGE_FORMAT.lower()};base64,{img_str}",
            'filename': filename,
            'path': image_path,
            'metadata': {
                'model': model_desc,
                'lora_used': lora_filename if use_lora else None,
                'steps': num_steps,
                'dimensions': f"{width}×{height}",
                'ip_adapter': use_ip_adapter,
                'ip_adapter_scale': ip_adapter_scale if use_ip_adapter else None,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/history', methods=['GET'])
@verify_firebase_token
def get_history():
    """Get user's chat history from database"""
    try:
        firebase_user = getattr(request, 'firebase_user', None)
        if not firebase_user:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        uid = firebase_user.get('uid')
        
        with app.app_context():
            user = models.User.query.filter_by(firebase_uid=uid).first()
            if not user:
                return jsonify({'success': True, 'history': []})
            
            # Get all chat history for this user, ordered by most recent first
            history_entries = models.ChatHistory.query.filter_by(user_id=user.id)\
                .order_by(models.ChatHistory.created_at.desc())\
                .limit(50)\
                .all()
            
            history = []
            for entry in history_entries:
                history.append({
                    'id': entry.id,
                    'prompt': entry.prompt,
                    'image_path': entry.image_path,
                    'timestamp': entry.created_at.isoformat() if entry.created_at else None,
                    'preview': entry.prompt[:50] + ('...' if len(entry.prompt) > 50 else '')
                })
            
            return jsonify({
                'success': True,
                'history': history
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/history/<int:history_id>', methods=['GET'])
@verify_firebase_token
def get_history_item(history_id):
    """Get a specific chat history item"""
    try:
        firebase_user = getattr(request, 'firebase_user', None)
        if not firebase_user:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        uid = firebase_user.get('uid')
        
        with app.app_context():
            user = models.User.query.filter_by(firebase_uid=uid).first()
            if not user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
            
            # Get the specific history entry, ensuring it belongs to this user
            entry = models.ChatHistory.query.filter_by(id=history_id, user_id=user.id).first()
            if not entry:
                return jsonify({'success': False, 'error': 'History item not found'}), 404
            
            return jsonify({
                'success': True,
                'item': {
                    'id': entry.id,
                    'prompt': entry.prompt,
                    'image_path': entry.image_path,
                    'timestamp': entry.created_at.isoformat() if entry.created_at else None
                }
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/history/<int:history_id>', methods=['DELETE'])
@verify_firebase_token
def delete_history_item(history_id):
    """Delete a specific chat history item"""
    try:
        firebase_user = getattr(request, 'firebase_user', None)
        if not firebase_user:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        uid = firebase_user.get('uid')
        
        with app.app_context():
            user = models.User.query.filter_by(firebase_uid=uid).first()
            if not user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
            
            # Get the specific history entry, ensuring it belongs to this user
            entry = models.ChatHistory.query.filter_by(id=history_id, user_id=user.id).first()
            if not entry:
                return jsonify({'success': False, 'error': 'History item not found'}), 404
            
            # Delete the entry
            models.db.session.delete(entry)
            models.db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'History item deleted successfully'
            })
    except Exception as e:
        models.db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/history/clear', methods=['POST'])
@verify_firebase_token
def clear_history():
    """Clear all chat history for the user"""
    try:
        firebase_user = getattr(request, 'firebase_user', None)
        if not firebase_user:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        uid = firebase_user.get('uid')
        
        with app.app_context():
            user = models.User.query.filter_by(firebase_uid=uid).first()
            if not user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
            
            # Delete all history entries for this user
            models.ChatHistory.query.filter_by(user_id=user.id).delete()
            models.db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'All history cleared successfully'
            })
    except Exception as e:
        models.db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/model/status', methods=['GET'])
def model_status():
    """Get model status"""
    try:
        info = model_manager.get_model_info()
        return jsonify({
            'success': True,
            'model': info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/model/loras', methods=['GET'])
def list_loras():
    """Get list of available LoRA models"""
    try:
        loras = model_manager.get_available_loras()
        current_lora = model_manager.current_lora
        return jsonify({
            'success': True,
            'loras': loras,
            'current_lora': current_lora,
            'count': len(loras)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/outputs/<filename>')
def serve_output(filename):
    """Serve generated images"""
    return send_from_directory(config.OUTPUTS_DIR, filename)


if __name__ == '__main__':
    print(f"\n{'='*60}")
    print(f"🎨 {config.PROJECT_NAME} v{config.VERSION}")
    print(f"ChatGPT-Style Interface")
    print(f"{'='*60}\n")
    
    app.run(
        host='0.0.0.0',
        port=config.SERVER_PORT,
        debug=True
    )
