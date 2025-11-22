"""
Logo Reference Agent for Zypher AI Logo Generator
Gathers real-time visual references and generates optimized logo prompts using Brave Search API
"""
import os
import json
import requests
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
        
        if not self.brave_api_key or self.brave_api_key == 'your_brave_api_key_here':
            print("⚠️  WARNING: BRAVE_SEARCH_API_KEY not set in .env file")
            print("   Get your API key from: https://brave.com/search/api/")
    
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
        
        # Add logo-specific constraints
        prompt_parts.append("clean and minimal")
        prompt_parts.append("scalable vector style")
        prompt_parts.append("professional and modern")
        prompt_parts.append("suitable for branding")
        
        # Join all parts
        final_prompt = ', '.join(prompt_parts)
        
        # Ensure it doesn't exceed reasonable length
        if len(final_prompt) > 500:
            final_prompt = final_prompt[:497] + '...'
        
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
            headers = {
                'Accept': 'application/json',
                'X-Subscription-Token': self.brave_api_key
            }
            
            # Use web search endpoint with image focus (image search API has stricter limits)
            # Brave Image Search API may not support all parameters, so we use web search
            params = {
                'q': f"{query} logo",  # Add 'logo' to get better results
                'count': min(20, max_results * 4),  # Request more but respect API limits
                'search_lang': 'en'
            }
            
            response = requests.get(
                self.brave_search_endpoint,  # Use web search endpoint (more reliable)
                headers=headers,
                params=params,
                timeout=15  # Increased timeout for more results
            )
            
            if response.status_code == 401:
                return {
                    'success': False,
                    'error': 'Invalid Brave Search API key. Please check your BRAVE_SEARCH_API_KEY in .env'
                }
            
            if response.status_code == 422:
                # Fallback with simpler parameters
                params = {
                    'q': query,
                    'count': 10
                }
                response = requests.get(
                    self.brave_search_endpoint,
                    headers=headers,
                    params=params,
                    timeout=10
                )
            
            response.raise_for_status()
            data = response.json()
            
            # Get web results which include thumbnails
            web_results = data.get('web', {}).get('results', [])
            
            if not web_results:
                return {
                    'success': False,
                    'error': f'No images found for "{query}". Try a different search term.'
                }
            
            # Process and validate image results from web search
            image_results = []
            
            for result in web_results:
                if len(image_results) >= max_results:
                    break
                
                # Get thumbnail from web result
                thumbnail_data = result.get('thumbnail', {})
                thumbnail_url = thumbnail_data.get('src', '')
                
                # Also check for page_fetched and meta_url for additional context
                page_url = result.get('url', '')
                
                if not thumbnail_url:
                    continue
                
                # Validate URL format
                if not (thumbnail_url.startswith('http://') or thumbnail_url.startswith('https://')):
                    continue
                
                # Get source information
                hostname = result.get('meta_url', {}).get('hostname', 'web')
                title = result.get('title', 'Logo Image')
                description = result.get('description', '')
                
                # Check if from trusted sources
                is_trusted = any(trusted in hostname.lower() for trusted in [
                    'wikipedia.org', 'wikimedia.org', 'commons.wikimedia.org',
                    'official', 'logo', 'brand'
                ])
                
                image_results.append({
                    'image_url': thumbnail_url,
                    'thumbnail_url': thumbnail_url,
                    'full_image_url': page_url,  # Use page URL as fallback
                    'fallback_url': page_url,
                    'title': title,
                    'source': page_url,
                    'description': description,
                    'hostname': hostname,
                    'is_trusted': is_trusted,
                    'width': 0,  # Web search doesn't provide dimensions
                    'height': 0
                })
            
            if not image_results:
                return {
                    'success': False,
                    'error': f'No valid images found for "{query}". Try a different search term.'
                }
            
            return {
                'success': True,
                'results': image_results,
                'query': query,
                'total_results': len(image_results)
            }
            
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Search request timed out. Please try again.'
            }
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 422:
                return {
                    'success': False,
                    'error': f'Invalid search query. Please try different search terms.'
                }
            return {
                'success': False,
                'error': f'Search error: {e.response.status_code}'
            }
        except Exception as e:
            print(f"Error searching for photo: {e}")
            return {
                'success': False,
                'error': f'Search error: {str(e)}'
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
