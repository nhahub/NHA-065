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
import requests
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

# Store reference images for each user (in production, use Redis or database)
user_reference_images = {}  # uid -> PIL.Image





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
        use_web_search = data.get('use_web_search', False)
        
        # Debug: Log web search toggle state
        print(f"🔍 DEBUG: use_web_search = {use_web_search}, message = '{user_message[:50]}...'")
        
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
        
        # Check for photo search BEFORE calling Mistral if web search is enabled
        if use_web_search:
            # Import here to avoid circular dependency
            from utils.logo_agent import LogoReferenceAgent
            logo_agent = LogoReferenceAgent()
            
            print(f"🔍 DEBUG: Web search enabled, checking if photo search request...")
            
            # First check if there's a pending photo request (confirmation/refinement)
            if uid and uid in mistral_chat.pending_photo_requests:
                print(f"✅ DEBUG: User has pending photo request, checking response...")
                user_msg_lower = user_message.lower().strip()
                
                # Check if user selected a specific image by index
                import re
                index_match = re.search(r'use image (\d+)', user_msg_lower)
                selected_index = int(index_match.group(1)) if index_match else 0
                
                # Confirmation keywords
                if any(keyword in user_msg_lower for keyword in ['yes', 'correct', 'use image', 'this is correct', 'looks good', 'perfect', 'use it', '✅']):
                        photo_data = mistral_chat.pending_photo_requests.pop(uid)
                        
                        # Get the selected result from the results array
                        results = photo_data.get('results', [])
                        if results and selected_index < len(results):
                            selected_photo = results[selected_index]
                            
                            # Download and store the image as reference for IP-Adapter
                            try:
                                image_url = selected_photo.get('image_url')
                                hostname = selected_photo.get('hostname', 'web')
                                
                                print(f"📥 Downloading reference image from: {image_url}")
                                
                                # Download image with headers to avoid blocking
                                headers = {
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                                }
                                response = requests.get(image_url, timeout=15, headers=headers, stream=True)
                                response.raise_for_status()
                                
                                print(f"✅ Downloaded {len(response.content)} bytes")
                                
                                # Open and validate image
                                reference_img = Image.open(io.BytesIO(response.content))
                                reference_img = reference_img.convert('RGB')  # Ensure RGB format
                                
                                # Validate image size (not too small)
                                if reference_img.size[0] < 50 or reference_img.size[1] < 50:
                                    raise ValueError(f"Image too small: {reference_img.size}")
                                
                                # Store in memory
                                user_reference_images[uid] = reference_img
                                print(f"✅ Reference image stored for user {uid} - Size: {reference_img.size}")
                                
                                return jsonify({
                                    'success': True,
                                    'response': f"Perfect! I've saved this logo from **{hostname}** as your reference image. 🎨\n\nNow, please describe the logo you want me to create! For example:\n- \"Create a modern tech startup logo\"\n- \"Design a minimalist coffee shop logo\"\n- \"Generate a bold fitness brand logo\"\n\nI'll use your reference image to guide the style and design! 💡",
                                    'is_image_request': False,
                                    'photo_confirmed': True,
                                    'reference_stored': True
                                })
                            except requests.exceptions.RequestException as e:
                                print(f"❌ Network error downloading reference image: {e}")
                                return jsonify({
                                    'success': True,
                                    'response': f"I had trouble downloading the image from **{hostname}** (network error). Please try searching again or describe your logo directly! 🎨",
                                    'is_image_request': False,
                                    'photo_confirmed': False
                                })
                            except Exception as e:
                                print(f"❌ Error processing reference image: {type(e).__name__}: {e}")
                                import traceback
                                traceback.print_exc()
                                return jsonify({
                                    'success': True,
                                    'response': f"I had trouble processing the image from **{hostname}**. Please try a different image or describe your logo directly! 🎨",
                                    'is_image_request': False,
                                    'photo_confirmed': False
                                })
                
                # Refinement/rejection keywords
                elif any(keyword in user_msg_lower for keyword in ['no', 'different', 'search again', '❌', 'wrong']):
                        # Remove pending request and search again
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
                            print(f"Error searching for photo: {e}")
                            return jsonify({
                                'success': True,
                                'response': f"❌ Error searching for photo: {str(e)}",
                                'is_image_request': False
                            })
            
            # Check if this is a NEW photo search request
            elif mistral_chat.is_photo_search_request(user_message):
                print(f"✅ DEBUG: Detected NEW photo search request!")
                
                search_query = mistral_chat.extract_photo_search_query(user_message)
                
                print(f"🔍 DEBUG: New photo search, extracted query: '{search_query}'")
                
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
                        print(f"Error in photo search: {e}")
                        # Fall through to normal Mistral response        # Chat with Mistral AI (pass user_id for logo confirmation tracking)
        response_text, is_image_request, image_prompt, extra_data = mistral_chat.chat(
            user_message, 
            conversation_history,
            user_id=uid,
            use_web_search=use_web_search  # Pass the actual toggle state
        )
        
        # If logo preview data is returned, send preview for confirmation
        if extra_data and not is_image_request and extra_data.get('request_data'):
            return jsonify({
                'success': True,
                'response': response_text,
                'is_image_request': False,
                'awaiting_confirmation': True,
                'logo_preview': {
                    'extracted_features': extra_data.get('extracted_visual_features', {}),
                    'final_prompt': extra_data.get('final_diffusion_prompt', ''),
                    'confidence': extra_data.get('confidence', 'medium'),
                    'search_results': extra_data.get('search_results', [])
                }
            })
        
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
            # Check if user has a stored reference image
            reference_image = user_reference_images.get(uid)
            use_ip_adapter_auto = reference_image is not None
            ip_adapter_scale_auto = 0.6 if reference_image else 0.5  # Higher influence for web references
            
            if reference_image:
                print(f"🎨 Using stored reference image for user {uid} with IP-Adapter (scale: {ip_adapter_scale_auto})")
            
            image = model_manager.generate_image(
                prompt=image_prompt,
                use_lora=use_lora,
                lora_filename=lora_filename,
                reference_image=reference_image,
                ip_adapter_scale=ip_adapter_scale_auto,
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
                    
                    # Save image generation result as assistant message
                    image_metadata = {
                        'model': model_desc,
                        'lora_used': lora_filename if use_lora else None,
                        'steps': num_steps,
                        'dimensions': f'{width}×{height}',
                        'ip_adapter': use_ip_adapter or use_ip_adapter_auto,
                        'ip_adapter_scale': ip_adapter_scale if use_ip_adapter else (ip_adapter_scale_auto if reference_image else None),
                        'web_reference_used': reference_image is not None,
                        'prompt': image_prompt
                    }
                    
                    # Increment count
                    user.prompt_count = (user.prompt_count or 0) + 1
                    models.db.session.commit()
                    
                    print(f"✅ User {user.email} prompt count: {user.prompt_count}/5")
            except Exception as e:
                print(f"❌ Database error: {e}")
                models.db.session.rollback()
            
            # Clear the reference image after successful generation to save memory
            if uid in user_reference_images:
                del user_reference_images[uid]
                print(f"🗑️ Cleared reference image for user {uid} to save storage")
            
            # Build model description
            model_parts = []
            if use_lora:
                lora_name = lora_filename or "Custom LoRA"
                model_parts.append(f"LoRA: {lora_name}")
            else:
                model_parts.append("Base Flux Schnell")
            if use_ip_adapter:
                model_parts.append(f"IP-Adapter ({ip_adapter_scale:.1%})")
            elif reference_image:
                model_parts.append(f"IP-Adapter + Web Reference ({ip_adapter_scale_auto:.1%})")
            model_desc = " + ".join(model_parts)
            
            # Return success with image
            return jsonify({
                'success': True,
                'image': f"data:image/{config.IMAGE_FORMAT.lower()};base64,{img_str}",
                'filename': filename,
                'path': image_path,
                'extra_data': {
                    'model': model_desc,
                    'lora_used': lora_filename if use_lora else None,
                    'steps': num_steps,
                    'dimensions': f'{width}×{height}',
                    'ip_adapter': use_ip_adapter or use_ip_adapter_auto,
                    'ip_adapter_scale': ip_adapter_scale if use_ip_adapter else (ip_adapter_scale_auto if reference_image else None),
                    'web_reference_used': reference_image is not None,
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
            'extra_data': {
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
    """Get user's complete chat history from database"""
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
                .limit(200)\
                .all()
            
            history = []
            for entry in history_entries:
                history.append({
                    'id': entry.id,
                    'role': entry.role,
                    'message': entry.message,
                    'message_type': entry.message_type,
                    'image_path': entry.image_path,
                    'extra_data': entry.metadata,
                    'timestamp': entry.created_at.isoformat() if entry.created_at else None,
                    # For backward compatibility
                    'prompt': entry.message if entry.role == 'user' else None,
                    'preview': (entry.message[:80] + '...' if len(entry.message) > 80 else entry.message) if entry.message else None
                })
            
            return jsonify({
                'success': True,
                'history': history,
                'total': len(history)
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

@app.route('/api/unsubscribe', methods=['POST'])
@verify_firebase_token
def unsubscribe():
    """
    Unsubscribe user from Pro plan and revert to free tier
    """
    try:
        firebase_user = getattr(request, 'firebase_user', None)
        if not firebase_user:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        uid = firebase_user.get('uid')
        
        with app.app_context():
            user = models.User.query.filter_by(firebase_uid=uid).first()
            if not user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
            
            if not user.is_pro:
                return jsonify({'success': False, 'error': 'User is not subscribed to Pro'}), 400
            
            # Downgrade user to free tier
            user.is_pro = False
            models.db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Successfully unsubscribed from Pro. You are now on the free tier.'
            })
    
    except Exception as e:
        models.db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Admin routes
@app.route('/admin')
def admin_page():
    """Render admin dashboard"""
    return render_template('admin.html')


@app.route('/api/admin/users', methods=['GET'])
@verify_firebase_token
def admin_get_users():
    """
    Get all users with their statistics (admin only)
    TODO: Add proper admin role checking
    """
    try:
        firebase_user = getattr(request, 'firebase_user', None)
        if not firebase_user:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        # TODO: Check if user has admin role
        # For now, any authenticated user can access (update this in production!)
        
        with app.app_context():
            users = models.User.query.all()
            
            users_data = []
            total_generations = 0
            today_generations = 0
            pro_count = 0
            
            today = datetime.utcnow().date()
            
            for user in users:
                history_count = models.ChatHistory.query.filter_by(user_id=user.id).count()
                total_generations += history_count
                
                # Count today's generations
                today_count = models.ChatHistory.query.filter_by(user_id=user.id).filter(
                    models.ChatHistory.created_at >= datetime.combine(today, datetime.min.time())
                ).count()
                today_generations += today_count
                
                if user.is_pro:
                    pro_count += 1
                
                users_data.append({
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'is_pro': user.is_pro,
                    'history_count': history_count,
                    'prompt_count': user.prompt_count or 0,
                    'created_at': user.created_at.isoformat() if user.created_at else None
                })
            
            stats = {
                'total_users': len(users),
                'pro_users': pro_count,
                'total_generations': total_generations,
                'today_generations': today_generations
            }
            
            return jsonify({
                'success': True,
                'users': users_data,
                'stats': stats
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/admin/users/<int:user_id>/history', methods=['GET'])
@verify_firebase_token
def admin_get_user_history(user_id):
    """
    Get chat history for a specific user (admin only)
    TODO: Add proper admin role checking
    """
    try:
        firebase_user = getattr(request, 'firebase_user', None)
        if not firebase_user:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        # TODO: Check if user has admin role
        
        with app.app_context():
            user = models.User.query.get(user_id)
            if not user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
            
            history = models.ChatHistory.query.filter_by(user_id=user_id)\
                .order_by(models.ChatHistory.created_at.desc())\
                .all()
            
            history_data = []
            for entry in history:
                history_data.append({
                    'id': entry.id,
                    'prompt': entry.prompt,
                    'image_path': entry.image_path,
                    'created_at': entry.created_at.isoformat() if entry.created_at else None
                })
            
            return jsonify({
                'success': True,
                'history': history_data
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


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
