# 🌟 Star AI - Telegram Bot

A feature-rich Telegram bot powered by DeepSeek (Lite) and Grok (Pro) AI models, with voice support, image generation, and media downloading.

## ✨ Features

- 🤖 **AI Chat** — Lite (DeepSeek) and Pro (Grok) modes
- 🎙️ **Voice Support** — Send voice notes, get AI replies with TTS
- 🎨 **Image Generation** — FLUX-based image creation and regeneration
- 📥 **Media Downloader** — YouTube, Instagram, TikTok, Facebook videos
- 🎵 **Music** — Download YouTube songs, search lyrics
- 🔐 **Channel Gate** — Restrict access to channel members
- 👑 **Pro Mode** — Owner-controlled access with `/allow` and `/revoke`

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- FFmpeg (for voice transcription)
- Telegram Bot Token

### Local Setup

```bash
# Clone and navigate
git clone https://github.com/jowajoshua09-hub/Star-.git
cd Star-

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your credentials

# Run bot
python main.py
```

### Docker Deployment

```bash
# Copy environment
cp .env.example .env
# Edit .env

# Build and run
docker-compose up -d

# View logs
docker-compose logs -f starai
```

### Systemd (Linux VPS)

```bash
# Create user
sudo useradd -m starai
cd /home/starai
sudo -u starai git clone https://github.com/jowajoshua09-hub/Star-.git
cd Star-

# Setup
sudo -u starai python -m venv venv
sudo -u starai venv/bin/pip install -r requirements.txt
sudo -u starai cp .env.example .env
# Edit .env with credentials

# Install service
sudo cp systemd/starai.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable starai
sudo systemctl start starai

# Monitor
sudo journalctl -u starai -f
```

## 📝 Environment Variables

```env
TELEGRAM_BOT_TOKEN=your_bot_token
OWNER_ID=your_telegram_id
REQUIRED_CHANNEL=@your_channel
REQUIRED_CHANNEL_LINK=https://t.me/your_channel
```

## 💬 Commands

| Command | Description |
|---------|-------------|
| `/start` | Greet and show current mode |
| `/help` | Show features and contact info |
| `/mode` | Switch between Lite and Pro |
| `/voice` | Toggle voice mode & pick voice |
| `/allow <user_id>` | Owner: grant Pro access |
| `/revoke <user_id>` | Owner: revoke Pro access |
| `/prolist` | Owner: list authorized users |

## 🎯 Usage Examples

### Text Chat
```
You: What's 2+2?
Bot: 4! That's correct.
```

### Voice Message
```
You: [Send voice note: "Generate an image of a sunset"]
Bot: [Transcribes] "Generating your image… 🎨" [Sends image]
```

### Image Generation
```
You: Generate a picture of a futuristic city
Bot: [Creates image with 🔄 Regenerate button]
```

### Video Download
```
You: Download https://youtube.com/watch?v=...
Bot: [Shows quality options: 720p, 480p, 360p, MP3]
```

## 🏗️ Architecture

```
main.py (core bot & handlers)
├── src/
│   ├── config.py (environment-based config)
│   ├── core/
│   │   ├── intent_router.py (intent detection)
│   │   ├── personality_engine.py (bot personality)
│   │   └── memory_system.py (user memory)
│   ├── handlers/
│   │   ├── ai_chat_handler.py
│   │   ├── image_gen_handler.py
│   │   ├── video_pull_handler.py
│   │   ├── music_handler.py
│   │   └── ...
│   └── utils/
│       ├── api_client.py (API calls)
│       └── pro_auth.py (authorization)
```

## 🔒 Security

- ✅ Secrets in `.env` (never committed)
- ✅ Environment variable validation
- ✅ Pro mode authorization checks
- ✅ Error handling & logging
- ✅ Channel membership gates

## 📊 Error Handling

All handlers include try-catch blocks:
- Timeout errors → user-friendly messages
- API failures → fallback options (e.g., text if TTS fails)
- Invalid input → helpful error messages
- Callback crashes → logged with alert

## 🐛 Troubleshooting

### Bot doesn't respond
```bash
# Check token is set
echo $TELEGRAM_BOT_TOKEN

# Test locally
python main.py  # Should show "Star AI bot is starting..."
```

### FFmpeg not found
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg
```

### Permission denied errors
```bash
# Fix file permissions
chmod +x main.py
chmod -R 755 data/
```

## 📜 License

MIT

## 👤 Author

StarDev-il (@lllstar372)

## 🤝 Contributing

Feel free to fork and submit pull requests!

---

**Deployed & Running** ✅
