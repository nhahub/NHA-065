"""
Logo Reference Agent for Zypher AI Logo Generator
Gathers real-time visual references and generates optimized logo prompts using Brave Search API
"""
import os
import json
import requests
import time
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
import re
from bs4 import BeautifulSoup

load_dotenv()


class LogoReferenceAgent:
    """
    Agent for gathering real-time visual references and generating optimized logo prompts.
    Uses Brave Search API to find design references and extract visual patterns.
    """
    
    def __init__(self):
        self.brave_api_key = os.getenv('BRAVE_SEARCH_API_KEY', '')
        self.brave_search_endpoint = 'https://api.search.brave.com/res/v1/web/search'
        self.brave_image_search_endpoint = 'https://api.search.brave.com/res/v1/images/search'
        self.last_api_call_time = 0  # Track last API call for rate limiting
        self.rate_limit_delay = 1.1  # Brave API: max 1 request/second, use 1.1s to be safe
        
        if not self.brave_api_key or self.brave_api_key == 'your_brave_api_key_here':
            print("⚠️  WARNING: BRAVE_SEARCH_API_KEY not set in .env file")
            print("   Get your API key from: https://brave.com/search/api/")
    
    def _enforce_rate_limit(self):
        """Ensure at least 1 second between Brave API calls (Brave limit: 1 req/sec)."""
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call_time
        
        if time_since_last_call < self.rate_limit_delay:
            wait_time = self.rate_limit_delay - time_since_last_call
            print(f"⏱️ Rate limiting: waiting {wait_time:.2f}s...")
            time.sleep(wait_time)
        
        self.last_api_call_time = time.time()
    
    def parse_user_request(self, user_message: str) -> Dict:
        """
        Parse the user's logo request to extract key information.
        
        Args:
            user_message (str): The user's logo request
            
        Returns:
            Dict: Parsed request with brand_name, domain, style, colors, themes
        """
        request_data = {
            'brand_name': None,
            'domain': None,
            'style': [],
            'colors': [],
            'themes': [],
            'symbols': [],
            'raw_request': user_message
        }
        
        # Extract brand name (look for "for [brand name]" or quotes)
        brand_patterns = [
            r'(?:for|called|named)\s+["\']?([A-Z][a-zA-Z0-9\s&]+)["\']?',
            r'["\']([A-Z][a-zA-Z0-9\s&]+)["\']',
        ]
        for pattern in brand_patterns:
            match = re.search(pattern, user_message)
            if match:
                request_data['brand_name'] = match.group(1).strip()
                break
        
        # Extract domain/industry keywords
        domain_keywords = [
            'tech', 'technology', 'startup', 'software', 'app', 'digital',
            'food', 'restaurant', 'cafe', 'bakery', 'juice', 'beverage',
            'fashion', 'clothing', 'apparel', 'boutique',
            'fitness', 'gym', 'health', 'wellness', 'yoga',
            'finance', 'bank', 'consulting', 'business',
            'education', 'school', 'learning', 'academy',
            'music', 'entertainment', 'gaming', 'esports',
            'real estate', 'construction', 'architecture',
            'medical', 'healthcare', 'pharmacy', 'clinic',
            'automotive', 'car', 'vehicle', 'transport'
        ]
        
        message_lower = user_message.lower()
        for keyword in domain_keywords:
            if keyword in message_lower:
                request_data['domain'] = keyword
                break
        
        # Extract style keywords
        style_keywords = [
            'minimal', 'minimalist', 'modern', 'vintage', 'retro', 
            'abstract', 'geometric', 'organic', 'bold', 'elegant',
            'playful', 'professional', 'luxury', 'futuristic', 'clean',
            'flat', '3d', 'gradient', 'monochrome', 'colorful'
        ]
        for style in style_keywords:
            if style in message_lower:
                request_data['style'].append(style)
        
        # Extract color keywords
        color_keywords = [
            'blue', 'red', 'green', 'yellow', 'orange', 'purple', 'pink',
            'black', 'white', 'gray', 'grey', 'gold', 'silver', 'neon',
            'pastel', 'vibrant', 'dark', 'light', 'bright'
        ]
        for color in color_keywords:
            if color in message_lower:
                request_data['colors'].append(color)
        
        return request_data
    
    def search_design_references(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search Brave for design references and trends.
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            
        Returns:
            List[Dict]: Search results with title, url, description
        """
        if not self.brave_api_key or self.brave_api_key == 'your_brave_api_key_here':
            return [{
                'title': 'No API Key',
                'url': '',
                'description': 'Brave Search API key not configured. Please add BRAVE_SEARCH_API_KEY to .env'
            }]
        
        try:
            # Enforce rate limit before API call
            self._enforce_rate_limit()
            
            headers = {
                'Accept': 'application/json',
                'X-Subscription-Token': self.brave_api_key
            }
            
            params = {
                'q': query,
                'count': max_results,
                'search_lang': 'en'
            }
            
            response = requests.get(
                self.brave_search_endpoint,
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 401:
                return [{
                    'title': 'Invalid API Key',
                    'url': '',
                    'description': 'Invalid Brave Search API key. Please check your BRAVE_SEARCH_API_KEY in .env'
                }]
            
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get('web', {}).get('results', [])[:max_results]:
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('url', ''),
                    'description': item.get('description', '')
                })
            
            return results
            
        except requests.exceptions.Timeout:
            return [{
                'title': 'Timeout',
                'url': '',
                'description': 'Search request timed out. Please try again.'
            }]
        except Exception as e:
            print(f"Error searching Brave: {e}")
            return [{
                'title': 'Error',
                'url': '',
                'description': f'Search error: {str(e)}'
            }]
    
    def extract_visual_features(self, request_data: Dict, search_results: List[Dict]) -> Dict:
        """
        Extract visual identity patterns from search results and industry knowledge.
        
        Args:
            request_data (Dict): Parsed user request
            search_results (List[Dict]): Search results from Brave
            
        Returns:
            Dict: Extracted visual features including shapes, colors, typography, composition
        """
        features = {
            'shapes': [],
            'icons': [],
            'colors': [],
            'typography': [],
            'composition': [],
            'trends': []
        }
        
        domain = request_data.get('domain', '').lower()
        
        # Industry-specific design patterns
        industry_patterns = {
            'tech': {
                'shapes': ['geometric', 'abstract', 'angular', 'circuit-inspired'],
                'icons': ['digital elements', 'network nodes', 'data symbols'],
                'colors': ['blue', 'cyan', 'purple', 'gradient'],
                'typography': ['sans-serif', 'geometric', 'modern'],
                'composition': ['minimal', 'flat design', 'negative space']
            },
            'food': {
                'shapes': ['circular', 'organic', 'leaf-like', 'rounded'],
                'icons': ['food items', 'utensils', 'natural elements'],
                'colors': ['warm tones', 'red', 'orange', 'green', 'brown'],
                'typography': ['handwritten', 'friendly', 'rounded'],
                'composition': ['badge', 'emblem', 'illustrative']
            },
            'juice': {
                'shapes': ['circular', 'droplet', 'fruit-inspired', 'organic'],
                'icons': ['fruits', 'leaves', 'droplets', 'splash'],
                'colors': ['vibrant', 'orange', 'green', 'yellow', 'fresh'],
                'typography': ['playful', 'rounded', 'energetic'],
                'composition': ['colorful', 'dynamic', 'fresh']
            },
            'fitness': {
                'shapes': ['angular', 'dynamic', 'bold', 'athletic'],
                'icons': ['body silhouettes', 'dumbbells', 'movement'],
                'colors': ['bold', 'red', 'black', 'energetic'],
                'typography': ['bold', 'strong', 'athletic'],
                'composition': ['dynamic', 'powerful', 'motivational']
            },
            'fashion': {
                'shapes': ['elegant', 'flowing', 'sophisticated'],
                'icons': ['hangers', 'threads', 'fashion elements'],
                'colors': ['black', 'gold', 'elegant', 'luxury'],
                'typography': ['serif', 'elegant', 'luxury'],
                'composition': ['minimalist', 'sophisticated', 'luxury']
            },
            'finance': {
                'shapes': ['stable', 'geometric', 'symmetrical'],
                'icons': ['graphs', 'arrows', 'stability symbols'],
                'colors': ['blue', 'green', 'trust colors', 'professional'],
                'typography': ['professional', 'serif', 'trustworthy'],
                'composition': ['balanced', 'professional', 'trustworthy']
            }
        }
        
        # Apply industry patterns if domain is recognized
        if domain in industry_patterns:
            pattern = industry_patterns[domain]
            features['shapes'] = pattern['shapes']
            features['icons'] = pattern['icons']
            features['colors'] = pattern['colors']
            features['typography'] = pattern['typography']
            features['composition'] = pattern['composition']
        
        # Enhance with user-specified colors and styles
        if request_data.get('colors'):
            features['colors'].extend(request_data['colors'])
        
        if request_data.get('style'):
            features['composition'].extend(request_data['style'])
        
        # Extract insights from search results
        all_text = ' '.join([
            r.get('title', '') + ' ' + r.get('description', '')
            for r in search_results
        ]).lower()
        
        # Look for design trend keywords in search results
        trend_keywords = [
            'gradient', 'minimalist', 'bold', 'vintage', 'modern',
            'flat design', '3d', 'geometric', 'abstract', 'monogram',
            'lettermark', 'wordmark', 'emblem', 'mascot', 'combination'
        ]
        
        for keyword in trend_keywords:
            if keyword in all_text:
                features['trends'].append(keyword)
        
        # Deduplicate lists
        for key in features:
            features[key] = list(set(features[key]))
        
        return features
    
    def construct_diffusion_prompt(self, request_data: Dict, visual_features: Dict) -> str:
        """
        Generate a high-quality, structured logo prompt for diffusion models.
        
        Args:
            request_data (Dict): Parsed user request
            visual_features (Dict): Extracted visual features
            
        Returns:
            str: Complete prompt optimized for logo generation
        """
        prompt_parts = []
        
        # Brand name (if provided)
        if request_data.get('brand_name'):
            prompt_parts.append(f"Logo for '{request_data['brand_name']}'")
        else:
            prompt_parts.append("Professional logo design")
        
        # Domain/industry context
        if request_data.get('domain'):
            prompt_parts.append(f"for {request_data['domain']} industry")
        
        # Symbol/icon direction
        if visual_features.get('icons'):
            icon_desc = ', '.join(visual_features['icons'][:3])
            prompt_parts.append(f"featuring {icon_desc}")
        
        # Shape language
        if visual_features.get('shapes'):
            shape_desc = ', '.join(visual_features['shapes'][:2])
            prompt_parts.append(f"with {shape_desc} shapes")
        
        # Color palette
        if visual_features.get('colors'):
            color_desc = ', '.join(visual_features['colors'][:3])
            prompt_parts.append(f"using {color_desc} colors")
        
        # Composition style
        if visual_features.get('composition'):
            comp_desc = ', '.join(visual_features['composition'][:2])
            prompt_parts.append(f"{comp_desc} style")
        
        # Typography style
        if visual_features.get('typography'):
            typo_desc = visual_features['typography'][0]
            prompt_parts.append(f"with {typo_desc} typography")
        
        # Add logo-specific constraints (keep concise for CLIP's 77 token limit)
        prompt_parts.append("clean minimal")
        prompt_parts.append("professional modern")
        
        # Join all parts
        final_prompt = ', '.join(prompt_parts)
        
        # CRITICAL: CLIP has a 77 token limit (~300-350 characters safe limit)
        # Truncate intelligently to avoid diffuser errors
        if len(final_prompt) > 300:
            # Keep the most important parts (brand, industry, main features)
            truncated_parts = prompt_parts[:6]  # Keep first 6 most important parts
            final_prompt = ', '.join(truncated_parts)
            
            # Final safety check
            if len(final_prompt) > 300:
                final_prompt = final_prompt[:297] + '...'
        
        return final_prompt
    
    def process_logo_request(self, user_message: str) -> Dict:
        """
        Main workflow: Process a logo request end-to-end.
        
        Args:
            user_message (str): User's logo request
            
        Returns:
            Dict: Complete result with extracted features and final prompt
        """
        # Step 1: Parse user request
        request_data = self.parse_user_request(user_message)
        
        # Step 2: Construct search queries
        search_queries = []
        
        if request_data.get('domain'):
            search_queries.append(f"{request_data['domain']} logo design trends 2025")
            search_queries.append(f"best {request_data['domain']} logos")
        
        if request_data.get('brand_name'):
            search_queries.append(f"logo design inspiration for {request_data['brand_name']}")
        
        # Default search if no specific queries
        if not search_queries:
            search_queries.append("modern logo design trends 2025")
        
        # Step 3: Search for references (use first query)
        search_results = self.search_design_references(search_queries[0], max_results=5)
        
        # Step 4: Extract visual features
        visual_features = self.extract_visual_features(request_data, search_results)
        
        # Step 5: Construct diffusion prompt
        final_prompt = self.construct_diffusion_prompt(request_data, visual_features)
        
        # Return comprehensive result
        return {
            'success': True,
            'request_data': request_data,
            'search_results': search_results,
            'extracted_visual_features': visual_features,
            'final_diffusion_prompt': final_prompt,
            'confidence': 'high' if request_data.get('domain') else 'medium'
        }
    
    def format_preview_for_user(self, result: Dict) -> str:
        """
        Format the extracted features for user preview/confirmation.
        
        Args:
            result (Dict): Result from process_logo_request
            
        Returns:
            str: Formatted preview text
        """
        features = result['extracted_visual_features']
        request = result['request_data']
        
        preview_lines = []
        preview_lines.append("🎨 **Logo Design Preview**\n")
        
        if request.get('brand_name'):
            preview_lines.append(f"**Brand:** {request['brand_name']}")
        
        if request.get('domain'):
            preview_lines.append(f"**Industry:** {request['domain'].title()}")
        
        if features.get('shapes'):
            preview_lines.append(f"**Shapes:** {', '.join(features['shapes'][:3])}")
        
        if features.get('icons'):
            preview_lines.append(f"**Icons/Symbols:** {', '.join(features['icons'][:3])}")
        
        if features.get('colors'):
            preview_lines.append(f"**Colors:** {', '.join(features['colors'][:4])}")
        
        if features.get('composition'):
            preview_lines.append(f"**Style:** {', '.join(features['composition'][:3])}")
        
        if features.get('typography'):
            preview_lines.append(f"**Typography:** {', '.join(features['typography'][:2])}")
        
        preview_lines.append(f"\n**Generated Prompt:**")
        preview_lines.append(f"_{result['final_diffusion_prompt']}_")
        
        preview_lines.append("\n✅ **Confirm** to generate | ❌ **Refine** to search again")
        
        return '\n'.join(preview_lines)
    
    def search_for_photo(self, query: str, max_results: int = 3) -> Dict:
        """
        Search for multiple photos/logos using Brave Image Search API.
        Returns direct image URLs from CDNs, image hosts, and accessible sources.
        
        Args:
            query (str): Search query for the photo/logo
            max_results (int): Maximum number of results to return (default 3 for grid)
            
        Returns:
            Dict: Search results with multiple images, titles, sources, and metadata
        """
        if not self.brave_api_key or self.brave_api_key == 'your_brave_api_key_here':
            return {
                'success': False,
                'error': 'Brave Search API key not configured. Please add BRAVE_SEARCH_API_KEY to .env'
            }
        
        try:
            # Enforce rate limit before API call
            self._enforce_rate_limit()
            
            headers = {
                'Accept': 'application/json',
                'X-Subscription-Token': self.brave_api_key
            }
            
            # Add "logo" to query if not already present
            search_query = query
            if 'logo' not in query.lower():
                search_query = f"{query} logo"
            
            # Clean query: remove special characters that might cause 422
            search_query = search_query.strip()
            # Remove multiple spaces
            search_query = ' '.join(search_query.split())
            
            # Use Brave Image Search API for direct image URLs
            params = {
                'q': search_query,
                'count': min(max_results * 3, 20),  # Request more to filter, max 20
                'search_lang': 'en',
                'safesearch': 'strict'  # Brave API only accepts 'strict' or 'off', not 'moderate'
            }
            
            print(f"🔍 Searching images for: {params['q']}")
            print(f"📍 Using endpoint: {self.brave_image_search_endpoint}")
            
            response = requests.get(
                self.brave_image_search_endpoint,  # Use IMAGE search endpoint
                headers=headers,
                params=params,
                timeout=15
            )
            
            print(f"📊 Response status: {response.status_code}")
            
            if response.status_code == 401:
                print(f"❌ Authentication failed - check API key")
                return {
                    'success': False,
                    'error': 'Invalid Brave Search API key. Please check your BRAVE_SEARCH_API_KEY in .env'
                }
            
            if response.status_code == 429:
                print(f"⚠️ Rate limit hit")
                return {
                    'success': False,
                    'error': 'Rate limit reached. Please try again in a moment.'
                }
            
            if response.status_code == 422:
                print(f"⚠️ Invalid query format (422) - trying fallback")
                # Don't raise, let it fall through to fallback
                raise requests.exceptions.HTTPError(response=response)
            
            response.raise_for_status()
            data = response.json()
            
            # Get image results from Brave Image Search
            image_data = data.get('results', [])
            
            print(f"📦 API returned {len(image_data)} total results")
            
            if not image_data:
                print(f"⚠️ No results from image API, trying fallback")
                return self._fallback_web_search(query, max_results)
            
            # Filter for accessible image sources
            accessible_sources = [
                'wikimedia.org', 'wikipedia.org', 'imgur.com', 
                'cloudinary.com', 'wp.com', 'wordpress.com',
                'blogspot.com', 'tumblr.com', 'flickr.com',
                'pinimg.com', 'medium.com', 'githubusercontent.com',
                'googleusercontent.com', 'staticflickr.com',
                'unsplash.com', 'pexels.com', 'pixabay.com',
                'cdninstagram.com', 'fbcdn.net', 'twimg.com'
            ]
            
            # Blocked sources (known to block downloads)
            blocked_sources = [
                'shutterstock.com', 'gettyimages.com', 'istockphoto.com',
                'stock.adobe.com', 'alamy.com', 'dreamstime.com'
            ]
            
            # Process and prioritize image results
            image_results = []
            
            for result in image_data:
                if len(image_results) >= max_results:
                    break
                
                # Get image properties
                properties = result.get('properties', {})
                thumbnail = result.get('thumbnail', {})
                page_url = result.get('url', '')
                
                # Get direct image URL
                image_url = properties.get('url', '')
                thumbnail_url = thumbnail.get('src', '')
                
                if not image_url:
                    continue
                
                # Validate URL format
                if not (image_url.startswith('http://') or image_url.startswith('https://')):
                    continue
                
                # Check if from blocked source
                is_blocked = any(blocked in image_url.lower() for blocked in blocked_sources)
                if is_blocked:
                    print(f"⚠️ Skipping blocked source: {image_url}")
                    continue
                
                # Get source information
                source_url = properties.get('page', page_url)
                hostname = ''
                try:
                    from urllib.parse import urlparse
                    hostname = urlparse(image_url).netloc
                except:
                    hostname = 'web'
                
                title = result.get('title', 'Logo Image')
                
                # Check if from trusted/accessible source
                is_accessible = any(source in image_url.lower() for source in accessible_sources)
                
                # Prioritize accessible sources
                priority_score = 10 if is_accessible else 5
                
                # Check image dimensions (prefer larger images)
                width = properties.get('width', 0)
                height = properties.get('height', 0)
                
                # Skip very small images
                if width > 0 and height > 0 and (width < 100 or height < 100):
                    print(f"⚠️ Skipping small image: {width}x{height}")
                    continue
                
                image_results.append({
                    'image_url': image_url,
                    'thumbnail_url': thumbnail_url or image_url,  # Use full image if no thumbnail
                    'full_image_url': image_url,
                    'fallback_url': thumbnail_url,
                    'title': title,
                    'source': source_url,
                    'description': f"Logo image - {width}x{height}px" if width and height else "Logo image",
                    'hostname': hostname,
                    'is_accessible': is_accessible,
                    'is_trusted': is_accessible,
                    'width': width,
                    'height': height,
                    'priority': priority_score
                })
            
            if not image_results:
                return {
                    'success': False,
                    'error': f'No accessible images found for "{query}". Try a different search term or brand name.'
                }
            
            # Sort by priority (accessible sources first) and size
            image_results.sort(key=lambda x: (x['priority'], x['width'] * x['height']), reverse=True)
            
            # Limit to requested number
            image_results = image_results[:max_results]
            
            print(f"✅ Found {len(image_results)} accessible images")
            
            return {
                'success': True,
                'query': query,
                'results': image_results,
                'count': len(image_results)
            }
            
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Search request timed out. Please try again.'
            }
        except requests.exceptions.HTTPError as e:
            print(f"⚠️ HTTP Error {e.response.status_code}: {e}")
            if e.response.status_code == 422:
                # Fallback to web search when image search fails
                print(f"⚠️ Image search failed (422), falling back to web search...")
                return self._fallback_web_search(query, max_results)
            elif e.response.status_code == 429:
                return {
                    'success': False,
                    'error': 'Rate limit reached. Please try again in a moment.'
                }
            # Try fallback for other HTTP errors too
            print(f"⚠️ Trying fallback for HTTP {e.response.status_code}")
            return self._fallback_web_search(query, max_results)
        except Exception as e:
            print(f"❌ Error searching for photo: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            # Try fallback
            try:
                print(f"⚠️ Attempting fallback after exception...")
                return self._fallback_web_search(query, max_results)
            except Exception as fallback_error:
                print(f"❌ Fallback also failed: {fallback_error}")
                return {
                    'success': False,
                    'error': f'Search failed: {str(e)}'
                }
    
    def _fallback_web_search(self, query: str, max_results: int = 3) -> Dict:
        """
        Fallback to web search with open graph images when image search fails.
        """
        try:
            print(f"🔄 Using web search fallback for: {query}")
            
            if not self.brave_api_key or self.brave_api_key == 'your_brave_api_key_here':
                return {
                    'success': False,
                    'error': 'Brave Search API key not configured'
                }
            
            # Enforce rate limit before fallback API call
            self._enforce_rate_limit()
            
            headers = {
                'Accept': 'application/json',
                'X-Subscription-Token': self.brave_api_key
            }
            
            # Clean query for web search
            search_query = f"{query} logo".strip()
            search_query = ' '.join(search_query.split())
            
            params = {
                'q': search_query,
                'count': 20,  # Get more to filter
                'search_lang': 'en'
            }
            
            print(f"📍 Web search endpoint: {self.brave_search_endpoint}")
            
            response = requests.get(
                self.brave_search_endpoint,
                headers=headers,
                params=params,
                timeout=15
            )
            
            print(f"📊 Web search response: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            
            web_results = data.get('web', {}).get('results', [])
            print(f"📦 Web search returned {len(web_results)} results")
            
            if not web_results:
                return {
                    'success': False,
                    'error': f'No results found for "{query}". Try a different search term.'
                }
            
            # Extract images from web results
            image_results = []
            
            for result in web_results:
                if len(image_results) >= max_results:
                    break
                
                # Try to get thumbnail or open graph image
                thumbnail = result.get('thumbnail', {})
                thumbnail_url = thumbnail.get('src', '')
                
                # Also check meta_url for better source info
                meta_url = result.get('meta_url', {})
                hostname = meta_url.get('hostname', 'web')
                
                if not thumbnail_url:
                    continue
                
                # Validate URL
                if not thumbnail_url.startswith('http'):
                    continue
                
                title = result.get('title', 'Logo Image')
                description = result.get('description', '')
                page_url = result.get('url', '')
                
                # Check for accessible sources
                accessible_sources = ['wikimedia', 'wikipedia', 'imgur', 'cloudinary', 'wp.com']
                is_accessible = any(src in thumbnail_url.lower() for src in accessible_sources)
                
                image_results.append({
                    'image_url': thumbnail_url,
                    'thumbnail_url': thumbnail_url,
                    'full_image_url': thumbnail_url,
                    'fallback_url': thumbnail_url,
                    'title': title,
                    'source': page_url,
                    'description': description or f"Logo from {hostname}",
                    'hostname': hostname,
                    'is_accessible': is_accessible,
                    'is_trusted': is_accessible,
                    'width': 0,
                    'height': 0,
                    'priority': 5
                })
            
            if not image_results:
                return {
                    'success': False,
                    'error': f'No valid images found for "{query}". Try a different brand name.'
                }
            
            print(f"✅ Web search fallback found {len(image_results)} images")
            
            return {
                'success': True,
                'query': query,
                'results': image_results,
                'count': len(image_results)
            }
            
        except Exception as e:
            print(f"Fallback web search also failed: {e}")
            
            # Check if it's a rate limit error
            if '429' in str(e):
                return {
                    'success': False,
                    'error': '⏱️ **Rate Limit Reached**\n\nThe Brave Search API has usage limits.\n\n**What to do:**\n• Wait a few minutes and try again\n• OR skip the reference and describe what you want!\n\n*I can create great logos without reference images!* 🎨',
                    'rate_limited': True
                }
            
            return {
                'success': False,
                'error': f'Could not find images for "{query}". Try a different search term or describe your logo idea directly!'
            }
    
    def format_photo_preview(self, photo_result: Dict) -> str:
        """
        Format the photo search results for user preview (multiple results).
        
        Args:
            photo_result (Dict): Result from search_for_photo
            
        Returns:
            str: Formatted preview text
        """
        if not photo_result.get('success'):
            return f"❌ **Search Failed**\n\n{photo_result.get('error', 'Unknown error')}"
        
        preview_lines = []
        preview_lines.append("🔍 **Photos Found from Web Search**\n")
        preview_lines.append(f"**Found {photo_result.get('total_results', 0)} results for:** _{photo_result.get('query', '')}_\n")
        preview_lines.append("Select the best match below:")
        
        return '\n'.join(preview_lines)
