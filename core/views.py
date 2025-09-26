# این فایل viewهای Django رو مدیریت می‌کنه. چرا؟ برای پردازش درخواست‌ها، فرم‌ها، و پیش‌بینی ML.
from django.shortcuts import render  # برای رندر templateها.
from django.contrib import messages  # برای پیام‌های موفقیت/خطا.
import tensorflow as tf  # برای لود مدل NN.
import joblib  # برای لود scaler.
import plotly.express as px  # برای نمودار.
from .forms import UserInfoForm, QuestionnaireForm  # import هر دو فرم.
from .lie_detection import detect_lie  # import تابع تشخیص دروغ.
from .models import UserProfile  # import مدل DB.
import numpy as np  # برای append به array.

def welcome_view(request):
    # view صفحه خوش‌آمدگویی – چرا؟ برای راهنمایی قبل فرم.
    return render(request, 'core/welcome.html')  # رندر welcome.html – ساده.
def user_info_view(request):
    # این view فرم اطلاعات شخصی رو نمایش/پردازش می‌کنه. چرا؟ برای جمع‌آوری داده‌های اولیه کاربر.
    if request.method == 'POST':
        form = UserInfoForm(request.POST)
        if form.is_valid():
            # ذخیره در DB – چرا؟ دائمی.
            profile = UserProfile(
                first_name=form.cleaned_data.get('first_name', ''),
                last_name=form.cleaned_data.get('last_name', ''),
                email=form.cleaned_data.get('email', ''),
                country=form.cleaned_data.get('country', ''),
                city=form.cleaned_data.get('city', ''),
                age=form.cleaned_data.get('age', 0),
                relationship_duration=form.cleaned_data.get('relationship_duration', 0),
                mbti_type=form.cleaned_data.get('mbti_type', ''),  # MBTI ذخیره – جدید.
            )
            profile.save()  # ذخیره در DB.
            request.session['profile_id'] = profile.id  # ID برای predict.
            messages.success(request, 'اطلاعات ذخیره شد!')

            # QuestionnaireForm بساز و پاس بده.
            questionnaire_form = QuestionnaireForm()
            return render(request, 'core/questionnaire.html', {'form': questionnaire_form})
    else:
        form = UserInfoForm()
    return render(request, 'core/user_info.html', {'form': form})

