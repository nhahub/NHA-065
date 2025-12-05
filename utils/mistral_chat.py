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
    
    def is_image_generation_request(self, text: str, conversation_history: Optional[List[Dict]] = None) -> bool:
        """
        Detect if the user message is requesting image/logo generation with context awareness
        
        Args:
            text (str): User message
            conversation_history (Optional[List[Dict]]): Recent conversation for context
            
        Returns:
            bool: True if requesting image generation
        """
        text_lower = text.lower()
        
        # Strong generation indicators - these clearly mean "create new"
        strong_generation_patterns = [
            r'\b(create|generate|make|design|build|produce|craft)\s+(?:a|an|my|our)?\s*(?:logo|image|design|graphic)\b',
            r'\b(design|create)\s+(?:me|us)?\s*(?:a|an)?\s*(?:new)?\s*logo\b',
            r'\blogo\s+for\s+(?:my|our|a|an)\s+\w+',  # "logo for my business"
            r'\b(?:I|we)\s+(?:want|need)\s+(?:a|an)?\s*(?:new)?\s*logo\b',
            r'\bcan\s+you\s+(create|make|design|generate)\b',
        ]
        
        for pattern in strong_generation_patterns:
            if re.search(pattern, text_lower):
                return True
        
        # Check for generation keywords with context
        generation_action_words = ['create', 'generate', 'make', 'design', 'build', 'draw', 'produce', 'craft']
        target_words = ['logo', 'image', 'graphic', 'illustration', 'icon', 'banner', 'design']
        
        has_action = any(word in text_lower for word in generation_action_words)
        has_target = any(word in text_lower for word in target_words)
        
        # If both present, it's likely a generation request
        if has_action and has_target:
            # But check for negation patterns (e.g., "don't create", "not making")
            negation_patterns = [r'\b(don\'t|do not|not|never)\s+\w+\s+(create|make|design|generate)\b']
            for pattern in negation_patterns:
                if re.search(pattern, text_lower):
                    return False
            return True
        
        # Check context from conversation history for implicit requests
        if conversation_history and len(conversation_history) > 0:
            # Look at last few messages for context
            recent_messages = conversation_history[-3:] if len(conversation_history) >= 3 else conversation_history
            
            # If user previously mentioned wanting to create something
            context_str = " ".join([msg.get('content', '') for msg in recent_messages]).lower()
            
            # Implicit continuation patterns (e.g., "yes do it", "go ahead", "that sounds good")
            implicit_patterns = [
                r'\b(yes|yeah|yep|sure|okay|ok|please|go ahead|sounds good|let\'s do it)\b',
                r'\b(that\'s perfect|looks good|i like|proceed)\b'
            ]
            
            # Check if recent context was about logo creation
            if any(word in context_str for word in ['create', 'design', 'logo', 'generate']):
                for pattern in implicit_patterns:
                    if re.search(pattern, text_lower) and len(text.split()) <= 5:
                        return True
        
        return False
    
    def is_photo_search_request(self, text: str, conversation_history: Optional[List[Dict]] = None) -> bool:
        """
        Detect if the user message is requesting to search for a specific photo/logo with context awareness
        
        Args:
            text (str): User message
            conversation_history (Optional[List[Dict]]): Recent conversation for context
            
        Returns:
            bool: True if requesting photo search
        """
        text_lower = text.lower()
        print(f"🔍 Checking if photo search: '{text[:50]}...'")
        
        # Strong search indicators - these clearly mean "find existing"
        strong_search_patterns = [
            # Direct search commands
            r'\b(search|find|get|fetch|show|display|look\s*up|lookup)\s+(?:for\s+)?(?:a\s+)?(?:an\s+)?(?:the\s+)?(?:photo|image|logo|picture|pic)\s+(?:of|for)\s+',
            # "show me [brand] logo"
            r'\b(show|find|get|fetch)\s+(?:me\s+)?(?:the\s+)?[A-Z]\w+\s+(?:logo|image)',
            # Direct "X logo" requests (capitalized brand name)
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+logo\b',
            # "what does X logo look like"
            r'\bwhat\s+(?:does|is)\s+\w+(?:\s+\w+)*?\s+logo\s+look\s+like\b',
            # Searching with "for" - "search for nike logo"
            r'\b(search|find|lookup)\s+(?:for\s+)?\w+\s+logo\b',
        ]
        
        for pattern in strong_search_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                # Additional check: make sure it's not about creating
                if not re.search(r'\b(create|generate|make|design|similar|like)\b', text_lower):
                    return True
        
        # Contextual search patterns - need conversation history
        if conversation_history:
            recent_context = " ".join([msg.get('content', '') for msg in conversation_history[-3:]]).lower()
            
            # Follow-up search requests (e.g., "show me that", "search for it", "find it")
            implicit_search = [
                r'\b(show|search|find)\s+(me\s+)?(that|it|them)\b',
                r'\b(what about|how about)\s+\w+\s*\'?s?\s+logo\b',
                r'\blet\s+me\s+see\s+(that|it|the\s+\w+\s+logo)\b',
            ]
            
            for pattern in implicit_search:
                if re.search(pattern, text_lower):
                    # Check if recent context was about searching/viewing logos
                    if any(word in recent_context for word in ['search', 'find', 'show', 'logo', 'brand', 'reference']):
                        return True
            
            # Check if this is a refinement after rejection (e.g., "i want the red logo", "the performance one")
            # These indicate user is continuing a search conversation
            if any(rejection_word in recent_context for rejection_word in ['no problem', 'what would you like', 'search for instead', 'different', 'search again']):
                # User is answering "what would you like to search for?"
                refinement_indicators = [
                    r'\bi\s+want\s+(?:the\s+)?[\w\s]+\s+logo\b',  # "i want the red logo"
                    r'\bthe\s+[\w\s]+\s+logo\b',  # "the performance logo"
                    r'\bfor\s+(?:the\s+)?[\w\s]+',  # "for the performance"
                    r'\b[\w\s]+\s+(?:version|variant|one|model)\b',  # "performance version"
                ]
                
                for pattern in refinement_indicators:
                    if re.search(pattern, text_lower):
                        return True
        
        # Check for "the X logo" pattern (lowercase - referring to existing brand)
        # But exclude if followed by generation words
        the_logo_match = re.search(r'\bthe\s+(\w+)\s+logo\b', text_lower)
        if the_logo_match:
            brand = the_logo_match.group(1)
            # Check if brand looks like a real company (not generic words)
            generic_words = ['new', 'old', 'first', 'last', 'main', 'best', 'perfect', 'right']
            if brand not in generic_words:
                # Make sure no generation words follow
                following_text = text_lower[the_logo_match.end():]
                if not re.search(r'\b(create|generate|make|design)\b', following_text):
                    return True
        
        return False
    
    def extract_photo_search_query_with_ai(self, text: str, conversation_history: Optional[List[Dict]] = None) -> Optional[str]:
        """
        Use Mistral AI to analyze context and extract the search query intelligently.
        This provides much better context understanding than regex patterns.
        
        Args:
            text (str): User message
            conversation_history (Optional[List[Dict]]): Recent conversation for context
            
        Returns:
            Optional[str]: Extracted search query or None
        """
        print(f"🤖 Using Mistral AI to extract search query from: '{text}'")
        
        try:
            # Build context from conversation history
            context_messages = []
            if conversation_history:
                # Include last 5 messages for context
                for msg in conversation_history[-5:]:
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    if content:
                        context_messages.append(f"{role.upper()}: {content}")
            
            context_str = "\n".join(context_messages) if context_messages else "No previous context"
            
            # Create AI prompt for query extraction
            extraction_prompt = f"""You are helping extract a search query for a logo/brand image search.

CONVERSATION HISTORY:
{context_str}

CURRENT USER MESSAGE:
{text}

TASK:
Analyze the current message and conversation history to determine what logo/brand the user wants to search for.

RULES:
1. If the user mentions a specific brand name (e.g., "BMW", "Nike"), extract it
2. If the user is refining a previous search (e.g., "the red one", "performance version"), combine the refinement with the brand from conversation history
3. For refinements like "performance", "M", "sport", "racing" with BMW context, use "BMW M Performance" or similar
4. If there's a color mentioned (red, black, white), include it: "BMW red logo"
5. Return ONLY the search query, nothing else
6. If unclear what to search for, return "UNCLEAR"

EXAMPLES:
- User says "BMW logo" → Return: "BMW logo"
- Previous: "BMW logo", User says "the performance one" → Return: "BMW M Performance logo"
- Previous: "BMW logo", User says "i want the red logo for the performance" → Return: "BMW M Performance red logo"
- Previous: "Nike", User says "the swoosh" → Return: "Nike swoosh logo"

Search query:"""

            # Call Mistral AI
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': self.model,
                'messages': [
                    {'role': 'user', 'content': extraction_prompt}
                ],
                'temperature': 0.3,  # Lower temperature for more consistent extraction
                'max_tokens': 50  # Short response expected
            }
            
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            response.raise_for_status()
            data = response.json()
            
            ai_query = data['choices'][0]['message']['content'].strip()
            print(f"🤖 AI extracted query: '{ai_query}'")
            
            # Validate AI response
            if ai_query and ai_query != "UNCLEAR" and len(ai_query) > 2:
                # Clean up any extra explanation
                ai_query = ai_query.split('\n')[0].strip()
                # Remove quotes if present
                ai_query = ai_query.strip('"\'')
                
                # Ensure it contains "logo" if not already
                if 'logo' not in ai_query.lower():
                    ai_query = f"{ai_query} logo"
                
                print(f"✅ Final AI query: '{ai_query}'")
                return ai_query
            else:
                print(f"⚠️ AI couldn't extract clear query, falling back to regex")
                return None
                
        except Exception as e:
            print(f"⚠️ AI extraction failed: {e}, falling back to regex")
            return None
    
    def extract_photo_search_query(self, text: str, conversation_history: Optional[List[Dict]] = None) -> Optional[str]:
        """
        Extract the subject/query for photo search from user message
        Uses Mistral AI first for intelligent context analysis, falls back to regex patterns
        
        Args:
            text (str): User message
            conversation_history (Optional[List[Dict]]): Recent conversation for context
            
        Returns:
            Optional[str]: Extracted search query or None
        """
        print(f"🔍 Extracting query from: '{text}'")
        print(f"📝 History available: {len(conversation_history) if conversation_history else 0} messages")
        
        # Try AI-powered extraction first (better context understanding)
        ai_query = self.extract_photo_search_query_with_ai(text, conversation_history)
        if ai_query:
            return ai_query
        
        print(f"⚠️ Falling back to regex-based extraction")
        
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
                    # Check if this is a generic descriptor without a brand name
                    # (e.g., "performance logo", "red logo", etc.)
                    query_words = query.lower().replace(' logo', '').strip().split()
                    generic_descriptors = ['performance', 'red', 'black', 'white', 'blue', 'sport', 'racing', 
                                          'classic', 'vintage', 'new', 'old', 'the', 'a', 'an', 'that', 
                                          'this', 'my', 'their', 'its']
                    
                    # If query only contains generic descriptors, try to get brand from context
                    if all(word in generic_descriptors for word in query_words):
                        print(f"⚠️ Generic query detected: '{query}' - checking context for brand")
                        # Don't return yet, continue to context extraction below
                        break
                    else:
                        print(f"✅ Specific query found: '{query}'")
                        return query
        
        # If no specific brand found, try to use conversation context
        if conversation_history and len(conversation_history) > 0:
            text_lower = text.lower().strip()
            
            # Check if this is a refinement of a previous search (e.g., "the red one", "the performance version")
            refinement_patterns = [
                r'\b(?:the|a|an)\s+([\w\s]+?)\s+(?:logo|one|version)\b',  # "the red logo", "the performance one"
                r'\bi\s+want\s+(?:the\s+)?([\w\s]+?)\s+(?:logo|one|version)\b',  # "i want the red logo"
                r'\bfor\s+(?:the\s+)?([\w\s]+?)(?:\s+logo)?\b',  # "for the performance"
            ]
            
            refinement_query = None
            for pattern in refinement_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    refinement_query = match.group(1).strip()
                    break
            
            # Look for brand names or topics in recent conversation
            previous_brand = None
            for msg in reversed(conversation_history[-5:]):  # Check last 5 messages
                content = msg.get('content', '')
                
                # Try multiple patterns to find brand names
                brand_patterns = [
                    r'\b([A-Z][\w]+(?:\s+[A-Z][\w]+)?)\s+logo\b',  # "BMW logo"
                    r'(?:searching|found|search).*?(?:for|:)\s+([A-Z][\w]+)',  # "Searching for: BMW"
                    r'(?:photos?|images?|logo).*?(?:of|for)\s+([A-Z][\w]+)',  # "photo of BMW"
                ]
                
                for brand_pattern in brand_patterns:
                    context_match = re.search(brand_pattern, content)
                    if context_match:
                        previous_brand = context_match.group(1).strip()
                        print(f"✅ Found brand in context: '{previous_brand}' from message: '{content[:50]}...'")
                        break
                
                if previous_brand:
                    break
            
            # If we have both a refinement and a previous brand, combine them
            if refinement_query and previous_brand:
                print(f"🔗 Combining brand '{previous_brand}' + refinement '{refinement_query}'")
                # Common refinement terms that should be appended to brand
                refinement_terms = {
                    'red': 'red',
                    'performance': 'M Performance',  # BMW M Performance
                    'sport': 'sport',
                    'racing': 'racing',
                    'motorsport': 'motorsport',
                    'm': 'M',
                    'black': 'black',
                    'white': 'white',
                    'classic': 'classic',
                    'vintage': 'vintage',
                    'new': 'new',
                    'old': 'old'
                }
                
                # Check if refinement is a color/variant
                for key, value in refinement_terms.items():
                    if key in refinement_query.lower():
                        return f"{previous_brand} {value} logo"
                
                # General refinement
                return f"{previous_brand} {refinement_query} logo"
            
            # If we just have a previous brand and generic phrases
            if previous_brand:
                generic_phrases = ['search for it', 'show me', 'find it', 'look it up', 'get it', 'that one', 'search it']
                if any(phrase in text_lower for phrase in generic_phrases):
                    return f"{previous_brand} logo"
        
        return None
    
    def classify_user_intent_with_ai(self, text: str, conversation_history: Optional[List[Dict]] = None) -> Dict:
        """
        Use Mistral AI to classify user intent with better context understanding.
        
        Args:
            text (str): User message
            conversation_history (Optional[List[Dict]]): Recent conversation for context
            
        Returns:
            Dict: Intent classification result or None if AI fails
        """
        print(f"🤖 Using AI to classify intent for: '{text[:50]}...'")
        
        try:
            # Build context from conversation history
            context_messages = []
            if conversation_history:
                for msg in conversation_history[-5:]:
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    if content:
                        context_messages.append(f"{role.upper()}: {content}")
            
            context_str = "\n".join(context_messages) if context_messages else "No previous context"
            
            # Create AI prompt for intent classification
            intent_prompt = f"""You are analyzing user intent in a logo design and search application.

CONVERSATION HISTORY:
{context_str}

CURRENT USER MESSAGE:
{text}

TASK:
Classify the user's intent into ONE of these categories:

1. "search" - User wants to FIND/SEARCH for an existing logo/brand image
   Examples: "show me the BMW logo", "search for Nike logo", "find the Apple logo"

2. "generate" - User wants to CREATE/GENERATE a new logo
   Examples: "create a logo for my startup", "design a logo", "make a minimalist logo"

3. "confirmation" - User is confirming/accepting a previous suggestion
   Examples: "yes", "looks good", "perfect", "use it", "that's correct"

4. "refinement" - User is refining/rejecting a previous result
   Examples: "no", "different", "change the color", "make it more modern"

5. "conversation" - General conversation or questions
   Examples: "hello", "how are you", "what can you do", "help"

RULES:
- If the conversation shows a pending search/generation and user responds with refinement, classify as "refinement"
- If user mentions specific brand names to find/search, it's "search"
- If user wants to create something new, it's "generate"
- Consider the conversation context heavily

Respond ONLY with this JSON format:
{{"intent": "search|generate|confirmation|refinement|conversation", "confidence": 0.0-1.0, "reasoning": "brief explanation"}}"""

            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': self.model,
                'messages': [
                    {'role': 'user', 'content': intent_prompt}
                ],
                'temperature': 0.2,
                'max_tokens': 100
            }
            
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            response.raise_for_status()
            data = response.json()
            
            ai_response = data['choices'][0]['message']['content'].strip()
            print(f"🤖 AI intent response: {ai_response}")
            
            # Parse JSON response
            # Clean up markdown code blocks if present
            ai_response = ai_response.replace('```json', '').replace('```', '').strip()
            
            result = json.loads(ai_response)
            
            if result.get('intent') and result.get('confidence'):
                print(f"✅ AI classified as: {result['intent']} (confidence: {result['confidence']})")
                return {
                    'intent': result['intent'],
                    'confidence': float(result['confidence']),
                    'context': {'reasoning': result.get('reasoning', ''), 'ai_powered': True}
                }
            else:
                print(f"⚠️ Invalid AI response format, falling back")
                return None
                
        except Exception as e:
            print(f"⚠️ AI intent classification failed: {e}, falling back to regex")
            return None
    
    def classify_user_intent(self, text: str, conversation_history: Optional[List[Dict]] = None) -> Dict:
        """
        Classify user intent with high accuracy using AI first, then multiple signals as fallback
        
        Args:
            text (str): User message
            conversation_history (Optional[List[Dict]]): Recent conversation for context
            
        Returns:
            Dict: {
                'intent': 'generate' | 'search' | 'conversation' | 'confirmation',
                'confidence': float (0.0-1.0),
                'context': Dict with additional context
            }
        """
        # Try AI-powered classification first
        ai_result = self.classify_user_intent_with_ai(text, conversation_history)
        if ai_result:
            return ai_result
        
        print(f"⚠️ Falling back to regex-based intent classification")
        
        text_lower = text.lower().strip()
        
        # Check for simple confirmations/rejections first
        confirmation_words = ['yes', 'yeah', 'yep', 'sure', 'ok', 'okay', 'confirm', 'go ahead', 'proceed', 'perfect', '✅']
        rejection_words = ['no', 'nope', 'cancel', 'stop', 'different', 'again', '❌']
        
        # Very short messages are likely confirmations/rejections in context
        if len(text.split()) <= 3:
            if any(word in text_lower for word in confirmation_words):
                return {
                    'intent': 'confirmation',
                    'confidence': 0.9,
                    'context': {'type': 'positive'}
                }
            elif any(word in text_lower for word in rejection_words):
                return {
                    'intent': 'confirmation',
                    'confidence': 0.9,
                    'context': {'type': 'negative'}
                }
        
        # Check for explicit search intent (highest priority for existing logos)
        search_confidence = 0.0
        search_indicators = {
            r'\bsearch\s+(?:for\s+)?': 0.9,
            r'\bfind\s+(?:the\s+)?\w+\s+logo\b': 0.85,
            r'\bshow\s+me\s+(?:the\s+)?\w+\s+logo\b': 0.85,
            r'\bwhat\s+(?:does|is)\s+\w+\s+logo\s+look\s*like\b': 0.8,
            r'\b(get|fetch|display)\s+(?:the\s+)?logo\s+(?:of|for)\b': 0.8,
            r'\b[A-Z][a-z]+\s+logo\b': 0.7,  # "Nike logo", "Apple logo"
            r'\bthe\s+\w+\s+logo\b': 0.6,
        }
        
        for pattern, confidence in search_indicators.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                search_confidence = max(search_confidence, confidence)
        
        # Check for explicit generation intent
        generation_confidence = 0.0
        generation_indicators = {
            r'\b(create|generate|make)\s+(?:a|an|my)?\s*(?:new\s+)?logo\b': 0.95,
            r'\bdesign\s+(?:a|an|my)?\s*logo\s+for\b': 0.9,
            r'\blogo\s+for\s+(?:my|our)\s+\w+\b': 0.85,
            r'\b(create|make|design)\s+something\s+(like|similar|inspired)\b': 0.8,
            r'\bI\s+(?:want|need)\s+(?:a|an)\s+logo\b': 0.85,
        }
        
        for pattern, confidence in generation_indicators.items():
            if re.search(pattern, text_lower):
                generation_confidence = max(generation_confidence, confidence)
        
        # Contextual analysis from conversation history
        context_search_boost = 0.0
        context_generation_boost = 0.0
        
        if conversation_history and len(conversation_history) > 0:
            recent_messages = conversation_history[-3:]
            context_text = " ".join([msg.get('content', '') for msg in recent_messages]).lower()
            
            # Check what the conversation was about
            if any(word in context_text for word in ['search', 'find', 'show', 'reference', 'existing']):
                context_search_boost = 0.2
            
            if any(word in context_text for word in ['create', 'design', 'generate', 'my logo', 'our logo']):
                context_generation_boost = 0.2
        
        # Apply context boosts
        search_confidence += context_search_boost
        generation_confidence += context_generation_boost
        
        # Disambiguate: "search" keywords in generation context
        # Example: "search for inspiration then create a logo"
        if generation_confidence > 0.5 and search_confidence > 0.5:
            # Check for temporal indicators
            if re.search(r'\b(then|after|once|when)\b', text_lower):
                # Multiple intents - prioritize based on order
                search_first = text_lower.find('search') < text_lower.find('create') if 'create' in text_lower else True
                if search_first:
                    search_confidence += 0.2
                else:
                    generation_confidence += 0.2
        
        # Determine intent based on confidence scores
        max_confidence = max(search_confidence, generation_confidence)
        
        if max_confidence >= 0.6:
            if search_confidence > generation_confidence:
                return {
                    'intent': 'search',
                    'confidence': min(search_confidence, 1.0),
                    'context': {'query_extraction_needed': True}
                }
            else:
                return {
                    'intent': 'generate',
                    'confidence': min(generation_confidence, 1.0),
                    'context': {'prompt_extraction_needed': True}
                }
        
        # Low confidence - likely just conversation
        return {
            'intent': 'conversation',
            'confidence': 0.5,
            'context': {'needs_clarification': max_confidence > 0.3}
        }
    
    def extract_image_prompt(self, response_text: str) -> Optional[str]:
        """
        Extract image generation prompt from Mistral response if it contains JSON action
        Truncates prompts that are too long for CLIP text encoder (77 token limit)
        
        Args:
            response_text (str): Mistral response
            
        Returns:
            Optional[str]: Extracted and truncated prompt or None
        """
        try:
            # Try to parse as JSON
            data = json.loads(response_text)
            if isinstance(data, dict) and data.get('action') == 'generate_image':
                prompt = data.get('prompt')
                if prompt:
                    return self._truncate_prompt(prompt)
        except json.JSONDecodeError:
            # Try to extract JSON from text
            json_match = re.search(r'\{[^}]*"action"\s*:\s*"generate_image"[^}]*\}', response_text)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                    prompt = data.get('prompt')
                    if prompt:
                        return self._truncate_prompt(prompt)
                except:
                    pass
        
        return None
    
    def _truncate_prompt(self, prompt: str, max_length: int = 300) -> str:
        """
        Intelligently truncate prompt to stay under CLIP's 77 token limit
        
        Args:
            prompt (str): Original prompt
            max_length (int): Maximum character length (default 300 for ~75 tokens)
            
        Returns:
            str: Truncated prompt
        """
        if len(prompt) <= max_length:
            return prompt
        
        print(f"⚠️ Prompt too long ({len(prompt)} chars), truncating to {max_length} chars")
        
        # Truncate at word boundary to avoid cutting mid-word
        truncated = prompt[:max_length].rsplit(' ', 1)[0]
        
        # Add ellipsis if doesn't end with punctuation
        if truncated and not truncated[-1] in '.!?,;':
            truncated += '...'
        
        print(f"✓ Truncated prompt: {truncated}")
        return truncated
    
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
        Send a message to Mistral AI and get response with enhanced context awareness
        
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
        
        # === STEP 1: Classify user intent BEFORE processing ===
        intent_data = self.classify_user_intent(user_message, conversation_history)
        user_intent = intent_data['intent']
        intent_confidence = intent_data['confidence']
        
        print(f"🎯 Detected intent: {user_intent} (confidence: {intent_confidence:.2f})")
        
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
                # Get the original pending request data
                original_logo_data = self.pending_logo_requests.get(user_id, {})
                
                # Clear the pending request
                self.pending_logo_requests.pop(user_id)
                
                # Check if user provided specific changes or new request
                if len(user_message.split()) > 2:  # More than just "no" or "search again"
                    # Remove the rejection word to get the actual refinement
                    refinement_text = user_message
                    for keyword in ['no', 'nope', 'not', 'different']:
                        refinement_text = re.sub(rf'\b{keyword}\b', '', refinement_text, flags=re.IGNORECASE)
                    refinement_text = refinement_text.strip()
                    
                    # Check if this is a search request or a refinement
                    is_search_request = self.is_photo_search_request(refinement_text, conversation_history)
                    
                    # Check for logo refinement keywords that indicate generation, not search
                    logo_refinement_keywords = [
                        'without', 'with', 'add', 'remove', 'change', 'make it',
                        'style', 'color', 'shape', 'design', 'simpler', 'modern',
                        'minimalist', 'bold', 'clean', 'professional', 'playful',
                        'name', 'text', 'icon', 'symbol', 'background'
                    ]
                    has_refinement_keyword = any(keyword in refinement_text.lower() for keyword in logo_refinement_keywords)
                    
                    # If it has refinement keywords, it's definitely a logo refinement, not search
                    if has_refinement_keyword:
                        is_search_request = False
                        print(f"🎨 Detected logo refinement (has refinement keywords)")
                    
                    # If it's clearly a search (e.g., "no, search for Nike logo"), don't process as logo
                    if is_search_request and use_web_search and not has_refinement_keyword:
                        print(f"🔍 User wants to search instead: {refinement_text}")
                        # Let it fall through to normal search handling
                        # Clear the pending and return None to trigger search flow
                        return (None, False, None, None)
                    
                    # Otherwise, treat as logo generation refinement
                    # Combine original request context with refinement
                    original_request = original_logo_data.get('request_data', {}).get('raw_request', '')
                    combined_request = f"{original_request}. Refinement: {refinement_text}" if original_request else refinement_text
                    
                    print(f"🎨 Processing refinement: {refinement_text}")
                    
                    # User provided specific refinement, re-process with new request
                    try:
                        logo_result = self.logo_agent.process_logo_request(combined_request)
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
        
            # === STEP 2: Handle based on detected intent ===
            
            # HIGH-CONFIDENCE SEARCH INTENT - Direct search without asking Mistral
            if user_intent == 'search' and intent_confidence >= 0.75 and use_web_search:
                search_query = self.extract_photo_search_query(user_message, conversation_history)
                if search_query:
                    print(f"🔍 Direct search triggered: {search_query}")
                    try:
                        photo_result = self.logo_agent.search_for_photo(search_query)
                        
                        if photo_result.get('success'):
                            preview_text = self.logo_agent.format_photo_preview(photo_result)
                            if user_id:
                                self.pending_photo_requests[user_id] = photo_result
                            
                            return (preview_text, False, None, {'_web_search_result': True, 'photo_result': photo_result})
                    except Exception as e:
                        print(f"Error in direct search: {e}")
                        # Continue with normal response
            
            # HIGH-CONFIDENCE GENERATION INTENT - Skip search, go straight to generation prep
            if user_intent == 'generate' and intent_confidence >= 0.8:
                print(f"🎨 High-confidence generation detected")
                # If web search is enabled, use Logo Reference Agent
                if use_web_search:
                    try:
                        logo_result = self.logo_agent.process_logo_request(user_message)
                        
                        if logo_result.get('success'):
                            preview_text = self.logo_agent.format_preview_for_user(logo_result)
                            
                            if user_id:
                                self.pending_logo_requests[user_id] = logo_result
                            
                            return (preview_text, False, None, logo_result)
                    except Exception as e:
                        print(f"Error in logo agent processing: {e}")
                        # Continue with normal Mistral processing
            
            # === STEP 3: Check if this is a logo generation request (fallback for lower confidence) ===
            # Only use Logo Reference Agent when web search is ENABLED
            if self.is_image_generation_request(user_message, conversation_history) and use_web_search and user_intent != 'search':
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
