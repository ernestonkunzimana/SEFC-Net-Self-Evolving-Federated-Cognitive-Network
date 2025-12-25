"""
Database Module for SEFCNet Authentication
==========================================
Provides SQLite database for persistent user and token storage
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import aiosqlite

logger = logging.getLogger(__name__)

# Database file path
DB_DIR = Path(__file__).parent.parent.parent / "data"
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "sefcnet.db"


class Database:
    """Database manager for authentication data"""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._connection: Optional[aiosqlite.Connection] = None
    
    async def connect(self):
        """Create database connection"""
        if self._connection is None:
            self._connection = await aiosqlite.connect(str(self.db_path))
            self._connection.row_factory = aiosqlite.Row
            await self._connection.execute("PRAGMA foreign_keys = ON")
            await self._connection.commit()
            logger.info(f"Connected to database: {self.db_path}")
    
    async def close(self):
        """Close database connection"""
        if self._connection:
            await self._connection.close()
            self._connection = None
            logger.info("Database connection closed")
    
    async def init_schema(self):
        """Initialize database schema"""
        await self.connect()
        
        # Users table
        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                roles TEXT NOT NULL,
                permissions TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # API keys table
        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                api_key TEXT UNIQUE NOT NULL,
                key_name TEXT DEFAULT 'default',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Token blacklist table
        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS token_blacklist (
                token TEXT PRIMARY KEY,
                user_id TEXT,
                blacklisted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Password reset tokens table
        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS reset_tokens (
                token TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        await self._connection.commit()
        logger.info("Database schema initialized")
    
    async def create_user(self, user_data: Dict) -> Dict:
        """Create a new user"""
        await self.connect()
        await self._connection.execute("""
            INSERT INTO users (id, email, hashed_password, roles, permissions, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_data['id'],
            user_data['email'],
            user_data['hashed_password'],
            ','.join(user_data.get('roles', [])),
            ','.join(user_data.get('permissions', [])),
            1 if user_data.get('is_active', True) else 0
        ))
        await self._connection.commit()
        return await self.get_user_by_id(user_data['id'])
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        await self.connect()
        async with self._connection.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return self._row_to_dict(row)
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        await self.connect()
        async with self._connection.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return self._row_to_dict(row)
            return None
    
    async def update_user(self, user_id: str, updates: Dict):
        """Update user data"""
        await self.connect()
        set_clauses = []
        values = []
        
        for key, value in updates.items():
            if key == 'roles' or key == 'permissions':
                value = ','.join(value) if isinstance(value, list) else value
            set_clauses.append(f"{key} = ?")
            values.append(value)
        
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        values.append(user_id)
        
        await self._connection.execute(
            f"UPDATE users SET {', '.join(set_clauses)} WHERE id = ?",
            values
        )
        await self._connection.commit()
    
    async def add_api_key(self, user_id: str, api_key: str, key_name: str = "default"):
        """Add API key for user"""
        await self.connect()
        import uuid
        await self._connection.execute("""
            INSERT INTO api_keys (id, user_id, api_key, key_name)
            VALUES (?, ?, ?, ?)
        """, (str(uuid.uuid4()), user_id, api_key, key_name))
        await self._connection.commit()
    
    async def get_api_keys(self, user_id: str) -> List[str]:
        """Get all API keys for user"""
        await self.connect()
        async with self._connection.execute(
            "SELECT api_key FROM api_keys WHERE user_id = ?", (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [row['api_key'] for row in rows]
    
    async def revoke_api_key(self, user_id: str, api_key: str):
        """Revoke an API key"""
        await self.connect()
        await self._connection.execute(
            "DELETE FROM api_keys WHERE user_id = ? AND api_key = ?",
            (user_id, api_key)
        )
        await self._connection.commit()
    
    async def blacklist_token(self, token: str, user_id: Optional[str] = None):
        """Add token to blacklist"""
        await self.connect()
        await self._connection.execute("""
            INSERT OR REPLACE INTO token_blacklist (token, user_id)
            VALUES (?, ?)
        """, (token, user_id))
        await self._connection.commit()
    
    async def is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        await self.connect()
        async with self._connection.execute(
            "SELECT 1 FROM token_blacklist WHERE token = ?", (token,)
        ) as cursor:
            row = await cursor.fetchone()
            return row is not None
    
    async def create_reset_token(self, user_id: str, token: str, expires_at: datetime):
        """Create password reset token"""
        await self.connect()
        await self._connection.execute("""
            INSERT OR REPLACE INTO reset_tokens (token, user_id, expires_at)
            VALUES (?, ?, ?)
        """, (token, user_id, expires_at))
        await self._connection.commit()
    
    async def get_reset_token(self, token: str) -> Optional[Tuple[str, datetime]]:
        """Get reset token data"""
        await self.connect()
        async with self._connection.execute(
            "SELECT user_id, expires_at FROM reset_tokens WHERE token = ?", (token,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                expires_at = datetime.fromisoformat(row['expires_at']) if isinstance(row['expires_at'], str) else row['expires_at']
                return (row['user_id'], expires_at)
            return None
    
    async def delete_reset_token(self, token: str):
        """Delete reset token"""
        await self.connect()
        await self._connection.execute(
            "DELETE FROM reset_tokens WHERE token = ?", (token,)
        )
        await self._connection.commit()
    
    def _row_to_dict(self, row) -> Dict:
        """Convert database row to dictionary"""
        if row is None:
            return None
        
        data = dict(row)
        # Parse roles and permissions
        if 'roles' in data and data['roles']:
            data['roles'] = data['roles'].split(',') if isinstance(data['roles'], str) else data['roles']
        else:
            data['roles'] = []
        
        if 'permissions' in data and data['permissions']:
            data['permissions'] = data['permissions'].split(',') if isinstance(data['permissions'], str) else data['permissions']
        else:
            data['permissions'] = []
        
        data['is_active'] = bool(data.get('is_active', 1))
        return data


# Global database instance
_db: Optional[Database] = None


async def get_db() -> Database:
    """Get database instance"""
    global _db
    if _db is None:
        _db = Database()
        await _db.init_schema()
    return _db


async def init_db():
    """Initialize database"""
    db = await get_db()
    await db.init_schema()


async def close_db():
    """Close database connection"""
    global _db
    if _db:
        await _db.close()
        _db = None

