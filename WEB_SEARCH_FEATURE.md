# Web Search Toggle Feature Documentation

## Overview

The Web Search Toggle feature allows users to enable intelligent web-based photo and logo searches within the Zypher AI Logo Generator. When enabled, the AI can automatically detect when users are requesting to find specific photos or logos from the web, fetch them using the Brave Image Search API, present them for user confirmation, and then use them as references for generation.

## Features

### 1. **Toggle Control**
- Located in the Settings modal under "Generation Settings"
- Simple checkbox to enable/disable web search functionality
- State persists during the session and is sent with each request

### 2. **Intelligent Detection**
The system automatically detects photo search requests using pattern matching:
- Keywords: "search", "find", "look for", "get", "fetch", "show"
- Targets: "photo", "image", "picture", "logo"
- Context: "of", "for"
- Examples:
  - ✅ "Search for a photo of a Tesla logo"
  - ✅ "Find an image of Nike swoosh"
  - ✅ "Get a picture of Apple logo"
  - ✅ "Show me a photo of Coca-Cola branding"

### 3. **Search & Preview Workflow**

#### Step 1: User Makes Request
```
User: "Search for a photo of the Nike logo"
```

#### Step 2: AI Searches Web
- Uses Brave Image Search API
- Fetches top results based on query
- Returns best match with metadata

#### Step 3: Preview Display
The system displays:
- **Image Preview**: Actual photo from the web
- **Title**: Name of the image
- **Source**: Original URL
- **Description**: Context about the image
- **Search Query**: What was searched
- **Action Buttons**:
  - ✅ "This is correct - Use it" (Confirm)
  - ❌ "Search again" (Refine)

#### Step 4: User Confirmation
**If user confirms ("yes", "correct", "use it"):**
```
AI: "Great! I'll use this photo as a reference. You can now ask me to generate a logo based on it! 🎨"
```
The photo is confirmed and can be used as inspiration.

**If user rejects ("no", "search again", "different"):**
The system performs a new search with refined parameters.

## Technical Implementation

### Frontend Components

#### 1. Settings UI (`templates/index.html`)
```html
<div class="setting-group">
    <label class="setting-label checkbox-label">
        <input type="checkbox" id="useWebSearchToggle" class="settings-checkbox"
            onchange="toggleWebSearch()">
        <span class="checkmark"></span>
        Enable Web Search for Photos/Logos
    </label>
    <p class="setting-description">Allow AI to search the web for reference photos/logos when you ask for specific images</p>
</div>
```

#### 2. JavaScript State Management (`static/js/app.js`)
```javascript
let currentSettings = {
    // ... other settings
    use_web_search: false
};

function toggleWebSearch() {
    const webSearchToggle = document.getElementById('useWebSearchToggle');
    currentSettings.use_web_search = webSearchToggle ? webSearchToggle.checked : false;
}
```

#### 3. Photo Preview Display (`static/js/app.js`)
```javascript
function addPhotoPreviewMessage(text, photoResult) {
    // Creates interactive preview card with:
    // - Image display
    // - Metadata (title, source, description)
    // - Confirmation buttons
}
```

#### 4. Styling (`static/css/style.css`)
```css
.photo-preview-card {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 20px;
    /* ... */
}
```

### Backend Components

#### 1. Logo Agent (`utils/logo_agent.py`)

**New Method: `search_for_photo()`**
```python
def search_for_photo(self, query: str, max_results: int = 5) -> Dict:
    """
    Search for a specific photo/logo using Brave Image Search API.
    
    Returns:
        Dict: {
            'success': bool,
            'image_url': str,
            'title': str,
            'source': str,
            'description': str,
            'query': str,
            'total_results': int
        }
    """
```

**New Method: `format_photo_preview()`**
```python
def format_photo_preview(self, photo_result: Dict) -> str:
    """Format the photo search result for user preview."""
```

#### 2. Mistral Chat Manager (`utils/mistral_chat.py`)

**New Property:**
```python
self.pending_photo_requests = {}  # user_id -> photo_request_data
```

**New Method: `is_photo_search_request()`**
```python
def is_photo_search_request(self, text: str) -> bool:
    """Detect if the user message is requesting to search for a specific photo/logo"""
```

**New Method: `extract_photo_search_query()`**
```python
def extract_photo_search_query(self, text: str) -> Optional[str]:
    """Extract the subject/query for photo search from user message"""
```

**Updated Method: `chat()`**
```python
def chat(self, user_message: str, ..., use_web_search: bool = False):
    # Now accepts use_web_search parameter
    # Handles photo search detection and confirmation flow
```

#### 3. Flask API (`app_flask.py`)

**Updated Endpoint: `/api/chat`**
```python
@app.route('/api/chat', methods=['POST'])
@verify_firebase_token
def chat_with_ai():
    data = request.json
    use_web_search = data.get('use_web_search', False)
    
    response_text, is_image_request, image_prompt, extra_data = mistral_chat.chat(
        user_message, 
        conversation_history,
        user_id=uid,
        use_web_search=use_web_search  # Pass the toggle state
    )
    
    # Handle photo preview response
    if extra_data and extra_data.get('type') == 'photo_preview':
        return jsonify({
            'awaiting_photo_confirmation': True,
            'photo_result': photo_data
        })
```

## API Integration

### Brave Image Search API

**Endpoint:** `https://api.search.brave.com/res/v1/images/search`

