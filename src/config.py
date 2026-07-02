import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Load from environment variables (for security in production)
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    OWNER_ID = int(os.getenv("OWNER_ID", "0")) if os.getenv("OWNER_ID") else 0

    # Fallback to environment or hardcoded defaults
    REQUIRED_CHANNEL = os.getenv("REQUIRED_CHANNEL", "@startech372")
    REQUIRED_CHANNEL_LINK = os.getenv("REQUIRED_CHANNEL_LINK", "https://t.me/startech372")

    BOT_NAME = "Star AI"
    BOT_CREATOR = "StarDev-il"

    # AI Chat APIs
    DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.hostify.co.zw/api/ai/deepseek")
    GROK_API_URL = os.getenv("GROK_API_URL", "https://api.hostify.co.zw/api/ai/grok")

    # Image generation
    FLUX_API_URL = os.getenv("FLUX_API_URL", "https://api.hostify.co.zw/api/ai/flux")

    # Downloaders
    FB_DOWNLOADER_URL = os.getenv("FB_DOWNLOADER_URL", "https://api.hostify.co.zw/api/downloader/fbdl")
    IG_DOWNLOADER_URL = os.getenv("IG_DOWNLOADER_URL", "https://api.hostify.co.zw/api/downloader/instagram")
    TIKTOK_DOWNLOADER_URL = os.getenv("TIKTOK_DOWNLOADER_URL", "https://api.hostify.co.zw/api/downloader/tiktok")
    YT_VIDEO_URL = os.getenv("YT_VIDEO_URL", "https://api.hostify.co.zw/api/downloader/youtube")
    YT_SONG_URL = os.getenv("YT_SONG_URL", "https://api.hostify.co.zw/api/downloader/ytmp3")

    # Text-to-Speech
    TSUNDERE_API_URL = os.getenv("TSUNDERE_API_URL", "https://api.hostify.co.zw/api/ai/tsundere")
    SVARA_API_URL = os.getenv("SVARA_API_URL", "https://api.hostify.co.zw/api/ai/svara")
    SVARA_DEFAULT_VOICE = "nova"
    SVARA_VOICES = [
        "alloy", "aoede", "bella", "heart", "jessica",
        "kore", "nicole", "nova", "river", "sarah",
        "sky", "adam", "echo", "eric", "fenrir",
        "liam", "michael",
    ]

    USER_NICKNAMES = [
        "Starling", "Comet", "Nova", "Nebula", "Quasar",
        "Pulsar", "Galaxy", "Cosmos", "Orbit", "Eclipse"
    ]

    IMAGE_GEN_KEYWORDS = [
        "generate image", "create image", "make image", "draw", "generate a picture",
        "create a picture", "make a picture", "generate art", "create art",
        "make art", "imagine", "visualize", "render"
    ]

    IMAGE_PULL_KEYWORDS = [
        "download image", "get image", "save image", "pull image",
        "fetch image", "grab image"
    ]

    VIDEO_GEN_KEYWORDS = [
        "generate video", "create video", "make video", "animate"
    ]

    VIDEO_PULL_KEYWORDS = [
        "download video", "get video", "save video", "pull video",
        "fetch video", "grab video", "youtube", "instagram", "facebook",
        "youtu.be", "fb.watch", "reels", "tiktok", "vm.tiktok"
    ]

    MUSIC_KEYWORDS = [
        "music", "song", "lyrics", "play", "download song", "get song",
        "find song", "search song", "audio", "mp3"
    ]

    MEMORY_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "memory.json")
    TELEGRAM_FILE_LIMIT_BYTES = 50 * 1024 * 1024

    # Validate critical config on startup
    @classmethod
    def validate(cls):
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set!")
        if cls.OWNER_ID == 0:
            raise ValueError("OWNER_ID environment variable is not set!")
