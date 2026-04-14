import logging, random, os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Application, CommandHandler, CallbackQueryHandler,
                          ContextTypes, MessageHandler, filters)
from openai import OpenAI

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ استخدام Environment Variables بدل التوكن
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN:
    raise RuntimeError("Missing TELEGRAM_BOT_TOKEN")

if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY")

ai = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = "أنت مدرس لغة عربية للصف الثاني الثانوي، اشرح ببساطة واسأل الطالب."

# ================== القائمة الرئيسية ==================
def main_menu():
    keyboard = [
        [InlineKeyboardButton("📖 القراءة", callback_data="reading")],
        [InlineKeyboardButton("🌸 البلاغة", callback_data="rhetoric")],
        [InlineKeyboardButton("📜 الأدب", callback_data="literature")],
        [InlineKeyboardButton("🔤 النحو", callback_data="grammar")],
        [InlineKeyboardButton("📝 النصوص", callback_data="texts")],
        [InlineKeyboardButton("💬 التعبير", callback_data="writing")],
        [InlineKeyboardButton("📚 القصة", callback_data="story")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ================== start ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("اختر القسم 👇", reply_markup=main_menu())

# ================== الرد على الأزرار ==================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text_map = {
        "reading": "📖 اختر درس القراءة",
        "rhetoric": "🌸 اختر فرع البلاغة",
        "literature": "📜 اختر درس الأدب",
        "grammar": "🔤 اختر درس النحو",
        "texts": "📝 اختر النص",
        "writing": "💬 اختر نوع التعبير",
        "story": "📚 اختر جزء القصة",
    }

    await query.edit_message_text(text_map.get(query.data, "اختر من القائمة"))

# ================== الذكاء الاصطناعي ==================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    try:
        response = ai.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
        )

        reply = response.choices[0].message.content
        await update.message.reply_text(reply)

    except Exception as e:
        logger.error(e)
        await update.message.reply_text("حصل خطأ 😥")

# ================== التشغيل ==================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
