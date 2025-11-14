"""
Migration script to move from SQLite to PostgreSQL
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

# Import models
from models import User, ChatHistory
import config

def migrate_to_postgres(postgres_url):
    """
    Migrate data from SQLite to PostgreSQL
    
    Args:
        postgres_url (str): PostgreSQL connection URL
            Example: postgresql://username:password@localhost:5432/database_name
    """
    print("🔄 Starting migration from SQLite to PostgreSQL...")
    
    # Get SQLite database path
    sqlite_db_path = os.path.join(config.BASE_DIR, 'data.db')
    sqlite_url = f"sqlite:///{sqlite_db_path}"
    
    if not os.path.exists(sqlite_db_path):
        print(f"❌ SQLite database not found at: {sqlite_db_path}")
        print("   Nothing to migrate.")
        return
    
    print(f"📂 Source: {sqlite_url}")
    print(f"📂 Target: {postgres_url}")
    
    # Create engines
    try:
        sqlite_engine = create_engine(sqlite_url)
        postgres_engine = create_engine(postgres_url)
    except Exception as e:
        print(f"❌ Error connecting to databases: {e}")
        return
    
    # Create sessions
    SqliteSession = sessionmaker(bind=sqlite_engine)
    PostgresSession = sessionmaker(bind=postgres_engine)
    
    sqlite_session = SqliteSession()
    postgres_session = PostgresSession()
    
    try:
        # Import table structure
        from models import db
        
        # Create all tables in PostgreSQL
        print("\n📋 Creating tables in PostgreSQL...")
        db.metadata.create_all(postgres_engine)
        print("✅ Tables created successfully")
        
        # Migrate Users
        print("\n👥 Migrating users...")
        sqlite_users = sqlite_session.query(User).all()
        user_count = 0
        
        for user in sqlite_users:
            # Check if user already exists
            existing = postgres_session.query(User).filter_by(firebase_uid=user.firebase_uid).first()
            if existing:
                print(f"   ⏭️  Skipping existing user: {user.email}")
                continue
            
            # Create new user
            new_user = User(
                firebase_uid=user.firebase_uid,
                email=user.email,
                fname=user.fname,
                lname=user.lname,
                is_pro=user.is_pro,
                prompt_count=user.prompt_count,
                last_prompt_reset=user.last_prompt_reset,
                created_at=user.created_at
            )
            postgres_session.add(new_user)
            user_count += 1
            print(f"   ✅ Migrated user: {user.email}")
        
        postgres_session.commit()
        print(f"✅ Migrated {user_count} users")
        
        # Migrate Chat History
        print("\n💬 Migrating chat history...")
        sqlite_history = sqlite_session.query(ChatHistory).all()
        history_count = 0
        
        for entry in sqlite_history:
            # Get corresponding user in PostgreSQL
            user = postgres_session.query(User).filter_by(
                firebase_uid=sqlite_session.query(User).filter_by(id=entry.user_id).first().firebase_uid
            ).first()
            
            if not user:
                print(f"   ⚠️  Skipping entry - user not found")
                continue
            
            # Create new history entry
            new_entry = ChatHistory(
                user_id=user.id,
                prompt=entry.prompt,
                image_path=entry.image_path,
                created_at=entry.created_at
            )
            postgres_session.add(new_entry)
            history_count += 1
        
        postgres_session.commit()
        print(f"✅ Migrated {history_count} chat history entries")
        
        print("\n🎉 Migration completed successfully!")
        print(f"\n📊 Summary:")
        print(f"   Users migrated: {user_count}")
        print(f"   History entries migrated: {history_count}")
        
        # Backup SQLite database
        backup_path = sqlite_db_path + '.backup'
        if os.path.exists(sqlite_db_path):
            import shutil
            shutil.copy2(sqlite_db_path, backup_path)
            print(f"\n💾 SQLite database backed up to: {backup_path}")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        postgres_session.rollback()
        import traceback
        traceback.print_exc()
    finally:
        sqlite_session.close()
        postgres_session.close()
        print("\n✅ Database connections closed")


def verify_migration(postgres_url):
    """
    Verify that migration was successful
    
    Args:
        postgres_url (str): PostgreSQL connection URL
    """
    print("\n🔍 Verifying migration...")
    
    try:
        engine = create_engine(postgres_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        user_count = session.query(User).count()
        history_count = session.query(ChatHistory).count()
        
        print(f"✅ PostgreSQL database contains:")
        print(f"   Users: {user_count}")
        print(f"   Chat history entries: {history_count}")
        
        session.close()
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python migrate_to_postgres.py <postgres_url>")
        print("\nExample:")
        print("  python migrate_to_postgres.py postgresql://postgres:password@localhost:5432/zypher_ai")
        print("\nOr set DATABASE_URL environment variable and run:")
        print("  python migrate_to_postgres.py")
        sys.exit(1)
    
    # Get PostgreSQL URL from argument or environment
    if len(sys.argv) >= 2 and sys.argv[1] != 'env':
        postgres_url = sys.argv[1]
    else:
        postgres_url = os.getenv('DATABASE_URL')
        if not postgres_url or 'sqlite' in postgres_url:
            print("❌ DATABASE_URL not set or still pointing to SQLite")
            print("   Please provide PostgreSQL connection URL as argument")
            sys.exit(1)
    
    # Perform migration
    migrate_to_postgres(postgres_url)
    
    # Verify migration
    verify_migration(postgres_url)
    
    print("\n📝 Next steps:")
    print("   1. Update DATABASE_URL in your .env file to use PostgreSQL")
    print("   2. Restart your application")
    print("   3. Test the application to ensure everything works")
    print("   4. Once verified, you can delete the SQLite database backup")
