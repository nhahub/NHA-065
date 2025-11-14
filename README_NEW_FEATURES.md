# Logo Reference Agent & PostgreSQL Migration Guide

## Overview

This document describes the new features added to Zypher AI:

1. **Logo Reference Agent** - Intelligent logo design assistant using Brave Search API
2. **PostgreSQL Migration** - Scalable database with migration script
3. **Admin Dashboard** - View and manage user chat histories

---

## 1. Logo Reference Agent

### Features

The Logo Reference Agent enhances logo generation by:
- **Web Search Integration**: Uses Brave Search API to find real-world design references
- **Industry Analysis**: Extracts visual patterns from successful logos in the target industry
- **Smart Feature Extraction**: Identifies shapes, colors, typography, and composition trends
- **Preview & Confirmation**: Shows users the analysis before generation
- **Iterative Refinement**: Allows users to request new searches if not satisfied

### Setup

1. **Get Brave Search API Key**
   - Visit: https://brave.com/search/api/
   - Sign up and get your API key
   - Add to `.env` file:
     ```
     BRAVE_SEARCH_API_KEY=your_brave_api_key_here
     ```

2. **How It Works**

   When a user requests a logo (e.g., "Create a logo for my juice company"), the system:
   
   1. **Parses the request** - Extracts brand name, industry, style preferences
   2. **Searches the web** - Finds design references and trends using Brave API
   3. **Extracts features** - Analyzes industry patterns (colors, shapes, icons)
   4. **Generates prompt** - Creates optimized diffusion model prompt
   5. **Shows preview** - Displays extracted features to user
   6. **Awaits confirmation** - User can confirm or request refinement
   7. **Generates image** - Creates logo with enhanced prompt

### User Flow

```
User: "Create a logo for my tech startup"
    ↓
Agent searches web for "tech logo design trends 2025"
    ↓
Preview shown:
  🎨 Design Analysis Complete
  
  Shapes: geometric, abstract, angular
  Colors: blue, cyan, purple
  Style: minimal, modern, flat design
  Typography: sans-serif, geometric
  
  Generated Prompt: "Logo for tech startup featuring 
  digital elements, network nodes with geometric shapes..."
  
  [✅ Confirm & Generate] [🔄 Refine Search]
    ↓
User clicks Confirm
    ↓
Logo generated with optimized prompt
```

### API Structure

**New endpoint behavior in `/api/chat`:**

Response with logo preview:
```json
{
  "success": true,
  "response": "Preview message...",
  "awaiting_confirmation": true,
  "logo_preview": {
    "extracted_features": {
      "shapes": ["geometric", "angular"],
      "colors": ["blue", "cyan"],
      "icons": ["digital elements"],
      "typography": ["sans-serif"],
      "composition": ["minimal", "flat"]
    },
    "final_prompt": "Complete optimized prompt...",
    "confidence": "high",
    "search_results": [...]
  }
}
```

---

## 2. PostgreSQL Migration

### Why PostgreSQL?

- **Scalability**: Handle millions of users and chat histories
- **Performance**: Better query optimization for complex searches
- **Reliability**: ACID compliance and better data integrity
- **Features**: Advanced indexing, full-text search, JSON support

### Setup PostgreSQL

**Option A: Local PostgreSQL**
```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database
sudo -u postgres psql
CREATE DATABASE zypher_ai;
CREATE USER zypher_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE zypher_ai TO zypher_user;
\q
```

**Option B: Cloud PostgreSQL** (Recommended for production)
- **Heroku Postgres**: https://www.heroku.com/postgres
- **AWS RDS**: https://aws.amazon.com/rds/postgresql/
- **Google Cloud SQL**: https://cloud.google.com/sql/postgresql
- **DigitalOcean Managed Databases**: https://www.digitalocean.com/products/managed-databases

### Migration Steps

1. **Backup your SQLite database** (optional but recommended)
   ```bash
   cp data.db data.db.backup
   ```

2. **Update .env file**
   ```
   # PostgreSQL connection URL
   DATABASE_URL=postgresql://username:password@localhost:5432/zypher_ai
   
   # Or for cloud providers (example):
   # DATABASE_URL=postgresql://user:pass@host.aws.com:5432/dbname
   ```

3. **Install PostgreSQL driver**
   ```bash
   pip install psycopg2-binary
   ```

