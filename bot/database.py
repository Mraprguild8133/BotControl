"""
Database operations and management
"""

import sqlite3
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

class Database:
    """Database manager for bot operations"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.logger = logging.getLogger(__name__)
        self.connection = None
        self._connect()
        self._initialize_tables()
    
    def _connect(self):
        """Establish database connection"""
        try:
            if self.database_url.startswith('postgresql://') or self.database_url.startswith('postgres://'):
                # PostgreSQL connection
                self.connection = psycopg2.connect(self.database_url)
                self.connection.autocommit = True
                self.logger.info("Connected to PostgreSQL database")
            else:
                # SQLite connection
                db_path = self.database_url.replace('sqlite:///', '')
                self.connection = sqlite3.connect(db_path, check_same_thread=False)
                self.connection.row_factory = sqlite3.Row
                self.logger.info("Connected to SQLite database")
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            raise
    
    def _initialize_tables(self):
        """Create database tables if they don't exist"""
        try:
            cursor = self.connection.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT UNIQUE NOT NULL,
                    username VARCHAR(100),
                    first_name VARCHAR(100),
                    last_name VARCHAR(100),
                    is_admin BOOLEAN DEFAULT FALSE,
                    is_banned BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Channels table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS channels (
                    id SERIAL PRIMARY KEY,
                    channel_id BIGINT UNIQUE NOT NULL,
                    channel_name VARCHAR(200),
                    channel_username VARCHAR(100),
                    added_by BIGINT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    welcome_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Keywords table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS keywords (
                    id SERIAL PRIMARY KEY,
                    keyword VARCHAR(500) NOT NULL,
                    added_by BIGINT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Blocked messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS blocked_messages (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    channel_id BIGINT NOT NULL,
                    message_text TEXT,
                    reason VARCHAR(500),
                    blocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Bot stats table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bot_stats (
                    id SERIAL PRIMARY KEY,
                    stat_name VARCHAR(100) UNIQUE NOT NULL,
                    stat_value VARCHAR(500),
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Movie searches table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS movie_searches (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    search_query VARCHAR(500) NOT NULL,
                    results_count INTEGER DEFAULT 0,
                    searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.connection.commit()
            self.logger.info("Database tables initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize tables: {e}")
            raise
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None) -> bool:
        """Add or update user in database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO users (user_id, username, first_name, last_name, last_seen)
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id) DO UPDATE SET
                    username = EXCLUDED.username,
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    last_seen = CURRENT_TIMESTAMP
            """, (user_id, username, first_name, last_name))
            self.connection.commit()
            return True
        except Exception as e:
            self.logger.error(f"Failed to add user: {e}")
            return False
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT is_admin FROM users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            return result and result[0] if result else False
        except Exception as e:
            self.logger.error(f"Failed to check admin status: {e}")
            return False
    
    def add_admin(self, user_id: int) -> bool:
        """Add admin to database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE users SET is_admin = TRUE WHERE user_id = %s", (user_id,))
            self.connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"Failed to add admin: {e}")
            return False
    
    def remove_admin(self, user_id: int) -> bool:
        """Remove admin from database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE users SET is_admin = FALSE WHERE user_id = %s", (user_id,))
            self.connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"Failed to remove admin: {e}")
            return False
    
    def get_admins(self) -> List[Dict]:
        """Get list of all admins"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT user_id, username, first_name, last_name FROM users WHERE is_admin = TRUE")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Failed to get admins: {e}")
            return []
    
    def add_channel(self, channel_id: int, channel_name: str, channel_username: str, added_by: int) -> bool:
        """Add channel to database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO channels (channel_id, channel_name, channel_username, added_by)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (channel_id) DO UPDATE SET
                    channel_name = EXCLUDED.channel_name,
                    channel_username = EXCLUDED.channel_username,
                    is_active = TRUE
            """, (channel_id, channel_name, channel_username, added_by))
            self.connection.commit()
            return True
        except Exception as e:
            self.logger.error(f"Failed to add channel: {e}")
            return False
    
    def remove_channel(self, channel_id: int) -> bool:
        """Remove channel from database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE channels SET is_active = FALSE WHERE channel_id = %s", (channel_id,))
            self.connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"Failed to remove channel: {e}")
            return False
    
    def get_channels(self) -> List[Dict]:
        """Get list of active channels"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM channels WHERE is_active = TRUE")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Failed to get channels: {e}")
            return []
    
    def add_keyword(self, keyword: str, added_by: int) -> bool:
        """Add copyright keyword"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO keywords (keyword, added_by) VALUES (%s, %s)", (keyword.lower(), added_by))
            self.connection.commit()
            return True
        except Exception as e:
            self.logger.error(f"Failed to add keyword: {e}")
            return False
    
    def remove_keyword(self, keyword: str) -> bool:
        """Remove copyright keyword"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE keywords SET is_active = FALSE WHERE keyword = %s", (keyword.lower(),))
            self.connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"Failed to remove keyword: {e}")
            return False
    
    def get_keywords(self) -> List[str]:
        """Get list of active keywords"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT keyword FROM keywords WHERE is_active = TRUE")
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Failed to get keywords: {e}")
            return []
    
    def log_blocked_message(self, user_id: int, channel_id: int, message_text: str, reason: str) -> bool:
        """Log blocked message"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO blocked_messages (user_id, channel_id, message_text, reason)
                VALUES (%s, %s, %s, %s)
            """, (user_id, channel_id, message_text, reason))
            self.connection.commit()
            return True
        except Exception as e:
            self.logger.error(f"Failed to log blocked message: {e}")
            return False
    
    def log_movie_search(self, user_id: int, search_query: str, results_count: int) -> bool:
        """Log movie search"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO movie_searches (user_id, search_query, results_count)
                VALUES (%s, %s, %s)
            """, (user_id, search_query, results_count))
            self.connection.commit()
            return True
        except Exception as e:
            self.logger.error(f"Failed to log movie search: {e}")
            return False
    
    def get_total_users(self) -> int:
        """Get total user count"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            return cursor.fetchone()[0]
        except Exception as e:
            self.logger.error(f"Failed to get user count: {e}")
            return 0
    
    def get_total_channels(self) -> int:
        """Get total channel count"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM channels WHERE is_active = TRUE")
            return cursor.fetchone()[0]
        except Exception as e:
            self.logger.error(f"Failed to get channel count: {e}")
            return 0
    
    def get_total_keywords(self) -> int:
        """Get total keyword count"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM keywords WHERE is_active = TRUE")
            return cursor.fetchone()[0]
        except Exception as e:
            self.logger.error(f"Failed to get keyword count: {e}")
            return 0
    
    def get_blocked_messages_count(self) -> int:
        """Get blocked messages count"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM blocked_messages")
            return cursor.fetchone()[0]
        except Exception as e:
            self.logger.error(f"Failed to get blocked messages count: {e}")
            return 0
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.logger.info("Database connection closed")
