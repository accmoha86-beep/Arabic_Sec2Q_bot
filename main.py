"""
╔══════════════════════════════════════════════════╗
║   بوت اللغة العربية - الثاني الثانوي            ║
║   الترم الثاني 2026 | سلسلة الامتحان            ║
║   @Arabic_Sec2Q_bot                              ║
╚══════════════════════════════════════════════════╝
"""

import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

from config import BOT_TOKEN
from handlers.menu_handler import start, about, main_menu_callback
from handlers.summary_handler import summary_callback
from handlers.quiz_handler import quiz_callback

# ── إعداد اللوغ ──────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 استخدم /start للقائمة الرئيسية",
        parse_mode="Markdown"
    )


def main():
    logger.info("✅ تشغيل بوت اللغة العربية - @Arabic_Sec2Q_bot")
    app = Application.builder().token(BOT_TOKEN).build()

    # أوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("menu", start))

    # أزرار
    app.add_handler(CallbackQueryHandler(summary_callback, pattern="^sum"))
    app.add_handler(CallbackQueryHandler(quiz_callback, pattern="^(quiz|q_cat|ans|next_q)"))
    app.add_handler(CallbackQueryHandler(main_menu_callback))

    # رسائل غير معروفة
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_message))

    logger.info("🚀 البوت يعمل الآن...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
