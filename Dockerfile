FROM python:3.11-slim

# Аргументы сборки (не сохраняются в итоговом образе)
ARG USERNAME=botuser
ARG USER_UID=1000
ARG USER_GID=1000

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создание непривилегированного пользователя
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && mkdir -p /app \
    && chown $USERNAME:$USERNAME /app

# Переключение на рабочую директорию
WORKDIR /app

# Копирование файла с зависимостями (сначала только requirements.txt для кэширования)
COPY --chown=$USERNAME:$USERNAME requirements.txt .

# Установка зависимостей Python
RUN pip install --no-cache-dir --user -r requirements.txt

# Копирование остального кода
COPY --chown=$USERNAME:$USERNAME . .

# Создание папок для логов и временных файлов с правильными правами
RUN mkdir -p logs temp \
    && chown -R $USERNAME:$USERNAME logs temp

# Установка переменных окружения по умолчанию (будут переопределены при запуске)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=UTC

# Добавление пользовательского пути в PATH
ENV PATH="/home/$USERNAME/.local/bin:${PATH}"

# Переключение на непривилегированного пользователя
USER $USERNAME

# Проверка здоровья контейнера
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8080/health || exit 1

# Запуск бота
CMD ["python", "-m", "src.main"]