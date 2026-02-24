import pytest
import pytest_asyncio
import asyncpg
from src.database.repository import Database
from src.config.settings import DB_CONFIG

@pytest_asyncio.fixture
async def db():
    """Фикстура для базы данных"""
    database = Database()
    await database.init()
    yield database
    
    # Очищаем после тестов
    async with database.pool.acquire() as conn:
        await conn.execute("DELETE FROM messages")
        await conn.execute("DELETE FROM users")
    await database.close()

@pytest.mark.asyncio
async def test_ensure_user(db):
    """Тест создания пользователя"""
    user_id = 12345
    username = "test_user"
    first_name = "Test"
    last_name = "User"
    
    await db.ensure_user(user_id, username, first_name, last_name)
    
    # Проверяем, что пользователь создан
    async with db.pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE user_id = $1",
            user_id
        )
        assert user is not None
        assert user['username'] == username
        assert user['first_name'] == first_name

@pytest.mark.asyncio
async def test_save_and_get_messages(db):
    """Тест сохранения и получения сообщений"""
    user_id = 12345
    await db.ensure_user(user_id, "test", "Test", "User")
    
    # Сохраняем сообщения
    await db.save_message(user_id, "user", "Привет")
    await db.save_message(user_id, "assistant", "Здравствуйте", "test-model")
    
    # Получаем историю
    history = await db.get_history(user_id)
    
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Привет"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Здравствуйте"

@pytest.mark.asyncio
async def test_trim_history(db):
    """Тест обрезки истории"""
    user_id = 12345
    await db.ensure_user(user_id, "test", "Test", "User")
    
    # Сохраняем много сообщений
    for i in range(25):
        await db.save_message(user_id, "user", f"Message {i}")
    
    # Обрезаем до 10
    await db.trim_history(user_id, keep_last=10)
    
    # Проверяем
    history = await db.get_history(user_id)
    assert len(history) <= 10