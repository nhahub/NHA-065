# utils/helpers.py
from datetime import datetime
from flask import current_app
from models.db import db
from models.user import User
from models.chat_history import ChatHistory
from sqlalchemy import text

def check_and_reset_daily_limit(user):
    """
    Check if user's daily limit should reset.
    Returns True if reset occurred, False otherwise.
    """
    print(f"\nRESET CHECK for {user.email}")
    print(f"   Current prompt_count: {user.prompt_count}")
    print(f"   Last reset: {user.last_prompt_reset}")
    
    now = datetime.utcnow()  # Use datetime object, not string!
    
    # If never reset, or last reset was yesterday or earlier
    if user.last_prompt_reset is None or user.last_prompt_reset.date() < now.date():
        print(f"   → RESETTING prompt count (was {user.prompt_count})")
        user.prompt_count = 0
        user.last_prompt_reset = now  # This is now a datetime object
        db.session.commit()
        return True
    
    print(f"   → No reset needed")
    return False

def migrate_chat_history_schema():
    try:
        with current_app.app_context():
            conn = db.engine.connect()
            result = conn.execute(text("PRAGMA table_info('chat_history')"))
            cols = [row['name'] if isinstance(row, dict) else row[1] for row in result]

            for col, sql in [
                ('user_message', "ALTER TABLE chat_history ADD COLUMN user_message TEXT"),
                ('ai_response', "ALTER TABLE chat_history ADD COLUMN ai_response TEXT"),
                ('image_prompt', "ALTER TABLE chat_history ADD COLUMN image_prompt TEXT"),
                ('message_type', "ALTER TABLE chat_history ADD COLUMN message_type TEXT DEFAULT 'text'"),
            ]:
                if col not in cols:
                    try:
                        conn.execute(text(sql))
                        print(f"Added {col} column")
                    except Exception as e:
                        print(f"{col} error: {e}")

            # --- MODIFICATION START ---
            # Only attempt to migrate data if the old 'prompt' column exists
            if 'prompt' in cols and 'user_message' in cols:
                try:
                    conn.execute(text("""
                        UPDATE chat_history 
                        SET user_message = prompt,
                            message_type = CASE WHEN image_path IS NOT NULL THEN 'image' ELSE 'text' END
                        WHERE user_message IS NULL AND prompt IS NOT NULL
                    """))
                    print("Successfully migrated data from 'prompt' column.")
                except Exception as e:
                    print(f"Data migration from 'prompt' column failed: {e}")
            # --- MODIFICATION END ---
            
            conn.close()
            print("Migration check complete!") # Changed log message for clarity
    except Exception as e:
        print(f"Migration error: {e}")