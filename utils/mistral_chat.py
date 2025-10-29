"""
Mistral AI Chat Manager for Zypher AI Logo Generator
Handles conversations with Mistral AI and detects image generation requests
"""
import json
import re
import requests
from typing import Dict, Tuple, Optional, List
import config


class MistralChatManager:
    """Manages conversations with Mistral AI and detects image generation intents"""
    
    def __init__(self):
        self.api_key = config.MISTRAL_API_KEY
        self.model = config.MISTRAL_MODEL
        self.endpoint = config.MISTRAL_API_ENDPOINT
        self.system_prompt = config.MISTRAL_SYSTEM_PROMPT
        
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
    
    def chat(self, user_message: str, conversation_history: Optional[List[Dict]] = None) -> Tuple[str, bool, Optional[str]]:
        """
        Send a message to Mistral AI and get response
        
        Args:
            user_message (str): User's message
            conversation_history (Optional[List[Dict]]): Previous messages in format [{"role": "user/assistant", "content": "..."}]
            
        Returns:
            Tuple[str, bool, Optional[str]]: (response_text, is_image_request, image_prompt)
        """
        if not self.api_key or self.api_key == 'your_mistral_api_key_here':
            return ("⚠️ Mistral API key not configured. Please add MISTRAL_API_KEY to your .env file. Get your key from: https://console.mistral.ai/api-keys/", False, None)
        
        try:
            # Build messages array
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
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
            
            # Check if response contains image generation request
            image_prompt = self.extract_image_prompt(assistant_message)
            
            if image_prompt:
                return (assistant_message, True, image_prompt)
            else:
                return (assistant_message, False, None)
                
        except requests.exceptions.Timeout:
            return ("⚠️ Request timed out. Please try again.", False, None)
        except requests.exceptions.RequestException as e:
            error_msg = f"⚠️ Error communicating with Mistral AI: {str(e)}"
            return (error_msg, False, None)
        except Exception as e:
            return (f"⚠️ Unexpected error: {str(e)}", False, None)
    
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
