import logging
import os
import random
from typing import Dict, List, Optional

from openai import OpenAI
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN:
    raise RuntimeError("Missing TELEGRAM_BOT_TOKEN")
if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """أنت "أستاذ كريم" - مدرّس لغة عربية مصري للصف الثاني الثانوي الترم الثاني 2026.
التزم بمنهج اللغة العربية فقط.
الرد يكون واضحًا، قصيرًا نسبيًا، مشجعًا، وبروح مصرية خفيفة.
بعد الشرح اختم غالبًا بسؤال: "فاهم كده؟ 😊 ولا نعيد بطريقة تانية؟"
لو السؤال خارج المنهج فقل بلطف إنك متخصص في العربي فقط.
"""

LESSONS = {
    "قراءة_السلام": {"subject": "قراءة", "title": "📖 درس السلام", "summary": "قيمة السلام حاجة إنسانية وضرورة حضارية. السلام أساس التعاون والتقدم، والحرب تدمر الحضارات، وللفرد دور في نشر ثقافة التعايش والتسامح."},
    "قراءة_اللغة_والهوية": {"subject": "قراءة", "title": "📖 اللغة والهوية", "summary": "اللغة العربية ركيزة الهوية الوطنية. هي وعاء الفكر والثقافة، وترتبط بالانتماء، ويجب الحفاظ على الفصحى في مواجهة تحديات العصر."},
    "قراءة_مضريون": {"subject": "قراءة", "title": "📖 مضريون... مصريون", "summary": "الدرس يبرز عمق الانتماء المصري عبر التاريخ، وأن الارتباط بالأرض يصنع هوية راسخة، وأن التنوع الحضاري مصدر قوة وفخر."},
    "بلاغة_البيان": {"subject": "بلاغة", "title": "🌸 علم البيان", "summary": "يشمل التشبيه والاستعارة والكناية والمجاز المرسل. من أمثلته: العلم نورٌ تشبيه بليغ، ورأيت أسدًا يحاضر استعارة تصريحية، ونثر الليل نجومه استعارة مكنية."},
    "بلاغة_البديع": {"subject": "بلاغة", "title": "🌸 علم البديع", "summary": "يشمل الجناس والسجع والطباق والمقابلة والتورية وحسن التعليل. الطباق يبرز المعنى بالتضاد، والجناس يضيف نغمة موسيقية جميلة."},
    "بلاغة_المعاني": {"subject": "بلاغة", "title": "🌸 علم المعاني", "summary": "يشمل الخبر والإنشاء وأغراضهما البلاغية، مثل الأمر للدعاء أو الإرشاد، والاستفهام للنفي أو التقرير أو التعجب، مع أساليب التوكيد المختلفة."},
    "أدب_الغزل_العباسي": {"subject": "أدب", "title": "📜 الغزل العباسي", "summary": "منه عذري وصريح. ازدهر بسبب الترف والتأثر بالثقافات ومجالس الأنس. من أعلامه العباس بن الأحنف وبشار بن برد وأبو نواس."},
    "أدب_الأندلس": {"subject": "أدب", "title": "📜 الأدب الأندلسي", "summary": "امتاز بوصف الطبيعة والحنين وابتكار الموشح والزجل. من أعلامه ابن زيدون وابن حزم وابن قزمان."},
    "أدب_الرومانتيكية": {"subject": "أدب", "title": "📜 المدرسة الرومانتيكية", "summary": "تعتمد على التعبير عن المشاعر الذاتية والخيال والطبيعة والحزن والغربة. من روادها جماعة الديوان ومدرسة المهجر."},
    "أدب_الشعر_الوطني": {"subject": "أدب", "title": "📜 الشعر الوطني", "summary": "يعبر عن حب الوطن والدفاع عنه. من سماته الحماسة والوضوح وتوظيف التاريخ والوحدة. من شعرائه أحمد شوقي وحافظ إبراهيم والأبنودي."},
    "أدب_فن_المقال": {"subject": "أدب", "title": "📜 فن المقال", "summary": "قطعة نثرية تعالج موضوعًا واحدًا. منه الذاتي والموضوعي، وبنيته: مقدمة وعرض وخاتمة، ويتميز بوحدة الموضوع ووضوح الفكرة."},
    "نص_حب_ووفاء": {"subject": "نصوص", "title": "📝 حب ووفاء", "summary": "يتناول الحب الصادق والوفاء رغم البعد، وفيه استعارة وطباق وكناية، ويبرز قيمة الإخلاص والوفاء في العلاقات الإنسانية."},
    "نص_عتاب_اللغة": {"subject": "نصوص", "title": "📝 عتاب اللغة", "summary": "النص يصور اللغة العربية ككائن حي يعاتب أبناءه لإهمالها، وفيه تشخيص وأسلوب خطابي واستفهام ونداء للتأثير."},
    "نص_غودوا_إلى_مصر": {"subject": "نصوص", "title": "📝 غودوا إلى مصر", "summary": "دعوة إلى العودة والانتماء لمصر، وفيه نداء وأمر وتكرار، ويؤكد أن مصر روح وهوية وجذور لا تُنسى."},
    "نحو_التعجب": {"subject": "نحو", "title": "🔤 أسلوب التعجب", "summary": "له صيغتان قياسيتان: ما أفعلَه! وأفعِل به! ويشترط في الفعل سبعة شروط مثل أن يكون ثلاثيًا تامًا مثبتًا قابلًا للتفاوت."},
    "نحو_الاختصاص": {"subject": "نحو", "title": "🔤 أسلوب الاختصاص", "summary": "يتكون من ضمير يتبعه اسم ظاهر منصوب يسمى المختص، منصوب بفعل محذوف تقديره أخص أو أعني، مثل: نحن العربَ نكرم الضيف."},
    "نحو_اسماء_الافعال": {"subject": "نحو", "title": "🔤 أسماء الأفعال", "summary": "ألفاظ تدل على معنى الفعل وتعمل عمله، منها ماضٍ مثل هيهات، ومضارع مثل أفٍّ، وأمر مثل صه ومه وآمين."},
    "نحو_لا_النافية_للجنس": {"subject": "نحو", "title": "🔤 لا النافية للجنس", "summary": "تنفي الجنس كله وتعمل عمل إن. يشترط أن يكون اسمها وخبرها نكرتين، وألا يفصل بينها وبين اسمها فاصل، وألا تسبق بحرف جر."},
    "تعبير_وظيفي": {"subject": "تعبير", "title": "💬 التعبير الوظيفي", "summary": "يشمل التقرير والخطاب الرسمي والإعلان والسيرة الذاتية، ويتميز بالوضوح والإيجاز والتنظيم واللغة الرسمية الفصيحة."},
    "تعبير_إبداعي": {"subject": "تعبير", "title": "💬 التعبير الإبداعي", "summary": "يشمل القصة والمقال الأدبي والخاطرة والوصف، ويعتمد على مقدمة جذابة وأفكار مترابطة وخاتمة مؤثرة وصور بيانية طبيعية."},
    "قصة_وا_اسلاماه": {"subject": "قصة", "title": "📚 وا إسلاماه", "summary": "رواية تاريخية لعلي أحمد باكثير عن عصر المغول. من شخصياتها قطز وبيبرس وأيبك وأيدكين وهولاكو. وتنتهي بانتصار المسلمين في عين جالوت."},
    "قصة_ملخص_الاحداث": {"subject": "قصة", "title": "📚 ملخص أحداث وا إسلاماه", "summary": "يركز الملخص على الفصول التاسع والعاشر والرابع عشر والخامس عشر: نفي العز، انتقال قطز إلى مصر، الاستعداد لقتال التتار، ثم معركة عين جالوت وانتصار المسلمين."},
    "قصة_اسئلة_عامة": {"subject": "قصة", "title": "📚 أسئلة عامة على القصة", "summary": "أهم الأسئلة تدور حول دلالة العنوان، رسالة باكثير، صفات قطز وأيبك، وأهمية معركة عين جالوت كذروة للرواية التاريخية."},
}

