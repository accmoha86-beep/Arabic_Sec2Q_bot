"""
معالج الاختبارات وبنك الأسئلة
"""

import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from data.questions import QUESTIONS

CATEGORY_ICONS = {
    "قراءة": "📖", "بلاغة": "🌸", "أدب": "📜",
    "نصوص": "📝", "نحو": "🔤", "تعبير": "💬",
    "قصة": "📚", "مزيج": "🎯",
}


async def quiz_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # ── قائمة بنك الأسئلة ────────────────────
    if data == "q_cat_menu":
        keyboard = [
            [InlineKeyboardButton("📖 قراءة", callback_data="q_cat_قراءة"),
             InlineKeyboardButton("🌸 بلاغة", callback_data="q_cat_بلاغة")],
            [InlineKeyboardButton("📜 أدب", callback_data="q_cat_أدب"),
             InlineKeyboardButton("📝 نصوص", callback_data="q_cat_نصوص")],
            [InlineKeyboardButton("🔤 نحو", callback_data="q_cat_نحو"),
             InlineKeyboardButton("💬 تعبير", callback_data="q_cat_تعبير")],
            [InlineKeyboardButton("📚 قصة", callback_data="q_cat_قصة")],
            [InlineKeyboardButton("🎯 مزيج عشوائي (10 أسئلة)", callback_data="quiz_random")],
            [InlineKeyboardButton("🏠 الرئيسية", callback_data="main_menu")],
        ]
        await query.edit_message_text(
            "❓ *بنك الأسئلة*\nاختر المادة:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ── اختبار حسب المادة ────────────────────
    elif data.startswith("q_cat_") and data != "q_cat_menu":
        cat = data.replace("q_cat_", "")
        qs = QUESTIONS.get(cat, []).copy()
        if not qs:
            await query.edit_message_text("⚠️ لا توجد أسئلة في هذا المجال حالياً.")
            return
        random.shuffle(qs)
        _init_quiz(context, cat, qs)
        await _send_question(query, context)

    # ── اختبار عشوائي مزيج ───────────────────
    elif data == "quiz_random":
        all_q = []
        for qs in QUESTIONS.values():
            all_q.extend(qs)
        random.shuffle(all_q)
        _init_quiz(context, "مزيج", all_q[:10])
        await _send_question(query, context)

    # ── تسجيل الإجابة ────────────────────────
    elif data.startswith("ans_"):
        chosen = data.replace("ans_", "")
        questions = context.user_data.get("quiz_questions", [])
        idx = context.user_data.get("quiz_index", 0)

        if idx >= len(questions):
            return

        q = questions[idx]
        correct = q["answer"]
        is_correct = chosen == correct
        if is_correct:
            context.user_data["quiz_score"] = context.user_data.get("quiz_score", 0) + 1
            result_text = "✅ *إجابة صحيحة!* 🎉"
        else:
            result_text = f"❌ *إجابة خاطئة!*\n📌 الصواب: *{correct}*"

        context.user_data["quiz_index"] = idx + 1
        explanation = q.get("explanation", "")
        total = len(questions)
        current_score = context.user_data.get("quiz_score", 0)

        keyboard = [[InlineKeyboardButton("التالي ➡️", callback_data="next_q")]]
        await query.edit_message_text(
            f"{result_text}\n\n"
            f"💡 *التوضيح:*\n{explanation}\n\n"
            f"📊 النقاط: {current_score}/{idx + 1}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ── السؤال التالي ────────────────────────
    elif data == "next_q":
        questions = context.user_data.get("quiz_questions", [])
        idx = context.user_data.get("quiz_index", 0)
        if idx < len(questions):
            await _send_question(query, context)
        else:
            await _show_result(query, context)


# ══════════════════════════════════════════════
#   دوال مساعدة
# ══════════════════════════════════════════════

def _init_quiz(context, cat, questions):
    context.user_data["quiz_cat"] = cat
    context.user_data["quiz_index"] = 0
    context.user_data["quiz_score"] = 0
    context.user_data["quiz_questions"] = questions


async def _send_question(query, context):
    questions = context.user_data.get("quiz_questions", [])
    idx = context.user_data.get("quiz_index", 0)
    score = context.user_data.get("quiz_score", 0)
    cat = context.user_data.get("quiz_cat", "")
    icon = CATEGORY_ICONS.get(cat, "❓")

    if idx >= len(questions):
        return

    q = questions[idx]
    total = len(questions)

    # شريط التقدُّم
    filled = "🟩" * idx
    empty = "⬜" * (total - idx)
    progress = f"{filled}{empty} {idx}/{total}"

    keyboard = [
        [InlineKeyboardButton(opt, callback_data=f"ans_{opt[0]}")] for opt in q["options"]
    ]
    keyboard.append([InlineKeyboardButton("❌ إلغاء الاختبار", callback_data="q_cat_menu")])

    await query.edit_message_text(
        f"{icon} *اختبار {cat}*\n"
        f"{progress} | النقاط: {score}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"*س{idx + 1}: {q['q']}*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def _show_result(query, context):
    score = context.user_data.get("quiz_score", 0)
    questions = context.user_data.get("quiz_questions", [])
    total = len(questions)
    pct = int((score / total) * 100) if total > 0 else 0

    # التقدير
    if pct >= 90:
        grade = "🏆 ممتاز جداً"
        msg = "أداء رائع! استمر على هذا المستوى 🌟"
    elif pct >= 75:
        grade = "🥇 جيد جداً"
        msg = "أداء جيد جداً! راجع ما أخطأت فيه."
    elif pct >= 60:
        grade = "🥈 جيد"
        msg = "جيد! لكن تحتاج لمزيد من المراجعة."
    elif pct >= 50:
        grade = "🥉 مقبول"
        msg = "مقبول، راجع الدروس مرة أخرى."
    else:
        grade = "📚 يحتاج مراجعة"
        msg = "لا تيأس! راجع الملخصات وحاول مجدَّداً."

    # رسم شريط النتيجة
    bars = int(pct / 10)
    bar = "🟩" * bars + "⬜" * (10 - bars)

    keyboard = [
        [InlineKeyboardButton("🔄 اختبار جديد", callback_data="q_cat_menu"),
         InlineKeyboardButton("📋 الملخصات", callback_data="sum_menu")],
        [InlineKeyboardButton("🏠 الرئيسية", callback_data="main_menu")],
    ]

    await query.edit_message_text(
        f"🎉 *انتهى الاختبار!*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ الإجابات الصحيحة: *{score}/{total}*\n"
        f"📊 النسبة: *{pct}%*\n"
        f"{bar}\n"
        f"🎖️ التقدير: *{grade}*\n\n"
        f"💬 {msg}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
