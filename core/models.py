# این فایل مدل‌های DB رو تعریف می‌کنه. چرا؟ برای ذخیره اطلاعات شخصی و پاسخ‌ها در SQLite.
from django.db import models
from django.contrib.auth.models import User  # لینک به کاربر (اختیاری برای لاگین).
from django.core.exceptions import ValidationError  # برای validation.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  # لینک به کاربر – چرا؟ برای future auth.
    first_name = models.CharField(max_length=100)  # نام – max_length برای محدودیت.
    last_name = models.CharField(max_length=100)  # نام خانوادگی.
    email = models.CharField(max_length=254)  # ایمیل.
    country = models.CharField(max_length=100)  # کشور.
    city = models.CharField(max_length=100)  # شهر.
    age = models.IntegerField()  # سن – validation در clean().
    relationship_duration = models.CharField(max_length=50, default='0 روز')  # مدت رابطه – CharField برای string مثل "24 سال" – رفع ValueError.
    mbti_type = models.CharField(max_length=4, blank=True)  # MBTI – ۴ حرف، blank برای اختیاری.
    answers = models.JSONField(default=list)  # پاسخ‌های پرسشنامه – JSON برای لیست ۵۹ امتیاز.
    result = models.FloatField(default=0.0)  # ریسک طلاق – از مدل ML.
    created_at = models.DateTimeField(auto_now_add=True)  # زمان ذخیره – چرا؟ برای log.

    def __str__(self):  # نمایش در admin – چرا؟ خوانا.
        return f"{self.first_name} {self.last_name} ({self.email})"

    def clean(self):  # validation کلی – چرا؟ چک سن/مدت در DB.
        if self.age < 18:
            raise ValidationError({'age': 'سن باید حداقل ۱۸ سال باشد.'})
        # relationship_duration stringه – validation ساده (نه منفی).
        if self.relationship_duration and 'سال' in self.relationship_duration and int(self.relationship_duration.split()[0]) < 0:
            raise ValidationError({'relationship_duration': 'مدت رابطه نمی‌تواند منفی باشد.'})