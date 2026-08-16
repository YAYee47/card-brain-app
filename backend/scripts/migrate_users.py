import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'card_brain.db')

def migrate():
    print(f"Migrating database at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 1. Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_uuid VARCHAR(255) UNIQUE,
                nickname VARCHAR(100) NOT NULL,
                is_guest BOOLEAN NOT NULL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("Created 'users' table.")

        # 2. Insert default user 'YAYee'
        cursor.execute("SELECT id FROM users WHERE nickname = 'YAYee'")
        user = cursor.fetchone()
        if not user:
            cursor.execute("INSERT INTO users (device_uuid, nickname, is_guest) VALUES ('PENDING-YAYee', 'YAYee', 0)")
            user_id = cursor.lastrowid
            print(f"Inserted default user 'YAYee' with ID={user_id}.")
        else:
            user_id = user[0]
            print(f"User 'YAYee' already exists with ID={user_id}.")

        # 3. Add user_id to tables and update
        tables_to_migrate = ['user_cards', 'transactions', 'monthly_usage', 'app_alerts']
        for table in tables_to_migrate:
            # Check if column exists
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            if 'user_id' not in columns:
                print(f"Adding 'user_id' column to '{table}'...")
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN user_id INTEGER")
                cursor.execute(f"UPDATE {table} SET user_id = ?", (user_id,))
                print(f"Successfully migrated '{table}' to user_id={user_id}.")
            else:
                print(f"Column 'user_id' already exists in '{table}'.")

        conn.commit()
        print("Migration completed successfully!")
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
