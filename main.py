import logging
import os

from dotenv import load_dotenv
from openai import OpenAI
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

if not BOT_TOKEN:
    raise RuntimeError("Missing TELEGRAM_BOT_TOKEN environment variable.")
if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY environment variable.")

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """أنت مدرس لغة عربية مصري للصف الثاني الثانوي.
التزم بمنهج اللغة العربية فقط.
اجعل الرد واضحًا ومختصرًا ومفيدًا.
اختم أغلب الردود بسؤال يساعد الطالب يكمل المذاكرة.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(
            "أهلاً 👋
أنا جاهز أساعدك في اللغة العربية للصف الثاني الثانوي.
ابعت سؤالك وأنا أجاوبك."
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(
            "ابعت أي سؤال في العربي، شرح، سؤال نحو، بلاغة، أدب، نصوص، قراءة، أو قصة."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    user_text = update.message.text.strip()
    if not user_text:
        await update.message.reply_text("ابعت السؤال بشكل واضح وأنا أساعدك 😊")
        return

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
        )

        reply = response.choices[0].message.content
        if not reply:
            reply = "حصلت مشكلة بسيطة في تكوين الرد. ابعت سؤالك مرة ثانية."

        await update.message.reply_text(reply)

    except Exception as e:
        logger.exception("OpenAI request failed: %s", e)
        await update.message.reply_text(
            "حصل خطأ أثناء تجهيز الرد. تأكد من API key ثم جرّب مرة ثانية."
        )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Telegram error:", exc_info=context.error)

def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
