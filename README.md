<<<<<<< HEAD
markdown
# 🤖 Telegram Bot with Voice Features

A Telegram bot with voice message support using local AI models. The bot can recognize speech, generate responses using local LLMs, and respond with voice or text.

## ✨ Features

- 🎤 **Speech Recognition** - Convert voice messages to text using Faster-Whisper
- 🔊 **Voice Responses** - Generate natural speech responses using Microsoft Edge TTS
- 💬 **Text Support** - Regular text message handling
- 🗄️ **Conversation History** - Store and manage dialogue history in PostgreSQL
- 🤖 **Local LLMs** - Use any Ollama model for generating responses
- 🔄 **Context Management** - Maintain conversation context within token limits
- 📊 **Statistics** - Track your usage statistics
- 🧹 **History Reset** - Clear conversation history anytime

## 🛠️ Technologies

- **Python 3.11+** - Core programming language
- **python-telegram-bot** - Telegram Bot API wrapper
- **Faster-Whisper** - Optimized speech-to-text
- **Edge TTS** - Microsoft's neural text-to-speech
- **Ollama** - Local LLM management
- **PostgreSQL** - Database for storing conversations
- **Docker** - Containerization for easy deployment

## 📦 Installation

### Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose (optional)
- Ollama installed with at least one model
- PostgreSQL 16+ (if not using Docker)

### Step-by-Step Installation

#### 1. Clone the repository
```bash
git clone <your-repo-url>
cd telegram-voice-bot
```
#### 2. Set up virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```
#### 3. Install dependencies
```bash
pip install -r requirements.txt
```
#### 4. Configure environment variables
```bash
cp .env.example .env
# Edit .env with your values
```
#### 5. Start PostgreSQL
```bash
# Using Docker (recommended)
docker-compose up -d postgres

# Or manually (if you have PostgreSQL installed)
# Create database and user according to your .env settings
```
#### 6. Install Ollama models
```bash
# Pull the model you want to use
ollama pull gemma2:9b
# or
ollama pull llama3.1:8b
# or any other model
```
#### 7. Run the bot
```bash
python -m src.main
🎯 Usage
Available Commands
Command	Description
/start	Start the bot and see welcome message
/voice_on	Enable voice responses
/voice_off	Disable voice responses
/set_voice	Choose preferred voice
/test_edge_tts	Test available voices
/reset	Clear conversation history
/stats	Show usage statistics
How to Use
Text messages: Just type your message and send

Voice messages: Record and send a voice message

Change voice: Use /set_voice followed by voice name

Check stats: Use /stats to see your usage statistics
```

### 🏗️ Project Structure
```text
telegram-voice-bot/
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py      # Environment settings
│   │   └── constants.py     # Constants
│   ├── bot/
│   │   ├── __init__.py
│   │   └── handlers.py      # Command handlers
│   ├── database/
│   │   ├── __init__.py
│   │   ├── repository.py    # DB operations
│   │   └── models.py        # Data models
│   ├── voice/
│   │   ├── __init__.py
│   │   ├── stt_processor.py # Speech-to-text
│   │   ├── tts_manager.py   # Text-to-speech
│   │   └── audio_utils.py   # Audio utilities
│   └── utils/
│       ├── __init__.py
│       ├── logger.py        # Logging setup
│       └── helpers.py       # Helper functions
├── tests/                    # Tests
├── logs/                      # Log files
├── temp/                      # Temporary files
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

### 🔧 Configuration
#### Environment Variables (.env)
```env
# Telegram
BOT_TOKEN=your_bot_token_here

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_NAME=ai_bot_db
POSTGRES_USER=ai_bot_user
POSTGRES_PASSWD=your_password_here

# LLM
MODEL_NAME=gemma2:9b

# Voice
VOICE_ENABLED=True
WHISPER_MODEL=base
MAX_HISTORY=10
```

### Getting a Telegram Bot Token
* Open Telegram and search for @BotFather
* Send /newbot and follow instructions
* Copy the token and add it to your .env file

### 📊 Database Schema
#### Users Table
```sql
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
#### Messages Table
```sql
CREATE TABLE messages (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    model TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 🐳 Docker Deployment
Using Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild and start
docker-compose up -d --build
```

### Building Docker Image Manually
```bash
# Build image
docker build -t voice-bot .

# Run container
docker run -d --name voice-bot --env-file .env voice-bot
```

### 🧪 Testing
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_handlers.py -v

# Run with coverage
pytest --cov=src tests/
```

### 🤝 Contributing
Contributions are welcome! Here's how you can help:

### Fork the repository
1. Create a feature branch (git checkout -b feature/AmazingFeature)
2. Commit your changes (git commit -m 'Add some AmazingFeature')
3. Push to the branch (git push origin feature/AmazingFeature)
4. Open a Pull Request

### Development Guidelines
* Follow PEP 8 style guide
* Add tests for new features
* Update documentation accordingly
* Keep code modular and maintainable

### 📝 License
This project is licensed under the MIT License - see the [LICENSE](https://license/) file for details.

### 👨‍💻 Author
Igor Arefyev
* GitHub: @prince174
* Telegram: @whiteMage174

### ⭐ Support
If you find this project useful, please consider:
* Giving it a star on GitHub ⭐
* Sharing it with others 📢
* Contributing to its development 🤝

### 📧 Contact
For questions, suggestions, or issues:
* Open an [issue](https://github.com/prince174/ai_voice_assistent_with_mem/issues)
* Reach out on Telegram @whiteMage174

### 🙏 Acknowledgments
* [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) for the excellent library
* [Faster-Whisper](https://github.com/guillaumekln/faster-whisper) for fast speech recognition
* [Edge TTS](https://github.com/rany2/edge-tts) for voice synthesis
* [Ollama](https://ollama.ai/) for local LLM support

### 📊 Performance Notes
* Speech Recognition: ~2-5 seconds for a 10-second voice message
* Response Generation: Depends on your hardware and model size
* Voice Synthesis: ~1-3 seconds for typical responses
* Database: PostgreSQL handles thousands of messages efficiently

### 🔒 Security Notes
* All API keys and passwords are stored in .env file (not committed)
* Database credentials are separate from application code
* Temporary audio files are automatically deleted
* No user data is shared with external services

### 🚀 Roadmap
* Add support for multiple languages
* Implement user preferences storage
* Add more voice customization options
* Create web dashboard for statistics
* Add support for image recognition
* Implement rate limiting
* Add more comprehensive tests
* Made with ❤️ for the Telegram bot community
=======
# ai_voice_assistent_with_mem
A Telegram bot with voice message support using local AI models.
>>>>>>> 1e4f3d33f52bdd6ea0eaa6c956277c39ae83f317
