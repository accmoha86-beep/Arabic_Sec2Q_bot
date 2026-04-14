# 🤖 Arabic_Sec2Q_bot - دليل التشغيل الكامل

## هيكل المشروع
```
Arabic_Sec2Q_bot/
│
├── main.py                  ← نقطة البداية (شغِّل هذا)
├── config.py                ← التوكن والإعدادات
├── requirements.txt         ← المكتبات المطلوبة
│
├── data/
│   ├── summaries.py         ← كل الملخصات
│   └── questions.py         ← بنك الأسئلة الكامل
│
└── handlers/
    ├── menu_handler.py      ← القوائم الرئيسية
    ├── summary_handler.py   ← معالج الملخصات
    └── quiz_handler.py      ← معالج الاختبارات
```

---

## 🚀 التشغيل خطوة بخطوة

### الخطوة ١: تثبيت Python
تأكَّد أن Python 3.10+ مثبَّت:
```bash
python --version
```

### الخطوة ٢: تثبيت المكتبات
```bash
pip install -r requirements.txt
```

### الخطوة ٣: تشغيل البوت
```bash
python main.py
```

---

## ✅ التحقُّق من التشغيل
عند التشغيل الناجح ستظهر:
```
تشغيل بوت اللغة العربية - @Arabic_Sec2Q_bot
البوت يعمل الآن...
```

افتح تيليجرام → ابحث عن @Arabic_Sec2Q_bot → اكتب /start

---

## 📊 إحصائيات المحتوى

| المجال | عدد الملخصات | عدد الأسئلة |
|--------|-------------|------------|
| القراءة | 3 دروس | 7 أسئلة |
| البلاغة | 3 مجالات | 9 أسئلة |
| الأدب | 5 موضوعات | 7 أسئلة |
| النصوص | 3 نصوص | 3 أسئلة |
| النحو | 4 دروس | 8 أسئلة |
| التعبير | 2 موضوعات | 2 أسئلة |
| القصة | قصة كاملة | 6 أسئلة |
| **المجموع** | **21 ملخصاً** | **42 سؤالاً** |

---

## ➕ إضافة أسئلة جديدة

في ملف `data/questions.py` أضف في القاموس المناسب:
```python
{
    "q": "نص السؤال؟",
    "options": ["أ) الخيار الأول", "ب) الثاني", "ج) الثالث", "د) الرابع"],
    "answer": "أ",   # حرف الإجابة
    "explanation": "سبب الإجابة الصحيحة"
}
```

---

## ➕ إضافة ملخص جديد

في ملف `data/summaries.py`:
```python
"مفتاح_جديد": {
    "title": "📖 عنوان الدرس",
    "content": "محتوى الملخص..."
}
```
ثم أضف زراً له في `handlers/summary_handler.py` في `CATEGORY_MAP`.

---

## ☁️ رفع البوت للسيرفر (24/7)

### Railway.app (موصى به - مجاني):
1. سجِّل على railway.app
2. New Project → Deploy from GitHub
3. ارفع الملفات على GitHub أولاً
4. أضف متغيَّر البيئة: `PYTHONUNBUFFERED=1`
5. Start Command: `python main.py`

### Render.com:
1. New Web Service
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `python main.py`