4. **Run migration script**
   ```bash
   # Option 1: Use DATABASE_URL from .env
   python migrate_to_postgres.py
   
   # Option 2: Provide URL as argument
   python migrate_to_postgres.py postgresql://user:pass@localhost:5432/zypher_ai
   ```

5. **Verify migration**
   - Script will show summary of migrated data
   - SQLite backup created automatically at `data.db.backup`

6. **Test the application**
   ```bash
   python app_flask.py
   ```

### Migration Script Features

- ✅ Migrates all users with their profiles
- ✅ Migrates complete chat history
- ✅ Preserves timestamps and relationships
- ✅ Creates backup of SQLite database
- ✅ Verifies migration success
- ✅ Handles existing data (skip duplicates)

### Troubleshooting

**Connection errors:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -h localhost -U username -d zypher_ai
```

**Permission errors:**
```sql
-- Grant all permissions
GRANT ALL PRIVILEGES ON DATABASE zypher_ai TO username;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO username;
```

---

## 3. Admin Dashboard

### Features

- **User Management**: View all users with their statistics
- **Chat Histories**: Access any user's generation history
- **Analytics**: Total users, pro users, generation counts
- **Filtering**: Search by email, filter by plan type
- **Sorting**: By name, date, or generation count

### Access

Navigate to: `http://localhost:7860/admin`

**Note**: Currently accessible to all authenticated users. In production, implement proper admin role checking.

### Adding Admin Role (TODO)

Update `models.py`:
```python
class User(db.Model):
    # ... existing fields ...
    is_admin = db.Column(db.Boolean, default=False)
```

Update admin routes in `app_flask.py`:
```python
@app.route('/api/admin/users', methods=['GET'])
@verify_firebase_token
def admin_get_users():
    firebase_user = getattr(request, 'firebase_user', None)
    uid = firebase_user.get('uid')
    user = models.User.query.filter_by(firebase_uid=uid).first()
    
    # Check admin role
    if not user or not user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # ... rest of the code
```

### Dashboard Sections

1. **Statistics Cards**
   - Total users
   - Pro users
   - Total generations
   - Today's generations

2. **Filters**
   - Search by email
   - Filter by plan (All/Pro/Free)
   - Sort by (Recent/Name/Generations)

3. **Users Table**
   - User email and name
   - Plan badge (Pro/Free)
   - Generation count
   - Join date
   - View history button

4. **History Modal**
   - Shows all generations for selected user
   - Displays prompt and generated image
   - Timestamps for each generation

---

## Environment Variables

Update your `.env` file with all required variables:

```env
# Mistral AI
MISTRAL_API_KEY=your_mistral_api_key_here
MISTRAL_MODEL=mistral-large-latest

# Brave Search
BRAVE_SEARCH_API_KEY=your_brave_api_key_here

# Database (choose one)
# SQLite (default):
DATABASE_URL=sqlite:///data.db
# PostgreSQL:
DATABASE_URL=postgresql://username:password@localhost:5432/zypher_ai

# Firebase
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=123456789
FIREBASE_APP_ID=1:123456789:web:abc123

# Hugging Face
HUGGINGFACE_TOKEN=your_huggingface_token_here
```

---

## Testing the New Features

### Test Logo Reference Agent

1. Start the application:
   ```bash
   python app_flask.py
   ```

2. Login to the app

3. Try these test prompts:
   - "Create a logo for my juice company"
   - "Design a tech startup logo with blue colors"
   - "Make a fitness gym logo"

4. Verify preview appears with:
   - Extracted visual features
   - Generated prompt
   - Confirm/Refine buttons

5. Test confirmation:
   - Click "Confirm & Generate"
   - Verify logo generates

6. Test refinement:
   - Click "Refine Search"
   - Verify new search happens

### Test PostgreSQL Migration

1. Ensure SQLite database exists with data

2. Run migration:
   ```bash
   python migrate_to_postgres.py postgresql://user:pass@localhost/zypher_ai
   ```

3. Verify output shows:
   - Users migrated
   - History entries migrated
   - Backup created

4. Test application:
   - Login works
   - History displays
   - New generations save

### Test Admin Dashboard

1. Navigate to `/admin`

2. Verify statistics load

3. Test filters:
   - Search by email
   - Filter by plan
   - Sort options

4. Click "View History" on a user

5. Verify history modal shows:
   - All user's generations
   - Prompts and images
   - Correct timestamps

---

## Production Deployment Checklist