SUBJECTS = {
    "قراءة": ["قراءة_السلام", "قراءة_اللغة_والهوية", "قراءة_مضريون"],
    "بلاغة": ["بلاغة_البيان", "بلاغة_البديع", "بلاغة_المعاني"],
    "أدب": ["أدب_الغزل_العباسي", "أدب_الأندلس", "أدب_الرومانتيكية", "أدب_الشعر_الوطني", "أدب_فن_المقال"],
    "نصوص": ["نص_حب_ووفاء", "نص_عتاب_اللغة", "نص_غودوا_إلى_مصر"],
    "نحو": ["نحو_التعجب", "نحو_الاختصاص", "نحو_اسماء_الافعال", "نحو_لا_النافية_للجنس"],
    "تعبير": ["تعبير_وظيفي", "تعبير_إبداعي"],
    "قصة": ["قصة_وا_اسلاماه", "قصة_ملخص_الاحداث", "قصة_اسئلة_عامة"],
}

QUESTIONS = {
    "قراءة": [
        {"q": "ما نواتج التعلم الثلاثة في القراءة؟", "options": ["الفهم والتذوق والنقد", "الحفظ والتلاوة", "النحو والإملاء", "الكتابة فقط"], "answer": 0, "exp": "نواتج التعلم في القراءة هي: الفهم، التذوق، النقد."},
        {"q": "ما الفكرة العامة لدرس السلام؟", "options": ["تاريخ الحروب", "السلام ضرورة إنسانية وحضارية", "اللغة والهوية", "الهجرة"], "answer": 1, "exp": "الدرس يؤكد أن السلام ضرورة إنسانية وحضارية."},
        {"q": "اللغة في درس اللغة والهوية تُعد:", "options": ["زينة فقط", "وعاء الفكر والثقافة", "لهجة عامية", "موضوعًا ثانويًا"], "answer": 1, "exp": "اللغة وعاء الفكر والثقافة والحضارة."},
        {"q": "مِضريون... مصريون يركز على:", "options": ["الوصف الطبيعي", "الانتماء المصري", "النحو", "الغزل"], "answer": 1, "exp": "الدرس يبرز عمق الانتماء المصري عبر التاريخ."},
        {"q": "الوئام مضادها:", "options": ["السلام", "التسامح", "الخصام", "الاندماج"], "answer": 2, "exp": "الوئام عكسه الخصام."},
    ],
    "بلاغة": [
        {"q": "العلم نورٌ نوعه:", "options": ["استعارة مكنية", "تشبيه بليغ", "كناية", "مجاز مرسل"], "answer": 1, "exp": "العلم نور تشبيه بليغ لحذف الأداة ووجه الشبه."},
        {"q": "رأيت أسدًا يحاضر نوع الصورة:", "options": ["كناية", "استعارة تصريحية", "تشبيه تمثيلي", "طباق"], "answer": 1, "exp": "حُذف المشبه وصرح بالمشبه به، فهي استعارة تصريحية."},
        {"q": "نثر الليل نجومه نوع الصورة:", "options": ["استعارة مكنية", "تشبيه بليغ", "كناية عن صفة", "جناس"], "answer": 0, "exp": "شُبه الليل بإنسان ينثر، فهي استعارة مكنية."},
        {"q": "يعطي ويمنع مثال على:", "options": ["جناس", "طباق إيجاب", "طباق سلب", "مقابلة"], "answer": 1, "exp": "يجمع بين لفظين متضادين مثبتين، فهو طباق إيجاب."},
        {"q": "رب اغفر لي، الأمر هنا يفيد:", "options": ["التهديد", "الدعاء", "الإرشاد", "التمني"], "answer": 1, "exp": "الأمر من الأدنى إلى الأعلى يفيد الدعاء."},
    ],
    "أدب": [
        {"q": "العباس بن الأحنف من شعراء:", "options": ["الشعر الوطني", "الغزل العذري العباسي", "الرومانتيكية", "الأندلس"], "answer": 1, "exp": "العباس بن الأحنف من أبرز شعراء الغزل العذري في العصر العباسي."},
        {"q": "من أعلام الأدب الأندلسي:", "options": ["العقاد", "ابن زيدون", "شوقي", "الأبنودي"], "answer": 1, "exp": "ابن زيدون من أشهر أعلام الأدب الأندلسي."},
        {"q": "الرومانتيكية تعتمد على:", "options": ["العقل فقط", "المشاعر والخيال", "القواعد النحوية", "السخرية السياسية"], "answer": 1, "exp": "الرومانتيكية تعتمد على المشاعر الذاتية والخيال والطبيعة."},
        {"q": "من شعراء الشعر الوطني:", "options": ["أبو نواس", "حافظ إبراهيم", "ابن حزم", "المازني"], "answer": 1, "exp": "حافظ إبراهيم من أشهر شعراء الشعر الوطني."},
        {"q": "بنية المقال هي:", "options": ["عنوان فقط", "مقدمة وعرض وخاتمة", "حوار ونهاية", "أبيات فقط"], "answer": 1, "exp": "المقال يتكون من مقدمة وعرض وخاتمة."},
    ],
    "نصوص": [
        {"q": "حب ووفاء يدور حول:", "options": ["الحرب", "الحب الصادق والوفاء", "الهجرة", "الهوية"], "answer": 1, "exp": "النص يتحدث عن الحب الصادق والوفاء رغم البعد."},
        {"q": "عتاب اللغة يقوم على:", "options": ["التشخيص", "الطباق فقط", "السجع فقط", "المدح"], "answer": 0, "exp": "صوّر اللغة كإنسان يعاتب أبناءه، وهذا تشخيص."},
        {"q": "غودوا إلى مصر يستخدم:", "options": ["نداء وأمر وتكرار", "جناس فقط", "قصر فقط", "تصريع فقط"], "answer": 0, "exp": "النص يوظف النداء والأمر والتكرار للتأثير."},
        {"q": "الغرض من عتاب اللغة هو:", "options": ["السخرية", "الدعوة للاعتزاز بالعربية", "وصف الطبيعة", "المدح"], "answer": 1, "exp": "النص يدعو للاعتزاز باللغة العربية وعدم إهمالها."},
    ],
    "نحو": [
        {"q": "من صيغ التعجب القياسية:", "options": ["ما أفعلَه", "افعلْ", "ليس إلا", "إنما"], "answer": 0, "exp": "الصيغة الأولى لأسلوب التعجب هي: ما أفعلَه!"},
        {"q": "نحن العربَ نكرم الضيف. العربَ هنا:", "options": ["فاعل", "مختص منصوب", "خبر", "مفعول مطلق"], "answer": 1, "exp": "العربَ مختص منصوب بفعل محذوف تقديره أخص أو أعني."},
        {"q": "هيهاتَ من أسماء الأفعال:", "options": ["المضارعة", "الماضية", "الأمرية", "الناسخة"], "answer": 1, "exp": "هيهات من أسماء الأفعال الماضية بمعنى بَعُد."},
        {"q": "لا طالبَ كسول. اسم لا هنا:", "options": ["مبني على الفتح", "مرفوع", "مجرور", "مبني على الكسر"], "answer": 0, "exp": "اسم لا المفرد يبنى على الفتح."},
        {"q": "من شروط لا النافية للجنس:", "options": ["أن يكون اسمها معرفة", "ألا يفصل بينها وبين اسمها فاصل", "أن تسبق بحرف جر", "أن يكون خبرها فعلًا فقط"], "answer": 1, "exp": "يشترط ألا يفصل بينها وبين اسمها فاصل."},
    ],
    "تعبير": [
        {"q": "من عناصر التقرير:", "options": ["الوزن والقافية", "عنوان وجهة ومقدمة وعرض وخاتمة", "التورية فقط", "الاستفهام فقط"], "answer": 1, "exp": "التقرير الوظيفي له عناصر محددة منها العنوان والجهة والمقدمة والعرض والخاتمة."},
        {"q": "التعبير الإبداعي يعتمد على:", "options": ["أفكار مترابطة وخاتمة مؤثرة", "إجابات قصيرة فقط", "جداول", "أرقام"], "answer": 0, "exp": "التعبير الإبداعي يحتاج مقدمة جذابة وأفكارًا مترابطة وخاتمة مؤثرة."},
        {"q": "اللغة المناسبة للتعبير الوظيفي:", "options": ["العامية", "الفصحى الرسمية", "الرموز فقط", "اللهجات"], "answer": 1, "exp": "التعبير الوظيفي يحتاج لغة فصيحة رسمية واضحة."},
    ],
    "قصة": [
        {"q": "مؤلف وا إسلاماه هو:", "options": ["جبران", "علي أحمد باكثير", "طه حسين", "شوقي"], "answer": 1, "exp": "مؤلف وا إسلاماه هو علي أحمد باكثير."},
        {"q": "الحدث التاريخي الأبرز في الرواية:", "options": ["فتح الأندلس", "عين جالوت", "حرب أكتوبر", "الهجرة"], "answer": 1, "exp": "الرواية تبلغ ذروتها في معركة عين جالوت."},
        {"q": "دلالة عنوان وا إسلاماه:", "options": ["ندبة واستغاثة", "مدح", "هجاء", "فخر"], "answer": 0, "exp": "العنوان يحمل معنى الندبة والاستغاثة للإسلام."},
        {"q": "من شخصيات الرواية:", "options": ["قطز وبيبرس", "العقاد والمازني", "ابن زيدون وابن حزم", "شوقي وحافظ"], "answer": 0, "exp": "من أبرز شخصيات الرواية: قطز وبيبرس وأيبك وأيدكين."},
        {"q": "الرسالة العامة للرواية:", "options": ["اللهو", "الوحدة تقود للنصر", "الانعزال", "الترف"], "answer": 1, "exp": "الرواية تؤكد أن الوحدة والتضحية تقودان للنصر."},
    ],
}

