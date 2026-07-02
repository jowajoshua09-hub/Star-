import io
import logging
import os
import tempfile

import speech_recognition as sr
from pydub import AudioSegment

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction
from telegram.error import BadRequest
from telegram.ext import Application, MessageHandler, CommandHandler, filters, CallbackQueryHandler

from src.config import Config
from src.core.intent_router import IntentRouter
from src.core.personality_engine import PersonalityEngine
from src.core.memory_system import MemorySystem
from src.utils.api_client import APIClient
from src.utils import pro_auth

from src.handlers.ai_chat_handler import AIChatHandler
from src.handlers.image_gen_handler import ImageGenHandler
from src.handlers.image_pull_handler import ImagePullHandler
from src.handlers.video_gen_handler import VideoGenHandler
from src.handlers.video_pull_handler import VideoPullHandler
from src.handlers.music_handler import MusicHandler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global state — initialized in main()
intent_router = None
personality_engine = None
memory_system = None
api_client = None
ai_chat_handler = None
image_gen_handler = None
image_pull_handler = None
video_gen_handler = None
video_pull_handler = None
music_handler = None

OWNER_ID = Config.OWNER_ID

OWNER_KEYWORDS = [
    "owner", "creator", "who made you", "who created you",
    "who built you", "contact", "developer", "dev"
]


# ── CHANNEL GATE ─────────────────────────────────────────────────────────────

async def is_channel_member(bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(
            chat_id=Config.REQUIRED_CHANNEL, user_id=user_id
        )
        return member.status not in ("left", "kicked", "banned")
    except BadRequest:
        return True
    except Exception as e:
        logger.warning(f"Error checking channel membership: {e}")
        return True


async def send_join_prompt(update: Update):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Channel", url=Config.REQUIRED_CHANNEL_LINK)],
    ])
    await update.message.reply_text(
        f"🔒 You must join our channel to use Star AI!\n\n"
        f"👉 Join here: {Config.REQUIRED_CHANNEL_LINK}\n\n"
        f"Then send any message to continue.",
        reply_markup=keyboard
    )


# ── KEYBOARDS ────────────────────────────────────────────────────────────────

def get_owner_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 WhatsApp", url="https://wa.me/263783633309")],
        [InlineKeyboardButton("✈️ Telegram",  url="https://t.me/lllstar372")],
    ])


def get_mode_keyboard(current_mode: str):
    lite_label = "⚡ Star AI Lite  ✅" if current_mode == "lite" else "⚡ Star AI Lite"
    pro_label  = "🚀 Star AI Pro   ✅" if current_mode == "pro"  else "🚀 Star AI Pro"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(lite_label, callback_data="mode_lite")],
        [InlineKeyboardButton(pro_label,  callback_data="mode_pro")],
    ])


def get_voice_keyboard(voice_on: bool, current_voice: str):
    toggle_label = "🔇 Turn Voice OFF" if voice_on else "🔊 Turn Voice ON"
    rows = [[InlineKeyboardButton(toggle_label, callback_data="voice_toggle")]]
    # Voice picker grid (3 per row)
    voices = Config.SVARA_VOICES
    row = []
    for v in voices:
        label = f"✅ {v}" if v == current_voice else v
        row.append(InlineKeyboardButton(label, callback_data=f"vset_{v}"))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(rows)


# ── COMMAND HANDLERS ─────────────────────────────────────────────────────────

async def start(update: Update, context):
    user = update.effective_user
    if not await is_channel_member(context.bot, user.id):
        await send_join_prompt(update)
        return
    memory_system.set_username(user.id, user.first_name or user.username)
    mode = context.user_data.get("mode", "lite")
    mode_label = "⚡ Lite" if mode == "lite" else "🚀 Pro"
    await update.message.reply_html(
        f"{personality_engine.get_greeting(user.first_name or user.username)}\n\n"
        f"Current mode: <b>{mode_label}</b> — use /mode to switch."
    )