- [ ] Set up production PostgreSQL database
- [ ] Update DATABASE_URL with production connection string
- [ ] Run migration script on production data
- [ ] Test database connection
- [ ] Get Brave Search API key and add to environment
- [ ] Implement admin role checking in admin routes
- [ ] Set up database backups
- [ ] Configure PostgreSQL connection pooling
- [ ] Add database indexes for performance:
  ```sql
  CREATE INDEX idx_users_firebase_uid ON users(firebase_uid);
  CREATE INDEX idx_chat_history_user_id ON chat_history(user_id);
  CREATE INDEX idx_chat_history_created_at ON chat_history(created_at);
  ```
- [ ] Enable PostgreSQL logging for monitoring
- [ ] Set up rate limiting for Brave Search API
- [ ] Test error handling for API failures
- [ ] Monitor API usage and costs

---

## Cost Considerations

### Brave Search API
- Free tier: 2,000 queries/month
- Paid plans start at $5/month for 20,000 queries
- Monitor usage in dashboard: https://brave.com/search/api/

### PostgreSQL
- **Local**: Free (self-hosted)
- **Heroku**: Free tier available, paid from $9/month
- **AWS RDS**: From $15/month for small instances
- **DigitalOcean**: From $15/month for managed database

---

## Support & Troubleshooting

### Common Issues

**1. Brave API not working**
- Check API key is correct in .env
- Verify API quota not exceeded
- Test with curl:
  ```bash
  curl -H "X-Subscription-Token: YOUR_KEY" \
       "https://api.search.brave.com/res/v1/web/search?q=test"
  ```

**2. PostgreSQL connection fails**
- Verify PostgreSQL is running
- Check connection string format
- Test with psql command line
- Check firewall settings

**3. Migration fails**
- Ensure PostgreSQL user has CREATE privileges
- Check SQLite database is not corrupted
- Review migration script output for specific errors

**4. Admin dashboard not loading**
- Check authentication token is valid
- Verify API endpoints return data
- Check browser console for errors

---

## Next Steps

1. **Enhanced Search**: Add image search alongside web search
2. **Style Transfer**: Use reference images with IP-Adapter
3. **Logo Variations**: Generate multiple versions automatically
4. **Brand Guidelines**: Extract and save brand style rules
5. **Vector Export**: Add SVG output option
6. **A/B Testing**: Show multiple designs for comparison
7. **Admin Roles**: Implement proper role-based access control
8. **Analytics Dashboard**: Add charts and graphs for insights
9. **API Rate Limiting**: Implement request throttling
10. **Caching**: Cache search results to reduce API calls

---

## Architecture Diagram

```
User Request
    ↓
Flask App (/api/chat)
    ↓
Mistral Chat Manager
    ↓
[Logo Request?] ──No──→ Normal Chat Response
    ↓ Yes
Logo Reference Agent
    ↓
Brave Search API
    ↓
Feature Extraction
    ↓
Preview Generation
    ↓
User Confirmation
    ↓
[Confirm?] ──No──→ Refine Search (loop back)
    ↓ Yes
Model Manager
    ↓
Flux Model + LoRA
    ↓
Generated Logo
    ↓
Save to PostgreSQL
    ↓
Return to User
```

---

## File Structure

```
/workspaces/NHA-065/
├── app_flask.py                 # Flask app (updated with admin routes)
├── config.py                    # Config (added BRAVE_SEARCH_API_KEY)
├── models.py                    # Database models (PostgreSQL compatible)
├── migrate_to_postgres.py       # Migration script (NEW)
├── requirements.txt             # Dependencies (updated)
├── utils/
│   ├── logo_agent.py           # Logo Reference Agent (NEW)
│   ├── mistral_chat.py         # Chat manager (updated)
│   ├── model_manager.py        # Image generation
│   ├── firebase_auth.py        # Authentication
│   └── chat_history.py         # History manager
├── templates/
│   ├── index.html              # Main chat interface
│   ├── admin.html              # Admin dashboard (NEW)
│   ├── login.html
│   ├── signup.html
│   └── upgrade.html
├── static/
│   ├── css/
│   │   └── style.css           # Styles (updated with logo preview)
│   └── js/
│       └── app.js              # Frontend logic (updated)
└── README_NEW_FEATURES.md      # This file
```

---

## Credits

- **Brave Search API**: https://brave.com/search/api/
- **PostgreSQL**: https://www.postgresql.org/
- **Flask**: https://flask.palletsprojects.com/
- **Mistral AI**: https://mistral.ai/

---

## License

Same license as the main project.