ICONS = {"قراءة": "📖", "بلاغة": "🌸", "أدب": "📜", "نصوص": "📝", "نحو": "🔤", "تعبير": "💬", "قصة": "📚"}
chat_histories = {}

def main_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 الملخصات", callback_data="sum_menu"), InlineKeyboardButton("❓ بنك الأسئلة", callback_data="q_menu")],
        [InlineKeyboardButton("🎯 اختبار عشوائي", callback_data="quiz_random"), InlineKeyboardButton("📊 المواد", callback_data="subjects")],
        [InlineKeyboardButton("ℹ️ عن البوت", callback_data="about")],
    ])

def back_main_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🏠 الرئيسية", callback_data="main")]])

def subjects_kb(prefix):
    rows = []
    for subject in SUBJECTS.keys():
        rows.append([InlineKeyboardButton(f"{ICONS.get(subject, '📚')} {subject}", callback_data=f"{prefix}:{subject}")])
    rows.append([InlineKeyboardButton("🏠 الرئيسية", callback_data="main")])
    return InlineKeyboardMarkup(rows)

def lessons_kb(subject):
    rows = []
    for lesson_id in SUBJECTS[subject]:
        rows.append([InlineKeyboardButton(LESSONS[lesson_id]["title"], callback_data=f"lesson:{lesson_id}")])
    rows.append([InlineKeyboardButton("📝 امتحان على المادة", callback_data=f"subject_quiz:{subject}")])
    rows.append([InlineKeyboardButton("🔙 رجوع", callback_data="sum_menu"), InlineKeyboardButton("🏠 الرئيسية", callback_data="main")])
    return InlineKeyboardMarkup(rows)

