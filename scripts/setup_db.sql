-- Скрипт для инициализации базы данных
-- Запуск: psql -U ai_bot_user -d ai_bot_db -f scripts/setup_db.sql

-- Создание пользователя (если не существует)
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE rolname = 'ai_bot_user') THEN
      CREATE USER ai_bot_user WITH PASSWORD 'your_password_here';
   END IF;
END
$do$;

-- Создание базы данных (если не существует)
CREATE DATABASE ai_bot_db OWNER ai_bot_user;

-- Подключаемся к базе
\c ai_bot_db

-- Создание таблицы пользователей
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы сообщений
CREATE TABLE IF NOT EXISTS messages (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    model TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов для ускорения запросов
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);

-- Назначение прав
GRANT ALL PRIVILEGES ON DATABASE ai_bot_db TO ai_bot_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ai_bot_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ai_bot_user;

-- Вывод информации
SELECT '✅ База данных инициализирована' as status;