async def help_command(update: Update, context):
    user = update.effective_user
    if not await is_channel_member(context.bot, user.id):
        await send_join_prompt(update)
        return
    text = (
        "🌟 <b>Star AI</b> — built by StarDev-il\n\n"
        "<b>What I can do:</b>\n"
        "• AI chat (Lite &amp; Pro modes)\n"
        "• Voice notes — just send a voice message!\n"
        "• Image generation\n"
        "• Download YouTube, Instagram, Facebook &amp; TikTok videos\n"
        "• Download YouTube songs (mp3)\n"
        "• Lyrics search\n\n"
        "<b>Commands:</b>\n"
        "/start — greet me\n"
        "/mode  — switch between Lite &amp; Pro AI\n"
        "/voice — toggle live voice replies &amp; pick a voice\n"
        "/help  — show this menu\n\n"
        "📬 <b>Contact the owner:</b>"
    )
    await update.message.reply_html(text, reply_markup=get_owner_keyboard())


async def mode_command(update: Update, context):
    user = update.effective_user
    if not await is_channel_member(context.bot, user.id):
        await send_join_prompt(update)
        return
    current = context.user_data.get("mode", "lite")
    await update.message.reply_text(
        "Choose your AI mode:\n\n"
        "⚡ <b>Star AI Lite</b> — DeepSeek, fast &amp; snappy\n"
        "🚀 <b>Star AI Pro</b>  — Grok, more powerful &amp; creative",
        parse_mode="HTML",
        reply_markup=get_mode_keyboard(current)
    )


async def voice_command(update: Update, context):
    user = update.effective_user
    if not await is_channel_member(context.bot, user.id):
        await send_join_prompt(update)
        return
    voice_on = context.user_data.get("voice_mode", False)
    voice_name = context.user_data.get("voice_name", Config.SVARA_DEFAULT_VOICE)
    status = "🔊 ON" if voice_on else "🔇 OFF"
    await update.message.reply_text(
        f"🎙️ <b>Live Voice Mode</b> — {status}\n"
        f"Current voice: <b>{voice_name}</b>\n\n"
        f"When ON, every AI reply is also sent as a voice message.\n"
        f"Pick a voice below, then toggle it on:",
        parse_mode="HTML",
        reply_markup=get_voice_keyboard(voice_on, voice_name)
    )


async def allow_command(update: Update, context):
    """Owner-only: /allow <user_id>"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Owner only.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /allow <user_id>")
        return
    try:
        target = int(context.args[0])
        pro_auth.authorize(target)
        await update.message.reply_text(f"✅ User {target} can now use Pro mode.")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")


async def revoke_command(update: Update, context):
    """Owner-only: /revoke <user_id>"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Owner only.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /revoke <user_id>")
        return
    try:
        target = int(context.args[0])
        pro_auth.revoke(target)
        await update.message.reply_text(f"🚫 Pro access removed for user {target}.")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")


async def prolist_command(update: Update, context):
    """Owner-only: list all Pro-authorized users."""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Owner only.")
        return
    users = pro_auth.list_authorized()
    if users:
        await update.message.reply_text("🚀 Pro-authorized users:\n" + "\n".join(str(u) for u in users))
    else:
        await update.message.reply_text("No users authorized for Pro (owner always has access).")


# ── VOICE TRANSCRIPTION ───────────────────────────────────────────────────────

async def transcribe_voice(bot, voice) -> str | None:
    """Download a Telegram voice note and return its transcript (or None)."""
    ogg_path = None
    wav_path = None
    try:
        file = await bot.get_file(voice.file_id)
        ogg_bytes = await file.download_as_bytearray()

        # Write OGG to a real temp file — BytesIO is unreliable with pydub/ffmpeg for OPUS
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as f:
            f.write(bytes(ogg_bytes))
            ogg_path = f.name

        wav_path = ogg_path.replace(".ogg", ".wav")

        # Convert with ffmpeg directly — most reliable for OGG OPUS
        import subprocess
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", ogg_path, "-ar", "16000", "-ac", "1", wav_path],
            capture_output=True, timeout=15
        )
        if result.returncode != 0:
            logger.warning(f"ffmpeg conversion failed: {result.stderr.decode()}")
            return None

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data, language="en-US")
        return text.strip() if text else None

    except sr.UnknownValueError:
        logger.info("Voice note could not be understood")
        return None
    except sr.RequestError as e:
        logger.warning(f"Google STT request error: {e}")
        return None
    except Exception as e:
        logger.warning(f"Voice transcription failed: {e}")
        return None
    finally:
        for path in (ogg_path, wav_path):
            if path:
                try:
                    os.remove(path)
                except Exception:
                    pass


# ── MESSAGE HANDLERS ──────────────────────────────────────────────────────────