def lesson_actions_kb(lesson_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 الملخص", callback_data=f"show:{lesson_id}")],
        [InlineKeyboardButton("🧠 اشرحلي أكتر", callback_data=f"explain:{lesson_id}")],
        [InlineKeyboardButton("❓ اختبرني", callback_data=f"lesson_quiz:{lesson_id}")],
        [InlineKeyboardButton("🔙 رجوع", callback_data=f"subject_from_lesson:{lesson_id}"), InlineKeyboardButton("🏠 الرئيسية", callback_data="main")],
    ])

def quiz_options_kb(options, prefix):
    rows = [[InlineKeyboardButton(opt, callback_data=f"{prefix}:{i}")] for i, opt in enumerate(options)]
    rows.append([InlineKeyboardButton("🏁 إنهاء الاختبار", callback_data=f"{prefix}:finish")])
    return InlineKeyboardMarkup(rows)

def result_text(score, total):
    pct = int((score / total) * 100) if total else 0
    grade = "🏆 ممتاز جدًا" if pct >= 90 else "🥇 جيد جدًا" if pct >= 75 else "🥈 جيد" if pct >= 60 else "🥉 مقبول" if pct >= 50 else "📚 راجع الملخصات"
    bar = "🟩" * (pct // 10) + "⬜" * (10 - (pct // 10))
    return f"🎉 *انتهى الاختبار!*\n━━━━━━━━━━━━━━━━━━━━━━\n✅ الصحيح: *{score}/{total}*\n📊 النسبة: *{pct}%*\n{bar}\n🎖️ *{grade}*"

def build_quiz_pool(subject=None, lesson_id=None):
    if lesson_id:
        lesson_subject = LESSONS[lesson_id]["subject"]
        pool = QUESTIONS.get(lesson_subject, []).copy()
        random.shuffle(pool)
        return pool[:5]
    if subject:
        pool = QUESTIONS.get(subject, []).copy()
        random.shuffle(pool)
        return pool[: min(7, len(pool))]
    pool = []
    for qs in QUESTIONS.values():
        pool.extend(qs)
    random.shuffle(pool)
    return pool[:10]

async def send_current_question(q, ctx):
    quiz = ctx.user_data.get("quiz", {})
    index = quiz.get("index", 0)
    questions = quiz.get("questions", [])
    if index >= len(questions):
        await finish_quiz(q, ctx)
        return
    item = questions[index]
    title = quiz.get("title", "الاختبار")
    await q.edit_message_text(
        f"📝 *{title}*\nالسؤال *{index + 1}* من *{len(questions)}*\n━━━━━━━━━━━━━━━━━━━━━━\n{item['q']}",
        parse_mode="Markdown",
        reply_markup=quiz_options_kb(item["options"], "quiz"),
    )

async def finish_quiz(q, ctx):
    quiz = ctx.user_data.get("quiz", {})
    score = quiz.get("score", 0)
    total = len(quiz.get("questions", []))
    await q.edit_message_text(
        result_text(score, total),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 اختبار جديد", callback_data="q_menu"), InlineKeyboardButton("📋 الملخصات", callback_data="sum_menu")],
            [InlineKeyboardButton("🏠 الرئيسية", callback_data="main")]
        ]),
    )
    ctx.user_data.pop("quiz", None)

