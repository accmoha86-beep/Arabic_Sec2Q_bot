"""
معالج القوائم الرئيسية والتنقل
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


# ══════════════════════════════════════════════
#   لوحة المفاتيح الرئيسية
# ══════════════════════════════════════════════

def main_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📋 الملخصات", callback_data="sum_menu"),
            InlineKeyboardButton("❓ بنك الأسئلة", callback_data="q_cat_menu"),
        ],
        [
            InlineKeyboardButton("🎯 اختبار عشوائي", callback_data="quiz_random"),
            InlineKeyboardButton("📊 المواد", callback_data="subjects_menu"),
        ],
        [
            InlineKeyboardButton("ℹ️ عن البوت", callback_data="about"),
        ],
    ])


WELCOME_TEXT = (
    "🎓 *أهلاً بك في بوت اللغة العربية*\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "📚 الصف الثاني الثانوي\n"
    "📅 الترم الثاني 2026\n"
    "📖 المرجع: سلسلة *الامتحان المتميزون*\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "اختر من القائمة:"
)


# ══════════════════════════════════════════════
#   /start
# ══════════════════════════════════════════════

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        WELCOME_TEXT,
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )


# ══════════════════════════════════════════════
#   عن البوت
# ══════════════════════════════════════════════

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "ℹ️ *عن البوت*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🤖 الاسم: @Arabic_Sec2Q_bot\n"
        "🎓 المرحلة: الثاني الثانوي - ترم ثانٍ\n"
        "📖 المرجع: سلسلة الامتحان المتميزون 2026\n\n"
        "✨ *المحتوى:*\n"
        "• ملخصات جميع المجالات (7 مجالات)\n"
        "• بنك أسئلة تفاعلي بالتوضيح\n"
        "• اختبارات بتقييم فوري وتقدير\n\n"
        "📌 *المجالات المتاحة:*\n"
        "القراءة | البلاغة | الأدب | النصوص\n"
        "النحو | التعبير | القصة\n"
    )
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 الرئيسية", callback_data="main_menu")]
        ])
    )


# ══════════════════════════════════════════════
#   معالج عام للأزرار
# ══════════════════════════════════════════════

async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # ── الرئيسية ─────────────────────────────
    if data == "main_menu":
        await query.edit_message_text(
            WELCOME_TEXT,
            parse_mode="Markdown",
            reply_markup=main_keyboard()
        )

    # ── عن البوت ─────────────────────────────
    elif data == "about":
        await about(update, context)

    # ── المواد ───────────────────────────────
    elif data == "subjects_menu":
        await query.edit_message_text(
            "📊 *المواد الدراسية - الترم الثاني 2026*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "اضغط على المادة للملخصات أو الأسئلة:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📖 القراءة (3 دروس)", callback_data="sum_cat_قراءة"),
                 InlineKeyboardButton("🌸 البلاغة (3 مجالات)", callback_data="sum_cat_بلاغة")],
                [InlineKeyboardButton("📜 الأدب (5 موضوعات)", callback_data="sum_cat_أدب"),
                 InlineKeyboardButton("📝 النصوص (3 نصوص)", callback_data="sum_cat_نصوص")],
                [InlineKeyboardButton("🔤 النحو (4 دروس)", callback_data="sum_cat_نحو"),
                 InlineKeyboardButton("💬 التعبير (2)", callback_data="sum_cat_تعبير")],
                [InlineKeyboardButton("📚 القصة: وا إسلاماه", callback_data="sum_cat_قصة")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")],
            ])
        )