def predict_view(request):
    # این view پیش‌بینی رو مدیریت می‌کنه. چرا؟ برای محاسبه ریسک با NN و نمایش با نمودار.
    if request.method == 'POST':
        try:
            # جمع‌آوری answers (لیست 59) از فیلدهای q1 تا q59.
            answers = [int(request.POST.get(f'q{i}', 0)) for i in range(1, 60)]
            if len(answers) != 59:
                raise ValueError('تعداد پاسخ‌ها کامل نیست.')
            main_answers = answers[:54]
            lie_risk = detect_lie(answers)

            # لود مدل و scaler – path به core/.
            model = tf.keras.models.load_model('core/divorce_model.h5')  # path نسبی به core/ – 
            scaler = joblib.load('core/scaler.pkl')
            scaled = scaler.transform([main_answers])
            prob = float(model.predict(scaled, verbose=0)[0][0]) * 100
            print(f"Debug: prob = {prob}")  # log prob – console ببین.
            
            # نتیجه متن.
            result_text = [
                f'درصد موفق بودن رابطه شما: {prob:.2f}%',
                f'میزان پاسخ‌های غیرواقعی (دروغ):  {lie_risk:.2f}%'
            ]
            if 'country' in request.session:
                result_text.append(f'در مقایسه با زوج‌های {request.session["country"]}: متوسط ریسک')
            
            # فیدبک شخصی‌سازی‌شده بر اساس درصد موفقیت (100 - prob).
            success_rate = 100 - prob
            feedback = 'بهتره روی اعتماد و حل تعارض کار کنید. مشاوره پیشنهاد می‌شه. نکته‌های مفید: ۱. زود کمک بگیرید (مشاوره). ۲. انتقادها رو کنترل کنید. ۳. مهارت‌های حل اختلاف رو یاد بگیرید.'
            if success_rate > 70:
                feedback ='رابطه‌تون متوسطه. کمی روی اعتماد و درک متقابل کار کنید. نکته‌های مفید: ۱. بحث‌ها رو با آرامش شروع کنید. ۲. احساسات همدیگه رو درک کنید. ۳. زمان‌هایی برای گفتگوی عمیق اختصاص بدید.'
            elif 50 <= success_rate <= 70:
                feedback = 'رابطه‌تون خیلی قویه! ادامه بدید و روی ارتباط عاطفی تمرکز کنید. نکته‌های مفید: ۱. ارتباط باز و صادقانه رو حفظ کنید. ۲. زمان کیفیت‌دار با هم بگذرانید. ۳. قدردانی رو فراموش نکنید.'
            else:
                feedback =  'رابطه‌تون بی‌نظیره! این سطح از موفقیت واقعاً استثناییه. نکته‌های مفید: ۱. این تعادل رو حفظ کنید و از لحظات با هم لذت ببرید. ۲. تجربه‌هاتون رو با دیگران به اشتراک بگذارید. ۳. عشق و حمایت رو همچنان تقویت کنید.'
            
            # فیدبک MBTI – از profile بگیر.
            mbti_feedback = ''
            profile_id = request.session.get('profile_id')
            if profile_id:
                profile = UserProfile.objects.get(id=profile_id)
                mbti_type = profile.mbti_type  # MBTI کاربر.
                if mbti_type:  # اگر MBTI انتخاب شده.
                    # دیکشنری کامل سازگاری MBTI – ۱۶ تایپ، هر کدوم ۳ سازگار با success_rate و tip بر اساس روانشناسی.
                    compatibility = {
                        'INTJ': {'compatible': ['ENFP', 'ENTP', 'INFJ'], 'success_rate': 85, 'tip': 'به عنوان INTJ، با ENFP رابطه بهتری دارید – تمرکز روی خلاقیت و احساسات.'},
                        'INTP': {'compatible': ['ENTJ', 'ESTJ', 'ENFJ'], 'success_rate': 80, 'tip': 'به عنوان INTP، با ENTJ سازگارید – بحث‌های منطقی رو لذت ببرید.'},
                        'ENTJ': {'compatible': ['INTP', 'INFP', 'ENTP'], 'success_rate': 88, 'tip': 'به عنوان ENTJ، با INTP تعادل خوبی دارید – استراتژی و ایده‌پردازی.'},
                        'ENTP': {'compatible': ['INTJ', 'INFJ', 'ENFJ'], 'success_rate': 82, 'tip': 'به عنوان ENTP، با INTJ هم‌خوانی دارید – نوآوری و برنامه‌ریزی.'},
                        'INFJ': {'compatible': ['ENFP', 'ENTP', 'INTJ'], 'success_rate': 90, 'tip': 'به عنوان INFJ، با ENFP رابطه عمیقی دارید – احساس و بینش.'},
                        'INFP': {'compatible': ['ENFJ', 'ENTJ', 'INFJ'], 'success_rate': 87, 'tip': 'به عنوان INFP، با ENFJ سازگارید – ارزش‌ها و همدلی.'},
                        'ENFJ': {'compatible': ['INFP', 'ISFP', 'INTP'], 'success_rate': 85, 'tip': 'به عنوان ENFJ، با INFP تعادل خوبی دارید – رهبری و خلاقیت.'},
                        'ENFP': {'compatible': ['INTJ', 'INFJ', 'ISTJ'], 'success_rate': 92, 'tip': 'به عنوان ENFP، با INTJ انرژی‌تون رو متعادل کنید – خلاقیت و منطق.'},
                        'ISTJ': {'compatible': ['ESFP', 'ESTP', 'ISFJ'], 'success_rate': 78, 'tip': 'به عنوان ISTJ، با ESFP تنوع رو تجربه کنید – مسئولیت و ماجراجویی.'},
                        'ISFJ': {'compatible': ['ESTP', 'ESFP', 'ISTJ'], 'success_rate': 80, 'tip': 'به عنوان ISFJ، با ESTP هیجان رو اضافه کنید – مراقبت و عمل.'},
                        'ESTJ': {'compatible': ['INTP', 'ISTP', 'ESFJ'], 'success_rate': 82, 'tip': 'به عنوان ESTJ، با INTP ایده‌های نو رو بررسی کنید – ساختار و خلاقیت.'},
                        'ESFJ': {'compatible': ['ISTP', 'INFP', 'ESTJ'], 'success_rate': 85, 'tip': 'به عنوان ESFJ، با ISTP استقلال رو متعادل کنید – جامعه و عمل.'},
                        'ISTP': {'compatible': ['ESFJ', 'ESTJ', 'INTP'], 'success_rate': 79, 'tip': 'به عنوان ISTP، با ESFJ ارتباط رو تقویت کنید – آزادی و مراقبت.'},
                        'ISFP': {'compatible': ['ESTJ', 'ENFJ', 'ESFP'], 'success_rate': 81, 'tip': 'به عنوان ISFP، با ESTJ ساختار رو اضافه کنید – هنر و سازمان.'},
                        'ESTP': {'compatible': ['ISFJ', 'INFJ', 'ENTJ'], 'success_rate': 83, 'tip': 'به عنوان ESTP، با ISFJ ثبات رو تجربه کنید – ماجراجویی و مراقبت.'},
                        'ESFP': {'compatible': ['ISTJ', 'INTJ', 'ISFP'], 'success_rate': 84, 'tip': 'به عنوان ESFP، با ISTJ برنامه‌ریزی رو متعادل کنید – سرگرمی و مسئولیت.'},
                    }
                    
                    if mbti_type in compatibility:
                        comp = compatibility[mbti_type]
                        mbti_feedback = f"تایپ MBTI شما ({mbti_type}): با {comp['compatible'][0]} سازگارتره (موفقیت {comp['success_rate']}%). نکته: {comp['tip']}"
                    else:
                        mbti_feedback = f"تایپ MBTI شما ({mbti_type}): اطلاعات سازگاری در دسترس نیست – تست MBTI رو کامل کنید."
            
            # ذخیره در DB.
            if profile_id:
                profile = UserProfile.objects.get(id=profile_id)
                profile.answers = answers
                profile.result = prob
                profile.save()
            
            # نمودار Plotly.
            fig = px.pie(names=['ناموفق', 'موفقیت'], values=[100 - prob, prob], title='ریسک روابط زوج‌ها', color_discrete_map={'ناموفق': 'green', 'موفقیت': 'red'})
            chart = fig.to_html(full_html=False, include_plotlyjs='cdn')

            return render(request, 'core/result.html', {'results': result_text, 'chart': chart, 'prob': prob, 'feedback': feedback, 'mbti_feedback': mbti_feedback})
        except Exception as e:
            # مدیریت خطا – log و redirect.
            print(f"Predict error: {e}")  # log در console.
            messages.error(request, f'خطا: {str(e)}')
            questionnaire_form = QuestionnaireForm()
            return render(request, 'core/questionnaire.html', {'form': questionnaire_form})
    else:
        questionnaire_form = QuestionnaireForm()
        return render(request, 'core/questionnaire.html', {'form': questionnaire_form})

def welcome_view(request):
    return render(request, 'core/welcome.html')  # رندر welcome.html – ساده.