async def explain_lesson(update_or_query, lesson_id, edit=False):
    lesson = LESSONS[lesson_id]
    prompt = f"{lesson['title']}\nملخص الدرس: {lesson['summary']}\nاشرح هذا الدرس لطالب ثاني ثانوي شرحًا واضحًا ومنظمًا في 6 نقاط قصيرة، ثم اختم بسؤال تحفيزي."
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
            max_tokens=350,
            temperature=0.5,
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        logger.error("Explain error: %s", e)
        answer = "حصلت مشكلة بسيطة في الشرح الآن. جرّب بعد لحظة."
    if edit:
        await update_or_query.edit_message_text(answer, reply_markup=lesson_actions_kb(lesson_id))
    else:
        await update_or_query.reply_text(answer, reply_markup=lesson_actions_kb(lesson_id))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = "🎓 *أهلاً بك في بوت اللغة العربية*\n━━━━━━━━━━━━━━━━━━━━━━\n📚 الصف الثاني الثانوي | الترم الثاني 2026\n✨ ملخصات + شرح + اختبارات + تقييم فوري\n━━━━━━━━━━━━━━━━━━━━━━\nاختر من القائمة:"
    await update.message.reply_text(welcome, parse_mode="Markdown", reply_markup=main_kb())

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    if data == "main":
        await q.edit_message_text("🎓 *القائمة الرئيسية*\nاختر اللي يناسبك 👇", parse_mode="Markdown", reply_markup=main_kb())
    elif data == "about":
        total_summaries = len(LESSONS)
        total_questions = sum(len(v) for v in QUESTIONS.values())
        await q.edit_message_text(
            f"ℹ️ *عن البوت*\n━━━━━━━━━━━━━━━━━━━━━━\n📚 الملخصات: *{total_summaries}*\n❓ الأسئلة: *{total_questions}*\n🧠 شرح AI حسب الدرس\n🎯 اختبارات للمادة أو للدرس\n📊 تقييم فوري في نهاية الاختبار",
            parse_mode="Markdown",
            reply_markup=back_main_kb(),
        )
    elif data == "subjects":
        lines = [f"{ICONS.get(subject, '📚')} *{subject}*: {len(lesson_ids)} دروس" for subject, lesson_ids in SUBJECTS.items()]
        await q.edit_message_text("📊 *المواد المتاحة*\n━━━━━━━━━━━━━━━━━━━━━━\n" + "\n".join(lines), parse_mode="Markdown", reply_markup=back_main_kb())
    elif data == "sum_menu":
        await q.edit_message_text("📋 *اختر المادة لعرض الدروس*", parse_mode="Markdown", reply_markup=subjects_kb("sum_subject"))
    elif data.startswith("sum_subject:"):
        subject = data.split(":", 1)[1]
        await q.edit_message_text(f"{ICONS.get(subject, '📚')} *{subject}*\nاختر الدرس:", parse_mode="Markdown", reply_markup=lessons_kb(subject))
    elif data.startswith("lesson:"):
        lesson_id = data.split(":", 1)[1]
        lesson = LESSONS[lesson_id]
        await q.edit_message_text(f"{lesson['title']}\n━━━━━━━━━━━━━━━━━━━━━━\nاختر المطلوب:", reply_markup=lesson_actions_kb(lesson_id))
    elif data.startswith("show:"):
        lesson_id = data.split(":", 1)[1]
        lesson = LESSONS[lesson_id]
        await q.edit_message_text(f"{lesson['title']}\n━━━━━━━━━━━━━━━━━━━━━━\n{lesson['summary']}", reply_markup=lesson_actions_kb(lesson_id))
    elif data.startswith("explain:"):
        lesson_id = data.split(":", 1)[1]
        await q.edit_message_text("⏳ جاري تجهيز شرح مرتب...")
        await explain_lesson(q, lesson_id, edit=True)
    elif data.startswith("subject_from_lesson:"):
        lesson_id = data.split(":", 1)[1]
        subject = LESSONS[lesson_id]["subject"]
        await q.edit_message_text(f"{ICONS.get(subject, '📚')} *{subject}*\nاختر الدرس:", parse_mode="Markdown", reply_markup=lessons_kb(subject))
    elif data == "q_menu":
        await q.edit_message_text("❓ *اختر المادة لبدء الاختبار*", parse_mode="Markdown", reply_markup=subjects_kb("quiz_subject"))
    elif data.startswith("quiz_subject:"):
        subject = data.split(":", 1)[1]
        context.user_data["quiz"] = {"questions": build_quiz_pool(subject=subject), "index": 0, "score": 0, "title": f"اختبار مادة {subject}"}
        await send_current_question(q, context)
    elif data.startswith("subject_quiz:"):
        subject = data.split(":", 1)[1]
        context.user_data["quiz"] = {"questions": build_quiz_pool(subject=subject), "index": 0, "score": 0, "title": f"اختبار مادة {subject}"}
        await send_current_question(q, context)
    elif data.startswith("lesson_quiz:"):
        lesson_id = data.split(":", 1)[1]
        context.user_data["quiz"] = {"questions": build_quiz_pool(lesson_id=lesson_id), "index": 0, "score": 0, "title": f"اختبار {LESSONS[lesson_id]['title']}"}
        await send_current_question(q, context)
    elif data == "quiz_random":
        context.user_data["quiz"] = {"questions": build_quiz_pool(), "index": 0, "score": 0, "title": "اختبار عشوائي شامل"}
        await send_current_question(q, context)
    elif data.startswith("quiz:"):
        action = data.split(":", 1)[1]
        if action == "finish":
            await finish_quiz(q, context)
            return
        quiz = context.user_data.get("quiz")
        if not quiz:
            await q.edit_message_text("الاختبار غير متاح الآن.", reply_markup=back_main_kb())
            return
        index = quiz["index"]
        current = quiz["questions"][index]
        selected = int(action)
        correct = current["answer"]
        feedback = f"✅ *إجابة صحيحة!*\n{current['exp']}" if selected == correct else f"❌ *إجابة غير صحيحة*\n{current['exp']}"
        if selected == correct:
            quiz["score"] += 1
        quiz["index"] += 1
        context.user_data["quiz"] = quiz
        if quiz["index"] >= len(quiz["questions"]):
            await q.edit_message_text(feedback + "\n\nاضغط التالي لعرض النتيجة.", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏁 النتيجة", callback_data="quiz:finish")]]))
        else:
            await q.edit_message_text(feedback, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("➡️ السؤال التالي", callback_data="quiz_next")]]))
    elif data == "quiz_next":
        await send_current_question(q, context)
    elif data == "new_chat":
        user_id = update.effective_user.id
        chat_histories.pop(user_id, None)
        await q.edit_message_text("✅ تم بدء محادثة جديدة.\nاكتب سؤالك الآن 👇", reply_markup=back_main_kb())

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_msg = update.message.text.strip()
    if not user_msg:
        return
    if user_id not in chat_histories:
        chat_histories[user_id] = []
    if user_msg.lower() in {"menu", "القائمة", "ابدأ", "start"}:
        await start(update, context)
        return
    chat_histories[user_id].append({"role": "user", "content": user_msg})
    if len(chat_histories[user_id]) > 10:
        chat_histories[user_id] = chat_histories[user_id][-10:]
    wait = await update.message.reply_text("⚡")
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, *chat_histories[user_id]],
            max_tokens=350,
            temperature=0.5,
        )
        answer = response.choices[0].message.content.strip()
        chat_histories[user_id].append({"role": "assistant", "content": answer})
        await wait.delete()
        await update.message.reply_text(answer, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 محادثة جديدة", callback_data="new_chat"), InlineKeyboardButton("🏠 الرئيسية", callback_data="main")]]))
    except Exception as e:
        logger.error("OpenAI error: %s", e)
        await wait.delete()
        await update.message.reply_text("⚠️ حدث خطأ، حاول مرة أخرى.", reply_markup=back_main_kb())

def main():
    logger.info("✅ Arabic bot is running...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("menu", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
