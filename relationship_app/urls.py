"""
URL configuration for relationship_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# این فایل URLهای پروژه رو تعریف می‌کنه. چرا؟ برای مسیردهی درخواست‌ها به viewها.
from django.contrib import admin  # import برای پنل مدیریت Django.
from django.urls import path
from core import views  # import viewهای اپ core.

urlpatterns = [  # لیست واحد – همه pathها رو اینجا بگذار.
    path('admin/', admin.site.urls),  # پنل ادمین در /admin/.
    path('', views.welcome_view, name='welcome'),  # صفحه اصلی (/) به welcome.
    path('user_info/', views.user_info_view, name='user_info'),  # جدید: /user_info/ به فرم سوالات – name برای {% url 'user_info' %}.
    path('predict/', views.predict_view, name='predict'),  # پیش‌بینی.
]