async def handle_voice(update: Update, context):
    user = update.effective_user
    chat_id = update.effective_chat.id

    if not await is_channel_member(context.bot, user.id):
        await send_join_prompt(update)
        return

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    transcript = await transcribe_voice(context.bot, update.message.voice)
    if not transcript:
        await update.message.reply_text("🎙️ Sorry, I couldn't understand that voice note. Try again or type your message.")
        return

    await update.message.reply_text(f"🎙️ _You said:_ {transcript}", parse_mode="Markdown")

    intent = intent_router.detect_intent(transcript)
    logger.info(f"voice intent={intent} user={user.id} transcript={transcript[:60]}")
    update.message.text = transcript

    # Non-AI intents — handle normally with text reply
    if intent == "image_gen":
        await image_gen_handler.handle(update, context)
        return
    elif intent == "video_pull":
        await video_pull_handler.handle(update, context)
        return
    elif intent == "music":
        await music_handler.handle(update, context)
        return

    # AI chat — get text response then convert to voice
    mode = context.user_data.get("mode", "lite")
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.RECORD_VOICE)

    # Step 1: get AI text (once)
    try:
        ai_text = await api_client.get_ai_response(transcript, mode=mode)
        ai_text = personality_engine.format_response(ai_text, user_id=user.id)
    except Exception as e:
        logger.error(f"AI response failed in voice handler: {e}")
        await update.message.reply_text("⚠️ Couldn't get a response right now. Try again!")
        return

    # Step 2: TTS — try tsundere, fall back to svara, fall back to text
    tts_text = ai_text[:500]  # APIs may reject very long strings
    try:
        try:
            audio_bytes = await api_client.tts_tsundere(tts_text)
        except Exception as e:
            logger.warning(f"tsundere TTS failed ({e}), trying svara...")
            audio_bytes = await api_client.tts_svara(tts_text)

        caption = f"_{ai_text[:200]}{'...' if len(ai_text) > 200 else ''}_"
        await context.bot.send_voice(
            chat_id=chat_id,
            voice=io.BytesIO(audio_bytes),
            caption=caption,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"TTS failed, sending text reply instead: {e}")
        await update.message.reply_text(ai_text)


async def handle_message(update: Update, context):
    user = update.effective_user
    user_message = update.message.text
    if not user_message:
        return

    if not await is_channel_member(context.bot, user.id):
        await send_join_prompt(update)
        return

    if any(kw in user_message.lower() for kw in OWNER_KEYWORDS):
        await update.message.reply_text(
            "Here's how to reach the owner of Star AI 👇",
            reply_markup=get_owner_keyboard()
        )
        return

    intent = intent_router.detect_intent(user_message)
    logger.info(f"intent={intent} user={user.id} msg={user_message[:60]}")

    if intent == "image_gen":
        await image_gen_handler.handle(update, context)
    elif intent == "image_pull":
        await image_pull_handler.handle(update, context)
    elif intent == "video_gen":
        await video_gen_handler.handle(update, context)
    elif intent == "video_pull":
        await video_pull_handler.handle(update, context)
    elif intent == "music":
        await music_handler.handle(update, context)
    else:
        await ai_chat_handler.handle(update, context)


# ── CALLBACK HANDLER ──────────────────────────────────────────────────────────

