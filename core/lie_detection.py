# این فایل تابع تشخیص دروغ رو مدیریت می‌کنه. چرا؟ برای چک consistency پاسخ‌ها (۵ سوال چک).
import numpy as np

def detect_lie(answers):
    # answers: لیست ۵۹ عنصر (۵۴ اصلی + ۵ چک)
    # pairs: جفت‌های چک (مثال: سوال ۱ و ۵۵ معکوس هم – فرض scale ۰-۴)
    # معکوس: اگر سوال مثبت امتیاز ۴ باشه، معکوس باید ۰ باشه (۴ - امتیاز)
    inconsistencies = 0
    pairs = [(0, 54), (10, 55), (20, 56), (30, 57), (40, 58)]  # ایندکس‌ها ۰-based (۵ جفت)
    for pos, neg in pairs:
        expected_neg = 4 - answers[pos]  # معکوس امتیاز مثبت
        if abs(answers[neg] - expected_neg) > 1:  # اگر تفاوت >۱، ناسازگار
            inconsistencies += 1
    lie_risk = (inconsistencies / len(pairs)) * 100  # درصد ریسک (۰-۱۰۰)
    return lie_risk

# sample_answers = np.random.randint(0, 5, 59)
# print(f'ریسک دروغ: {detect_lie(sample_answers):.2f}%')