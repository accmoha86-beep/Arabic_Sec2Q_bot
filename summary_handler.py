"""
معالج الملخصات
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from data.summaries import SUMMARIES

# ── خريطة الفئات ──────────────────────────────
CATEGORY_MAP = {
    "قراءة": [
        ("📖 السَّلَام", "قراءة_السلام"),
        ("📖 اللغة والهُوِيَّة", "قراءة_اللغة_والهوية"),
        ("📖 مِضريُّون... مِصريُّون", "قراءة_مضريون"),
    ],
    "بلاغة": [
        ("🌸 علم البيان", "بلاغة_علم_البيان"),
        ("🌸 علم البديع", "بلاغة_علم_البديع"),
        ("🌸 علم المعاني", "بلاغة_علم_المعاني"),
    ],
    "أدب": [
        ("📜 الغزل العباسي", "أدب_الغزل_العباسي"),
        ("📜 الأدب الأندلسي", "أدب_الأندلس"),
        ("📜 الرومانتيكية", "أدب_الرومانتيكية"),
        ("📜 الشعر الوطني", "أدب_الشعر_الوطني"),
        ("📜 فن المقال", "أدب_فن_المقال"),
    ],
    "نصوص": [
        ("📝 حُبٌّ وَوَفَاء", "نص_حب_ووفاء"),
        ("📝 عِتاب اللغة الغريبة", "نص_عتاب_اللغة"),
        ("📝 غُودوا إلى مِصر", "نص_غودوا_مصر"),
    ],
    "نحو": [
        ("🔤 أسلوب التعجُّب", "نحو_اسلوب_التعجب"),
        ("🔤 أسلوب الاختصاص", "نحو_اسلوب_الاختصاص"),
        ("🔤 أسماء الأفعال", "نحو_اسماء_الافعال"),
        ("🔤 لا النافية للجنس", "نحو_لا_النافية_للجنس"),
    ],
    "تعبير": [
        ("💬 التعبير الوظيفي", "تعبير_وظيفي"),
        ("💬 التعبير الإبداعي", "تعبير_إبداعي"),
    ],
    "قصة": [
        ("📚 وا إسلاماه", "قصة_وا_اسلاماه"),
    ],
}

CATEGORY_ICONS = {
    "قراءة": "📖", "بلاغة": "🌸", "أدب": "📜",
    "نصوص": "📝", "نحو": "🔤", "تعبير": "💬", "قصة": "📚",
}


async def summary_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # ── قائمة الملخصات الرئيسية ───────────────
    if data == "sum_menu":
        keyboard = [
            [InlineKeyboardButton("📖 القراءة", callback_data="sum_cat_قراءة"),
             InlineKeyboardButton("🌸 البلاغة", callback_data="sum_cat_بلاغة")],
            [InlineKeyboardButton("📜 الأدب", callback_data="sum_cat_أدب"),
             InlineKeyboardButton("📝 النصوص", callback_data="sum_cat_نصوص")],
            [InlineKeyboardButton("🔤 النحو", callback_data="sum_cat_نحو"),
             InlineKeyboardButton("💬 التعبير", callback_data="sum_cat_تعبير")],
            [InlineKeyboardButton("📚 القصة", callback_data="sum_cat_قصة")],
            [InlineKeyboardButton("🏠 الرئيسية", callback_data="main_menu")],
        ]
        await query.edit_message_text(
            "📋 *الملخصات*\nاختر المجال:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ── قائمة دروس المجال ────────────────────
    elif data.startswith("sum_cat_"):
        cat = data.replace("sum_cat_", "")
        items = CATEGORY_MAP.get(cat, [])
        icon = CATEGORY_ICONS.get(cat, "📚")
        keyboard = [[InlineKeyboardButton(name, callback_data=f"sum_show_{key}")] for name, key in items]
        keyboard.append([InlineKeyboardButton("🔙 رجوع للملخصات", callback_data="sum_menu"),
                         InlineKeyboardButton("🏠 الرئيسية", callback_data="main_menu")])
        await query.edit_message_text(
            f"{icon} *مجال {cat}*\nاختر الدرس:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ── عرض ملخص درس ─────────────────────────
    elif data.startswith("sum_show_"):
        key = data.replace("sum_show_", "")
        summary = SUMMARIES.get(key)
        if not summary:
            await query.edit_message_text("⚠️ لم يُوجد هذا الملخص.")
            return

        # تحديد المجال للرجوع
        cat = key.split("_")[0]
        keyboard = [
            [InlineKeyboardButton(f"🔙 رجوع لـ{cat}", callback_data=f"sum_cat_{cat}"),
             InlineKeyboardButton("📋 كل الملخصات", callback_data="sum_menu")],
            [InlineKeyboardButton("🏠 الرئيسية", callback_data="main_menu")],
        ]
        text = f"{summary['title']}\n━━━━━━━━━━━━━━━━━━━━━━━━\n{summary['content']}"

        # تيليجرام محدود بـ 4096 حرف
        if len(text) > 4000:
            text = text[:3990] + "\n\n...(يتبع)"

        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
