"""
Mistral AI Chat Manager for Zypher AI Logo Generator
Handles conversations with Mistral AI and detects image generation requests
Integrates with Logo Reference Agent for enhanced logo design workflow
"""
import json
import re
import requests
from typing import Dict, Tuple, Optional, List
import config
from utils.logo_agent import LogoReferenceAgent


class MistralChatManager:
    """Manages conversations with Mistral AI and detects image generation intents"""
    
    def __init__(self):
        self.api_key = config.MISTRAL_API_KEY
        self.model = config.MISTRAL_MODEL
        self.endpoint = config.MISTRAL_API_ENDPOINT
        self.system_prompt = config.MISTRAL_SYSTEM_PROMPT
        self.logo_agent = LogoReferenceAgent()
        
        # Track pending logo requests awaiting confirmation
        self.pending_logo_requests = {}  # user_id -> logo_request_data
        
        # Track pending photo search requests awaiting confirmation
        self.pending_photo_requests = {}  # user_id -> photo_request_data
        
        if not self.api_key or self.api_key == 'your_mistral_api_key_here':
            print("⚠️  WARNING: MISTRAL_API_KEY not set in .env file")
            print("   Get your API key from: https://console.mistral.ai/api-keys/")
    
    def is_image_generation_request(self, text: str) -> bool:
        """
        Detect if the user message is requesting image/logo generation
        
        Args:
            text (str): User message
            
        Returns:
            bool: True if requesting image generation
        """
        # Keywords that indicate image generation intent
        generation_keywords = [
            r'\b(create|generate|make|design|build|draw|produce)\b',
            r'\b(logo|image|picture|photo|graphic|illustration|icon|banner)\b'
        ]
        
        text_lower = text.lower()
        
        # Check if message contains both action and target keywords
        has_action = bool(re.search(generation_keywords[0], text_lower))
        has_target = bool(re.search(generation_keywords[1], text_lower))
        
        return has_action and has_target
    
    def is_photo_search_request(self, text: str) -> bool:
        """
        Detect if the user message is requesting to search for a specific photo/logo
        
        Args:
            text (str): User message
            
        Returns:
            bool: True if requesting photo search
        """
        text_lower = text.lower()
        
        # Enhanced patterns that catch more natural language variations
        specific_patterns = [
            # Direct search commands
            r'\b(search|find|get|fetch|show|display|look up|lookup)\s+(?:for\s+)?(?:a\s+)?(?:an\s+)?(?:the\s+)?(?:photo|image|logo|picture|pic)\s+(?:of\s+|for\s+)',
            # "show me X logo" patterns
            r'\b(show|find|get|fetch)\s+(?:me\s+)?(?:the\s+)?\w+\s+(?:logo|image|photo)',
            # "X logo" at start or after search words
            r'\b(search|find|get|lookup|look up)\s+\w+\s+logo',
            # Photo/image/logo + of/for pattern
            r'\b(?:photo|image|logo|picture)\s+(?:of|for)\s+\w+',
            # Brand name + logo (e.g., "Nike logo")
            r'\b[A-Z]\w+\s+logo\b',
            # "the X logo"
            r'\bthe\s+\w+\s+logo\b',
        ]
        
        for pattern in specific_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        
        return False
    
    def extract_photo_search_query(self, text: str, conversation_history: Optional[List[Dict]] = None) -> Optional[str]:
        """
        Extract the subject/query for photo search from user message
        Uses conversation history for context when needed
        
        Args:
            text (str): User message
            conversation_history (Optional[List[Dict]]): Recent conversation for context
            
        Returns:
            Optional[str]: Extracted search query or None
        """
        # Patterns to extract the subject - more flexible to handle various phrasings
        patterns = [
            # "search for the BMW logo" -> captures "BMW logo"
            r'(?:search|find|get|fetch|show|display|look\s+up|lookup)\s+(?:for\s+)?(?:a\s+)?(?:an\s+)?(?:the\s+)?([\w\s]+\s+logo)',
            # "show me Nike logo" -> captures "Nike logo"
            r'(?:show|find|get)\s+(?:me\s+)?(?:the\s+)?([\w\s]+\s+logo)',
            # "search for a photo of BMW" -> captures "BMW"
            r'(?:search|find|get|fetch|show|display).*?(?:photo|image|logo|picture).*?(?:of|for)\s+([^.!?,]+)',
            # "photo of BMW" -> captures "BMW"
            r'(?:photo|image|logo|picture)\s+(?:of|for)\s+([^.!?,]+)',
            # "the Nike logo" -> captures "Nike logo"
            r'the\s+([\w\s]+\s+logo)',
            # "Brand name + logo" pattern (e.g., "Nike logo")
            r'\b([A-Z][\w\s]*\s+logo)\b',
            # Fallback: capture brand name before "logo"
            r'([\w\s]+)\s+logo',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                query = match.group(1).strip()
                # Clean up common trailing words and punctuation
                query = re.sub(r'\s+(please|thanks|thank you|now|today)$', '', query, flags=re.IGNORECASE)
                query = re.sub(r'[.!?,;]+$', '', query)  # Remove trailing punctuation
                
                # If query doesn't contain "logo", add it
                if query and 'logo' not in query.lower():
                    query = f"{query} logo"
                
                if query and len(query) > 2:  # Ensure we got something meaningful
                    return query
        
        # If no specific brand found and user said something generic like "search for it" or "show me"
        # Try to extract context from conversation history
        if conversation_history and len(conversation_history) > 0:
            text_lower = text.lower().strip()
            generic_phrases = ['search for it', 'show me', 'find it', 'look it up', 'get it', 'that one', 'search it']
            
            if any(phrase in text_lower for phrase in generic_phrases):
                # Look for brand names or topics in recent conversation
                for msg in reversed(conversation_history[-3:]):  # Check last 3 messages
                    content = msg.get('content', '')
                    # Try to find brand names (capitalized words followed by context words)
                    context_match = re.search(r'\b([A-Z][\w]+(?:\s+[A-Z][\w]+)?)\b.*(?:logo|brand|company|design)', content, re.IGNORECASE)
                    if context_match:
                        brand_name = context_match.group(1).strip()
                        return f"{brand_name} logo"
        
        return None
    
    def extract_image_prompt(self, response_text: str) -> Optional[str]:
        """
        Extract image generation prompt from Mistral response if it contains JSON action
        
        Args:
            response_text (str): Mistral response
            
        Returns:
            Optional[str]: Extracted prompt or None
        """
        try:
            # Try to parse as JSON
            data = json.loads(response_text)
            if isinstance(data, dict) and data.get('action') == 'generate_image':
                return data.get('prompt')
        except json.JSONDecodeError:
            # Try to extract JSON from text
            json_match = re.search(r'\{[^}]*"action"\s*:\s*"generate_image"[^}]*\}', response_text)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                    return data.get('prompt')
                except:
                    pass
        
        return None
    
    def extract_web_search_query(self, response_text: str) -> Optional[str]:
        """
        Extract web search query from Mistral response if it contains JSON search action
        
        Args:
            response_text (str): Mistral response
            
        Returns:
            Optional[str]: Extracted search query or None
        """
        try:
            # Try to parse as JSON
            data = json.loads(response_text)
            if isinstance(data, dict) and data.get('action') == 'search_web':
                return data.get('query')
        except json.JSONDecodeError:
            # Try to extract JSON from text
            json_match = re.search(r'\{[^}]*"action"\s*:\s*"search_web"[^}]*\}', response_text)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                    return data.get('query')
                except:
                    pass
        
        return None
    
    def chat(self, user_message: str, conversation_history: Optional[List[Dict]] = None, user_id: Optional[str] = None, use_web_search: bool = False) -> Tuple[str, bool, Optional[str], Optional[Dict]]:
        """
        Send a message to Mistral AI and get response
        
        Args:
            user_message (str): User's message
            conversation_history (Optional[List[Dict]]): Previous messages in format [{"role": "user/assistant", "content": "..."}]
            user_id (Optional[str]): User ID for tracking pending requests
            use_web_search (bool): Whether web search is enabled for photos/logos
            
        Returns:
            Tuple[str, bool, Optional[str], Optional[Dict]]: (response_text, is_image_request, image_prompt, logo_preview_data_or_photo_result)
        """
        if not self.api_key or self.api_key == 'your_mistral_api_key_here':
            return ("⚠️ Mistral API key not configured. Please add MISTRAL_API_KEY to your .env file. Get your key from: https://console.mistral.ai/api-keys/", False, None, None)
        
        # Check if user is confirming a pending logo request
        if user_id and user_id in self.pending_logo_requests:
            user_msg_lower = user_message.lower().strip()
            
            # Confirmation keywords
            if any(keyword in user_msg_lower for keyword in ['yes', 'confirm', 'looks good', 'perfect', 'generate', 'go ahead', '✅', 'proceed']):
                logo_data = self.pending_logo_requests.pop(user_id)
                return (
                    "Great! Generating your logo now... ✨",
                    True,
                    logo_data['final_diffusion_prompt'],
                    None
                )
            
            # Refinement/rejection keywords
            elif any(keyword in user_msg_lower for keyword in ['no', 'refine', 'different', 'change', 'search again', '❌', 'revise']):
                # Clear the pending request
                self.pending_logo_requests.pop(user_id)
                
                # Check if user provided specific changes or new request
                if len(user_message.split()) > 2:  # More than just "no" or "search again"
                    # User provided specific refinement, re-process with new request
                    try:
                        logo_result = self.logo_agent.process_logo_request(user_message)
                        if logo_result.get('success'):
                            preview_text = self.logo_agent.format_preview_for_user(logo_result)
                            
                            # Store pending request
                            if user_id:
                                self.pending_logo_requests[user_id] = logo_result
                            
                            return (preview_text, False, None, logo_result)
                    except Exception as e:
                        print(f"Error re-processing logo request: {e}")
                else:
                    # User just said no without specifics, ask for clarification
                    return (
                        "No problem! Would you like to:\n\n1️⃣ Search for a different reference logo\n2️⃣ Describe a different logo style or concept\n3️⃣ Proceed without references\n\nWhat changes would you like to make? 🎨",
                        False,
                        None,
                        None
                    )
        
        try:
            # Build messages array
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Add web search status context to system message if needed
            if use_web_search:
                messages.append({
                    "role": "system", 
                    "content": "Note: Web search is currently ENABLED. You can use the search_web action to find existing logos/images."
                })
            else:
                messages.append({
                    "role": "system",
                    "content": "Note: Web search is currently DISABLED. If user requests to search for existing logos, inform them to enable web search."
                })
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history[-10:])  # Keep last 10 messages for context
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Call Mistral API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 401:
                return ("⚠️ Invalid Mistral API key. Please check your MISTRAL_API_KEY in .env file.", False, None)
            
            response.raise_for_status()
            
            result = response.json()
            assistant_message = result['choices'][0]['message']['content']
            
            # Check if Mistral returned a web search action (when web search is enabled)
            if use_web_search:
                web_search_query = self.extract_web_search_query(assistant_message)
                if web_search_query:
                    # Mistral wants to search the web
                    # Fallback: if query is too short/generic, try extracting from user message
                    if len(web_search_query.split()) < 2:
                        fallback_query = self.extract_photo_search_query(user_message, conversation_history)
                        if fallback_query:
                            web_search_query = fallback_query
                    
                    try:
                        photo_result = self.logo_agent.search_for_photo(web_search_query)
                        
                        if photo_result.get('success'):
                            preview_text = self.logo_agent.format_photo_preview(photo_result)
                            # Store pending request for confirmation
                            if user_id:
                                self.pending_photo_requests[user_id] = photo_result
                            
                            # Return special tuple indicating this is a photo search result
                            # Format: (response, is_image_request, image_prompt, photo_data)
                            # We use a special marker in response to indicate this is a web search
                            return (preview_text, False, None, {'_web_search_result': True, 'photo_result': photo_result})
                    except Exception as e:
                        print(f"Error performing web search: {e}")
                        # Continue with normal response
            
            # Check if this is a logo generation request
            # Only use Logo Reference Agent when web search is ENABLED
            if self.is_image_generation_request(user_message) and use_web_search:
                try:
                    # Use Logo Reference Agent to gather references and create optimized prompt
                    logo_result = self.logo_agent.process_logo_request(user_message)
                    
                    if logo_result.get('success'):
                        # Format preview for user
                        preview_text = self.logo_agent.format_preview_for_user(logo_result)
                        
                        # Store pending request for confirmation
                        if user_id:
                            self.pending_logo_requests[user_id] = logo_result
                        
                        # Return preview without generating yet
                        return (preview_text, False, None, logo_result)
                    
                except Exception as e:
                    print(f"Error in logo agent processing: {e}")
                    # Fall back to original behavior
                    pass
            
            # Check if response contains image generation request (fallback)
            image_prompt = self.extract_image_prompt(assistant_message)
            
            if image_prompt:
                return (assistant_message, True, image_prompt, None)
            else:
                return (assistant_message, False, None, None)
                
        except requests.exceptions.Timeout:
            return ("⚠️ Request timed out. Please try again.", False, None, None)
        except requests.exceptions.RequestException as e:
            error_msg = f"⚠️ Error communicating with Mistral AI: {str(e)}"
            return (error_msg, False, None, None)
        except Exception as e:
            return (f"⚠️ Unexpected error: {str(e)}", False, None, None)
    
    def enhance_image_prompt(self, basic_prompt: str) -> str:
        """
        Use Mistral to enhance a basic image prompt with more details
        
        Args:
            basic_prompt (str): Basic image description
            
        Returns:
            str: Enhanced prompt with more details
        """
        if not self.api_key or self.api_key == 'your_mistral_api_key_here':
            return basic_prompt
        
        try:
            enhancement_request = f"""Enhance this image generation prompt with more specific details about style, colors, composition, and mood. Return ONLY the enhanced prompt, no explanations:

Original prompt: {basic_prompt}

Enhanced prompt:"""
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": enhancement_request}
                ],
                "temperature": 0.7,
                "max_tokens": 200
            }
            
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                enhanced = result['choices'][0]['message']['content'].strip()
                # Remove quotes if present
                enhanced = enhanced.strip('"').strip("'")
                return enhanced if enhanced else basic_prompt
            else:
                return basic_prompt
                
        except Exception as e:
            print(f"Error enhancing prompt: {e}")
            return basic_prompt
    
    def generate_acknowledgment(self, user_message: str) -> str:
        """
        Generate a friendly, personalized acknowledgment message for image generation requests
        
        Args:
            user_message (str): The user's original request
            
        Returns:
            str: A friendly acknowledgment message
        """
        if not self.api_key or self.api_key == 'your_mistral_api_key_here':
            return "Sure! I'll be generating that for you. This will just take a moment! ✨"
        
        try:
            acknowledgment_request = f"""Based on this user request, generate a short, friendly acknowledgment message (1-2 sentences max) that:
1. Says you'll generate what they asked for
2. Mentions specifically what they requested (e.g., "your logo for a juice company")
3. Adds excitement with an emoji
4. Keeps it brief and natural

User request: "{user_message}"

Reply with ONLY the acknowledgment message, nothing else:"""
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": acknowledgment_request}
                ],
                "temperature": 0.7,
                "max_tokens": 100
            }
            
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                acknowledgment = result['choices'][0]['message']['content'].strip()
                # Remove quotes if present
                acknowledgment = acknowledgment.strip('"').strip("'")
                return acknowledgment if acknowledgment else "Sure! I'll be generating that for you. This will just take a moment! ✨"
            else:
                return "Sure! I'll be generating that for you. This will just take a moment! ✨"
                
        except Exception as e:
            print(f"Error generating acknowledgment: {e}")
            return "Sure! I'll be generating that for you. This will just take a moment! ✨"
