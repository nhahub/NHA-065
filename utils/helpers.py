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
    """
    Migrate chat_history table schema to support conversation grouping and new fields.
    This function safely adds new columns and migrates existing data.
    """
    try:
        with current_app.app_context():
            conn = db.engine.connect()
            
            # Get existing columns
            result = conn.execute(text("PRAGMA table_info('chat_history')"))
            cols = [row['name'] if isinstance(row, dict) else row[1] for row in result]
            
            print("📋 Starting chat_history schema migration...")
            print(f"   Existing columns: {cols}")
            
            # Define all columns that should exist
            columns_to_add = [
                ('conversation_id', "ALTER TABLE chat_history ADD COLUMN conversation_id TEXT"),
                ('user_message', "ALTER TABLE chat_history ADD COLUMN user_message TEXT"),
                ('ai_response', "ALTER TABLE chat_history ADD COLUMN ai_response TEXT"),
                ('image_prompt', "ALTER TABLE chat_history ADD COLUMN image_prompt TEXT"),
                ('message_type', "ALTER TABLE chat_history ADD COLUMN message_type TEXT DEFAULT 'text'"),
            ]
            
            # Add missing columns
            for col_name, sql in columns_to_add:
                if col_name not in cols:
                    try:
                        conn.execute(text(sql))
                        conn.commit()
                        print(f"   ✓ Added column: {col_name}")
                    except Exception as e:
                        print(f"   ✗ Error adding {col_name}: {e}")
                        conn.rollback()
                else:
                    print(f"   → Column already exists: {col_name}")
            
            # Refresh column list after additions
            result = conn.execute(text("PRAGMA table_info('chat_history')"))
            cols = [row['name'] if isinstance(row, dict) else row[1] for row in result]
            
            # --- Data Migration Section ---
            
            # 1. Migrate old 'prompt' column to 'user_message' if needed
            if 'prompt' in cols and 'user_message' in cols:
                try:
                    # Check if there's data to migrate
                    result = conn.execute(text("""
                        SELECT COUNT(*) as count 
                        FROM chat_history 
                        WHERE user_message IS NULL AND prompt IS NOT NULL
                    """))
                    count = result.fetchone()[0]
                    
                    if count > 0:
                        print(f"   📦 Migrating {count} records from 'prompt' to 'user_message'...")
                        conn.execute(text("""
                            UPDATE chat_history 
                            SET user_message = prompt,
                                message_type = CASE 
                                    WHEN image_path IS NOT NULL THEN 'image' 
                                    ELSE 'text' 
                                END
                            WHERE user_message IS NULL AND prompt IS NOT NULL
                        """))
                        conn.commit()
                        print(f"   ✓ Successfully migrated data from 'prompt' column")
                    else:
                        print(f"   → No data to migrate from 'prompt' column")
                except Exception as e:
                    print(f"   ✗ Data migration from 'prompt' failed: {e}")
                    conn.rollback()
            
            # 2. Generate conversation_id ONLY for OLD records that don't have one
            # New records will get conversation_id from frontend
            if 'conversation_id' in cols:
                try:
                    # Check if there are OLD records without conversation_id
                    result = conn.execute(text("""
                        SELECT COUNT(*) as count 
                        FROM chat_history 
                        WHERE conversation_id IS NULL
                    """))
                    count = result.fetchone()[0]
                    
                    if count > 0:
                        print(f"   🔄 Generating conversation IDs for {count} OLD records...")
                        print(f"   ⚠️  Note: Old records will use UUID format, new records use frontend format")
                        
                        # Strategy: Group OLD messages by user and day, assign same conversation_id
                        result = conn.execute(text("""
                            SELECT id, user_id, created_at 
                            FROM chat_history 
                            WHERE conversation_id IS NULL
                            ORDER BY user_id, created_at
                        """))
                        
                        records = result.fetchall()
                        
                        if records:
                            import uuid
                            from datetime import datetime as dt
                            
                            current_user = None
                            current_date = None
                            current_conv_id = None
                            updates = []
                            
                            for record in records:
                                record_id = record[0]
                                user_id = record[1]
                                created_at = record[2]
                                
                                # Parse datetime
                                if isinstance(created_at, str):
                                    try:
                                        created_dt = dt.fromisoformat(created_at.replace('Z', '+00:00'))
                                    except:
                                        created_dt = dt.utcnow()
                                else:
                                    created_dt = created_at
                                
                                record_date = created_dt.date()
                                
                                # Start new conversation if user changed or date changed
                                if user_id != current_user or record_date != current_date:
                                    current_user = user_id
                                    current_date = record_date
                                    # Use same format as frontend for consistency
                                    timestamp = int(created_dt.timestamp() * 1000)
                                    random_suffix = str(uuid.uuid4())[:8]
                                    current_conv_id = f"conv_{timestamp}_{random_suffix}"
                                
                                updates.append({
                                    'record_id': record_id,
                                    'conv_id': current_conv_id
                                })
                            
                            # Execute updates in batches
                            batch_size = 100
                            for i in range(0, len(updates), batch_size):
                                batch = updates[i:i + batch_size]
                                for update in batch:
                                    conn.execute(
                                        text("UPDATE chat_history SET conversation_id = :conv_id WHERE id = :record_id"),
                                        {'conv_id': update['conv_id'], 'record_id': update['record_id']}
                                    )
                                conn.commit()
                            
                            print(f"   ✓ Generated {len(set(u['conv_id'] for u in updates))} unique conversations")
                        else:
                            print(f"   → No records found to process")
                    else:
                        print(f"   → All records already have conversation_id")
                        
                except Exception as e:
                    print(f"   ✗ Conversation ID generation failed: {e}")
                    conn.rollback()
            
            # 3. Create index on conversation_id for better query performance
            try:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_chat_history_conversation_id 
                    ON chat_history(conversation_id)
                """))
                conn.commit()
                print(f"   ✓ Created index on conversation_id")
            except Exception as e:
                print(f"   ✗ Index creation failed: {e}")
                conn.rollback()
            
            # 4. Create composite index for user_id + conversation_id
            try:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_chat_history_user_conversation 
                    ON chat_history(user_id, conversation_id)
                """))
                conn.commit()
                print(f"   ✓ Created composite index on user_id + conversation_id")
            except Exception as e:
                print(f"   ✗ Composite index creation failed: {e}")
                conn.rollback()
            
            # 5. Verify final schema
            result = conn.execute(text("PRAGMA table_info('chat_history')"))
            final_cols = [row['name'] if isinstance(row, dict) else row[1] for row in result]
            
            required_columns = ['id', 'user_id', 'conversation_id', 'user_message', 'ai_response', 
                              'image_prompt', 'image_path', 'message_type', 'created_at']
            missing = [col for col in required_columns if col not in final_cols]
            
            if missing:
                print(f"   ⚠️  WARNING: Missing columns: {missing}")
            else:
                print(f"   ✅ All required columns present")
            
            # Get statistics
            try:
                result = conn.execute(text("""
                    SELECT 
                        COUNT(*) as total_messages,
                        COUNT(DISTINCT conversation_id) as total_conversations,
                        COUNT(DISTINCT user_id) as total_users
                    FROM chat_history
                """))
                stats = result.fetchone()
                print(f"\n   📊 Database Statistics:")
                print(f"      Total messages: {stats[0]}")
                print(f"      Total conversations: {stats[1]}")
                print(f"      Total users: {stats[2]}")
            except Exception as e:
                print(f"   ⚠️  Could not get statistics: {e}")
            
            conn.close()
            print("\n✅ Migration completed successfully!")
            print("   💡 New messages will use frontend-generated conversation IDs\n")
            
    except Exception as e:
        print(f"\n❌ Migration error: {e}\n")
        import traceback
        traceback.print_exc()