async def handle_callback(update: Update, context):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    try:
        # ── Mode switcher ─────────────────────────────────────────────────────────
        if data == "mode_lite":
            await query.answer()
            context.user_data["mode"] = "lite"
            await query.edit_message_text(
                "⚡ Switched to <b>Star AI Lite</b> (DeepSeek) — fast &amp; efficient!",
                parse_mode="HTML",
                reply_markup=get_mode_keyboard("lite")
            )

        elif data == "mode_pro":
            if not pro_auth.is_pro_authorized(user_id, OWNER_ID):
                await query.answer(
                    "🔒 Pro mode is restricted. Contact the owner to get access.",
                    show_alert=True
                )
                return
            await query.answer()
            context.user_data["mode"] = "pro"
            await query.edit_message_text(
                "🚀 Switched to <b>Star AI Pro</b> (Grok) — powerful &amp; creative!",
                parse_mode="HTML",
                reply_markup=get_mode_keyboard("pro")
            )

        # ── Video quality / format ────────────────────────────────────────────────
        elif data in ("vid_720", "vid_480", "vid_360", "vid_mp3", "vid_direct", "vid_doc"):
            choice = data.replace("vid_", "")
            await video_pull_handler.handle_callback(update, context, choice)

        # ── Image regenerate ──────────────────────────────────────────────────────
        elif data == "img_regen":
            await image_gen_handler.handle_regen(update, context)

        # ── Song format ───────────────────────────────────────────────────────────
        elif data in ("song_audio", "song_doc"):
            await music_handler.handle_callback(update, context)

        # ── Voice mode toggle ─────────────────────────────────────────────────────
        elif data == "voice_toggle":
            await query.answer()
            current = context.user_data.get("voice_mode", False)
            context.user_data["voice_mode"] = not current
            voice_on = context.user_data["voice_mode"]
            voice_name = context.user_data.get("voice_name", Config.SVARA_DEFAULT_VOICE)
            status = "🔊 ON" if voice_on else "🔇 OFF"
            await query.edit_message_text(
                f"🎙️ <b>Live Voice Mode</b> — {status}\n"
                f"Current voice: <b>{voice_name}</b>\n\n"
                f"When ON, every AI reply is also sent as a voice message.\n"
                f"Pick a voice below, then toggle it on:",
                parse_mode="HTML",
                reply_markup=get_voice_keyboard(voice_on, voice_name)
            )

        # ── Voice picker ──────────────────────────────────────────────────────────
        elif data.startswith("vset_"):
            chosen = data[len("vset_"):]
            if chosen in Config.SVARA_VOICES:
                context.user_data["voice_name"] = chosen
                await query.answer(f"Voice set to {chosen} ✅")
                voice_on = context.user_data.get("voice_mode", False)
                await query.edit_message_text(
                    f"🎙️ <b>Live Voice Mode</b> — {'🔊 ON' if voice_on else '🔇 OFF'}\n"
                    f"Current voice: <b>{chosen}</b>\n\n"
                    f"When ON, every AI reply is also sent as a voice message.\n"
                    f"Pick a voice below, then toggle it on:",
                    parse_mode="HTML",
                    reply_markup=get_voice_keyboard(voice_on, chosen)
                )
            else:
                await query.answer("Unknown voice.", show_alert=True)
        else:
            logger.warning(f"Unknown callback data: {data}")
            await query.answer("Unknown action.", show_alert=True)
    except Exception as e:
        logger.error(f"Error in callback handler: {e}")
        try:
            await query.answer("An error occurred.", show_alert=True)
        except:
            pass


# ── LIFECYCLE ─────────────────────────────────────────────────────────────────

async def post_init(application: Application):
    global api_client
    try:
        api_client = APIClient()
        ai_chat_handler.api_client    = api_client
        image_gen_handler.api_client  = api_client
        image_pull_handler.api_client = api_client
        video_pull_handler.api_client = api_client
        music_handler.api_client      = api_client
        logger.info("APIClient session initialised.")
    except Exception as e:
        logger.error(f"Failed to initialize APIClient: {e}")
        raise


async def post_shutdown(application: Application):
    global api_client
    try:
        if api_client:
            await api_client.close_session()
            logger.info("APIClient session closed.")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


def main():
    global intent_router, personality_engine, memory_system, api_client
    global ai_chat_handler, image_gen_handler, image_pull_handler
    global video_gen_handler, video_pull_handler, music_handler

    # Validate configuration on startup
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise

    intent_router      = IntentRouter()
    personality_engine = PersonalityEngine()
    memory_system      = MemorySystem()

    ai_chat_handler    = AIChatHandler(None, personality_engine)
    image_gen_handler  = ImageGenHandler(None, personality_engine)
    image_pull_handler = ImagePullHandler(None, personality_engine)
    video_gen_handler  = VideoGenHandler(personality_engine)
    video_pull_handler = VideoPullHandler(None, personality_engine)
    music_handler      = MusicHandler(None, personality_engine)

    application = (
        Application.builder()
        .token(Config.TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    application.add_handler(CommandHandler("start",   start))
    application.add_handler(CommandHandler("help",    help_command))
    application.add_handler(CommandHandler("mode",    mode_command))
    application.add_handler(CommandHandler("voice",   voice_command))
    application.add_handler(CommandHandler("allow",   allow_command))
    application.add_handler(CommandHandler("revoke",  revoke_command))
    application.add_handler(CommandHandler("prolist", prolist_command))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_callback))

    logger.info("Star AI bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
