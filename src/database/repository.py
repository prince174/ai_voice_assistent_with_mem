import asyncpg
from typing import List, Dict, Any
from .models import User, Message
from src.config.settings import POSTGRES_CONFIG
from src.config.constants import MAX_HISTORY_CHARS, HISTORY_MESSAGES_LIMIT

class Database:
    async def init(self):
        self.pool = await asyncpg.create_pool(**POSTGRES_CONFIG)
        await self._create_tables()
    
    async def _create_tables(self):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id BIGSERIAL PRIMARY KEY,
                    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    model TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
    
    async def ensure_user(self, user_id: int, username: str, first_name: str, last_name: str):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO users (user_id, username, first_name, last_name)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (user_id) DO UPDATE SET
                    username = EXCLUDED.username,
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name
            ''', user_id, username, first_name, last_name)
    
    async def save_message(self, user_id: int, role: str, content: str, model: str = None):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO messages (user_id, role, content, model)
                VALUES ($1, $2, $3, $4)
            ''', user_id, role, content, model)
    
    async def get_history(self, user_id: int) -> List[Dict[str, str]]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT role, content
                FROM messages
                WHERE user_id = $1
                    AND content IS NOT NULL
                    AND LENGTH(TRIM(content)) > 0
                ORDER BY created_at DESC
                LIMIT $2
            ''', user_id, HISTORY_MESSAGES_LIMIT)
            
            rows = list(reversed(rows))
            history = []
            total_chars = 0
            
            for r in rows:
                content = r["content"].strip()
                if not content:
                    continue
                    
                total_chars += len(content)
                if total_chars > MAX_HISTORY_CHARS:
                    break
                    
                history.append({
                    "role": r["role"],
                    "content": content
                })
            
            return history
    
    async def trim_history(self, user_id: int, keep_last: int = 20):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                DELETE FROM messages
                WHERE id IN (
                    SELECT id FROM messages
                    WHERE user_id = $1
                    ORDER BY created_at DESC
                    OFFSET $2
                )
            ''', user_id, keep_last)

    async def close(self):
        """Безопасное закрытие соединения с БД"""
        if hasattr(self, 'pool') and self.pool:
            try:
                await self.pool.close()
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.error(f"Ошибка при закрытии пула соединений: {e}")
            finally:
                self.pool = None
                
    async def delete_user_history(self, user_id: int):
        """Удалить всю историю сообщений пользователя"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                DELETE FROM messages
                WHERE user_id = $1
            ''', user_id)
    
    async def get_user_stats(self, user_id: int) -> dict:
        """Получить статистику пользователя"""
        async with self.pool.acquire() as conn:
            # Общее количество сообщений
            total = await conn.fetchval('''
                SELECT COUNT(*) FROM messages WHERE user_id = $1
            ''', user_id)
            
            # Сообщения пользователя
            user_msgs = await conn.fetchval('''
                SELECT COUNT(*) FROM messages 
                WHERE user_id = $1 AND role = 'user'
            ''', user_id)
            
            # Ответы бота
            bot_msgs = await conn.fetchval('''
                SELECT COUNT(*) FROM messages 
                WHERE user_id = $1 AND role = 'assistant'
            ''', user_id)
            
            # Первое сообщение
            first_msg = await conn.fetchval('''
                SELECT created_at FROM messages 
                WHERE user_id = $1 
                ORDER BY created_at ASC 
                LIMIT 1
            ''', user_id)
            
            # Последнее сообщение
            last_msg = await conn.fetchval('''
                SELECT created_at FROM messages 
                WHERE user_id = $1 
                ORDER BY created_at DESC 
                LIMIT 1
            ''', user_id)
            
            return {
                'total': total or 0,
                'user_msgs': user_msgs or 0,
                'bot_msgs': bot_msgs or 0,
                'first_msg': first_msg,
                'last_msg': last_msg
            }