"""
Script to add footer_copyright column to site_settings table
Run this script directly: python add_footer_copyright_column.py
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import text
from database import engine

def add_footer_copyright_column():
    """Add footer_copyright column to site_settings table"""
    try:
        with engine.connect() as conn:
            # Check if column already exists
            if engine.url.drivername == 'sqlite':
                # SQLite check
                result = conn.execute(text("""
                    SELECT COUNT(*) as cnt 
                    FROM pragma_table_info('site_settings') 
                    WHERE name='footer_copyright'
                """))
            elif 'mysql' in engine.url.drivername or 'pymysql' in str(engine.url):
                # MySQL check
                result = conn.execute(text("""
                    SELECT COUNT(*) as cnt 
                    FROM information_schema.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = 'site_settings' 
                    AND COLUMN_NAME = 'footer_copyright'
                """))
            else:
                # PostgreSQL check
                result = conn.execute(text("""
                    SELECT COUNT(*) as cnt 
                    FROM information_schema.columns 
                    WHERE table_name = 'site_settings' 
                    AND column_name = 'footer_copyright'
                """))
            
            count = result.fetchone()[0]
            
            if count > 0:
                print("Column 'footer_copyright' already exists in site_settings table.")
                return
            
            # Add the column
            if engine.url.drivername == 'sqlite':
                # SQLite
                conn.execute(text("""
                    ALTER TABLE site_settings 
                    ADD COLUMN footer_copyright TEXT DEFAULT 'Powered By IT Centre Glorious Church Copyright @ 2023'
                """))
                conn.commit()
            elif 'mysql' in engine.url.drivername or 'pymysql' in str(engine.url):
                # MySQL
                conn.execute(text("""
                    ALTER TABLE site_settings 
                    ADD COLUMN footer_copyright TEXT DEFAULT 'Powered By IT Centre Glorious Church Copyright @ 2023'
                """))
                conn.commit()
            else:
                # PostgreSQL
                conn.execute(text("""
                    ALTER TABLE site_settings 
                    ADD COLUMN footer_copyright TEXT DEFAULT 'Powered By IT Centre Glorious Church Copyright @ 2023'
                """))
                conn.commit()
            print("Successfully added 'footer_copyright' column to site_settings table.")
            
    except Exception as e:
        print(f"Error adding column: {e}")
        sys.exit(1)

if __name__ == "__main__":
    add_footer_copyright_column()
