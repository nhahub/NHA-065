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
    conversation_id = data.get('conversation_id')  # ✅ Get conversation_id from request
    
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
        # Classify user intent first for better handling
        intent_data = mistral_chat.classify_user_intent(user_message, data.get('conversation_history', []))
        print(f"💭 Intent: {intent_data['intent']} (confidence: {intent_data['confidence']:.2f})")
        
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
                    
                    # Download and store the image as reference for FLUX Redux
                    image_url = selected_photo.get('image_url')
                    hostname = selected_photo.get('hostname', 'web')
                    thumbnail_url = selected_photo.get('thumbnail_url')
                    
                    # Try to download with retry logic
                    download_success = False
                    reference_img = None
                    error_details = None
                    
                    # Strategy 1: Try main image URL with retries
                    for attempt in range(3):
                        try:
                            print(f"📥 Attempt {attempt + 1}/3: Downloading from {hostname}")
                            
                            headers = {
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                                'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                                'Accept-Encoding': 'gzip, deflate, br',
                                'Accept-Language': 'en-US,en;q=0.9',
                                'Referer': 'https://www.google.com/',
                                'DNT': '1'
                            }
                            
                            response = requests.get(
                                image_url, 
                                timeout=20, 
                                headers=headers, 
                                stream=True,
                                allow_redirects=True,
                                verify=True
                            )
                            response.raise_for_status()
                            
                            # Open and validate image
                            reference_img = Image.open(io.BytesIO(response.content))
                            reference_img = reference_img.convert('RGB')
                            
                            # Validate image size
                            if reference_img.size[0] < 50 or reference_img.size[1] < 50:
                                raise ValueError(f"Image too small: {reference_img.size}")
                            
                            print(f"✅ Downloaded successfully: {reference_img.size}")
                            download_success = True
                            break
                            
                        except requests.exceptions.SSLError as e:
                            error_details = f"SSL error: {str(e)}"
                            print(f"⚠️ SSL error on attempt {attempt + 1}")
                            if attempt == 2:  # Last attempt
                                # Try without SSL verification as last resort
                                try:
                                    response = requests.get(image_url, timeout=20, headers=headers, stream=True, verify=False)
                                    response.raise_for_status()
                                    reference_img = Image.open(io.BytesIO(response.content)).convert('RGB')
                                    if reference_img.size[0] >= 50 and reference_img.size[1] >= 50:
                                        download_success = True
                                        break
                                except:
                                    pass
                        except requests.exceptions.Timeout:
                            error_details = "Download timed out"
                            print(f"⏱️ Timeout on attempt {attempt + 1}")
                        except requests.exceptions.HTTPError as e:
                            error_details = f"HTTP {e.response.status_code}"
                            print(f"❌ HTTP error {e.response.status_code}")
                            break  # Don't retry on 404, 403, etc.
                        except Exception as e:
                            error_details = str(e)
                            print(f"⚠️ Error on attempt {attempt + 1}: {e}")
                    
                    # Strategy 2: Try thumbnail URL as fallback
                    if not download_success and thumbnail_url:
                        try:
                            print(f"📥 Trying thumbnail URL as fallback...")
                            response = requests.get(thumbnail_url, timeout=15, headers=headers, stream=True)
                            response.raise_for_status()
                            reference_img = Image.open(io.BytesIO(response.content)).convert('RGB')
                            if reference_img.size[0] >= 50 and reference_img.size[1] >= 50:
                                print(f"✅ Thumbnail downloaded successfully")
                                download_success = True
                        except Exception as e:
                            print(f"⚠️ Thumbnail download failed: {e}")
                    
                    # Return result
                    if download_success and reference_img:
                        # Store in memory
                        user_reference_images[uid] = reference_img
                        
                        return jsonify({
                            'success': True,
                            'response': f"Perfect! I've saved this logo from **{hostname}** as your reference image. 🎨\n\nNow, please describe the logo you want me to create!",
                            'is_image_request': False,
                            'photo_confirmed': True
                        })
                    else:
                        # Download failed - provide helpful message with better guidance
                        error_msg = f"I had trouble downloading the image from **{hostname}**."
                        
                        # Provide specific error guidance
                        if error_details:
                            if "403" in error_details or "401" in error_details:
                                error_msg += " The website is blocking automated downloads."
                            elif "404" in error_details:
                                error_msg += " The image link is no longer valid."
                            elif "timeout" in error_details.lower():
                                error_msg += " The download timed out."
                            elif "SSL" in error_details:
                                error_msg += " There's a security certificate issue."
                        
                        # Check how many results are available
                        num_results = len(results)
                        other_options = []
                        if num_results > 1:
                            other_options.append(f"**Try another image** - Type 'use image 2' or 'use image 3'")
                        other_options.append("**Search again** - Try searching for a different brand")
                        other_options.append("**Skip the reference** - Just describe what you want, and I'll create it!")
                        
                        return jsonify({
                            'success': True,
                            'response': f"{error_msg}\n\n{'📋 Options:' if len(other_options) > 1 else ''}\n\n" + "\n".join(f"{i+1}️⃣ {opt}" for i, opt in enumerate(other_options)) + "\n\n*Tip: Some websites protect their images, but I can create amazing logos from your description!* 🎨",
                            'is_image_request': False,
                            'download_failed': True
                        })
            
            # Refinement/rejection keywords
            elif any(keyword in user_msg_lower for keyword in ['no', 'different', 'search again', '❌', 'wrong']):
                original_query = mistral_chat.pending_photo_requests[uid].get('query', '')
                mistral_chat.pending_photo_requests.pop(uid)
                
                # Check if user provided a new search query in their message
                new_query = mistral_chat.extract_photo_search_query(user_message, data.get('conversation_history', []))
                
                if new_query and new_query.lower() != original_query.lower():
                    # User provided new search terms, search with those
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
                else:
                    # User didn't provide new search terms, ask for clarification
                    return jsonify({
                        'success': True,
                        'response': f"No problem! What would you like me to search for instead? 🔍\n\n*Tip: Be specific with brand names or logo styles you want to reference.*",
                        'is_image_request': False
                    })
        
        # Check if this is a NEW photo search request
        elif mistral_chat.is_photo_search_request(user_message):
            search_query = mistral_chat.extract_photo_search_query(user_message, data.get('conversation_history', []))
            print(f"🔍 Extracted search query: {search_query}")
            print(f"📝 Conversation history length: {len(data.get('conversation_history', []))}")
            
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

    # Handle special case where chat returns None (user wants to search after rejecting logo)
    if response_text is None and use_web_search:
        search_query = mistral_chat.extract_photo_search_query(user_message, data.get('conversation_history', []))
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
            except Exception as e:
                response_text = "I had trouble with that search. Could you rephrase what you're looking for? 🔍"

    # Check if this is a web search result from Mistral
    if logo_data and isinstance(logo_data, dict) and logo_data.get('_web_search_result'):
        photo_result = logo_data.get('photo_result')
        return jsonify({
            'success': True,
            'response': response_text,
            'is_image_request': False,
            'awaiting_photo_confirmation': True,
            'photo_result': photo_result
        })

    if is_image and image_prompt:
        if not user.is_pro and user.prompt_count >= 5:
            limit_msg = "Free limit reached (5/day). Upgrade to Pro!"
            entry = ChatHistory(
                user_id=user.id, 
                user_message=user_message, 
                ai_response=limit_msg, 
                message_type='text',
                conversation_id=conversation_id  # ✅ Add conversation_id
            )
            db.session.add(entry)
            db.session.commit()
            return jsonify({'success': True, 'response': limit_msg + " [Upgrade](/upgrade)", 'needs_upgrade': True})

        friendly = mistral_chat.generate_acknowledgment(user_message)
        entry = ChatHistory(
            user_id=user.id, 
            user_message=user_message, 
            ai_response=response_text, 
            message_type='text',
            conversation_id=conversation_id  # ✅ Add conversation_id
        )
        db.session.add(entry)
        db.session.commit()
        return jsonify({
            'success': True, 'response': friendly, 'is_image_request': True,
            'image_prompt': image_prompt, 'needs_generation': True,
            'chat_entry_id': entry.id, 'remaining_prompts': None if user.is_pro else (5 - user.prompt_count)
        })

    # ✅ Add conversation_id to regular chat entries
    entry = ChatHistory(
        user_id=user.id, 
        user_message=user_message, 
        ai_response=response_text, 
        message_type='text',
        conversation_id=conversation_id  # ✅ Add conversation_id
    )
    db.session.add(entry)
    db.session.commit()

    return jsonify({'success': True, 'response': response_text, 'is_image_request': False})