**Required Environment Variable:**
```bash
BRAVE_SEARCH_API_KEY=your_brave_api_key_here
```

**Request Parameters:**
- `q`: Search query
- `count`: Number of results (default: 5)
- `search_lang`: Language (default: 'en')
- `safesearch`: Safe search mode (default: 'moderate')

**Response Format:**
```json
{
  "results": [
    {
      "title": "Image title",
      "url": "https://source.com/page",
      "thumbnail": {
        "src": "https://image-url.com/image.jpg"
      },
      "description": "Image description"
    }
  ]
}
```

## User Experience Flow

### Example 1: Basic Photo Search

```
👤 User: "Search for a photo of the McDonald's logo"

🤖 AI: [Searches web using Brave API]

🎨 Preview Card:
┌─────────────────────────────────────┐
│ 🔍 Photo Found from Web Search      │
├─────────────────────────────────────┤
│ [IMAGE OF MCDONALD'S LOGO]          │
├─────────────────────────────────────┤
│ Title: McDonald's Golden Arches     │
│ Source: mcdonalds.com               │
│ Description: Official McDonald's    │
│              brand logo              │
├─────────────────────────────────────┤
│ [✅ This is correct]  [❌ Search again] │
└─────────────────────────────────────┘

👤 User: "Yes, this is correct"

🤖 AI: "Great! I'll use this photo as a reference. 
       You can now ask me to generate a logo based on it! 🎨"
```

### Example 2: Refinement Flow

```
👤 User: "Find a picture of Starbucks logo"

🤖 AI: [Shows preview with an incorrect image]

👤 User: "No, search for a different photo"

🤖 AI: [Searches again with refined query]
      [Shows new preview]

👤 User: "Perfect, use this one"

🤖 AI: "Great! Ready to use as reference..."
```

## Error Handling

### 1. API Key Not Configured
```
⚠️ Brave Search API key not configured. 
Please add BRAVE_SEARCH_API_KEY to .env
```

### 2. No Results Found
```
❌ No images found for "your query". 
Try a different search term.
```

### 3. Network Timeout
```
⚠️ Search request timed out. Please try again.
```

### 4. Invalid API Key
```
❌ Invalid Brave Search API key. 
Please check your BRAVE_SEARCH_API_KEY in .env
```

## Configuration

### Environment Variables
```bash
# Required for web search functionality
BRAVE_SEARCH_API_KEY=your_api_key_here

# Other required variables
MISTRAL_API_KEY=your_mistral_key_here
```

### Default Settings
```javascript
// In app.js
currentSettings = {
    use_web_search: false  // Disabled by default
}
```

## Security Considerations

1. **API Key Protection**: Brave API key is stored server-side only
2. **User Authentication**: All search requests require Firebase authentication
3. **Rate Limiting**: Consider implementing rate limits for search requests
4. **Content Safety**: Brave API includes 'safesearch' parameter set to 'moderate'
5. **CORS**: Configured to prevent unauthorized access

## Future Enhancements

### Potential Improvements:
1. **Multiple Result Selection**: Show top 3-5 results, let user choose
2. **Image Caching**: Cache fetched images to reduce API calls
3. **Advanced Filters**: Size, color, style filters for search
4. **Direct URL Input**: Allow users to paste image URLs directly
5. **Image Analysis**: Analyze fetched image for design elements
6. **Search History**: Track and suggest previous successful searches
7. **Batch Search**: Search for multiple images at once
8. **Regional Search**: Specify region/country for search results

## Testing

### Manual Test Cases:

1. **Basic Search Test**
   - Enable web search toggle
   - Ask: "Search for a photo of Apple logo"
   - Verify: Preview displays with image
   - Confirm: Click "This is correct"
   - Verify: Success message appears

2. **Refinement Test**
   - Search for a photo
   - Click "Search again"
   - Verify: New search performed
   - Check: Different result shown

3. **Toggle Disabled Test**
   - Disable web search toggle
   - Ask: "Search for a photo of Nike logo"
   - Verify: No web search performed
   - Expected: Normal chat response

4. **Error Handling Test**
   - Search for nonsense query "asdfghjkl123"
   - Verify: "No results found" message
   - Check: Graceful error handling

5. **API Key Test**
   - Remove/invalid BRAVE_SEARCH_API_KEY
   - Attempt search
   - Verify: Clear error message about configuration

## Troubleshooting

### Issue: Toggle not working
**Solution:** Check browser console for JavaScript errors, refresh page

### Issue: No search results
**Solution:** 
- Verify BRAVE_SEARCH_API_KEY is set correctly
- Check API key has remaining quota
- Try a different search query

### Issue: Image not displaying
**Solution:**
- Check image URL is valid
- Verify CORS settings
- Check browser console for network errors

### Issue: Confirmation not working
**Solution:**
- Clear browser cache
- Check network tab for API responses
- Verify user is authenticated

## Conclusion

The Web Search Toggle feature provides an intelligent, user-friendly way to fetch and confirm photos/logos from the web before using them as references for AI-generated logos. The feature is:

- ✅ **Easy to use**: Simple toggle in settings
- ✅ **Intelligent**: Automatic detection of search requests
- ✅ **Interactive**: Confirmation flow ensures accuracy
- ✅ **Secure**: Server-side API key management
- ✅ **Extensible**: Built with future enhancements in mind

For support or questions, refer to the main README.md or contact the development team.
