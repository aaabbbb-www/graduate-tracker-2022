# نظام تتبع الخريجين - Graduate Tracker System

نظام شامل لإدارة ومتابعة الخريجين مبني باستخدام Django مع قاعدة بيانات MySQL، يتضمن نظام استبيانات تفاعلي وتقارير مفصلة.

## المميزات الرئيسية

### 🎓 إدارة الخريجين
- تسجيل وإدارة بيانات الخريجين الشخصية والأكاديمية
- تتبع حالة التوظيف والمسار المهني
- إدارة معلومات التواصل والتحديثات

### 📊 نظام الاستبيانات
- إنشاء استبيانات مخصصة بأنواع أسئلة متعددة
- واجهة تفاعلية وجذابة لأخذ الاستبيانات
- إرسال الاستبيانات عبر البريد الإلكتروني
- تتبع معدلات الاستجابة والإكمال

### 📈 التقارير والإحصائيات
- تقارير شاملة عن حالة الخريجين
- إحصائيات التوظيف حسب التخصص والسنة
- رسوم بيانية تفاعلية
- تصدير التقارير بصيغة PDF

### 👥 إدارة المستخدمين
- نظام صلاحيات متقدم
- أدوار مختلفة (مدير، موظف، خريج)
- تسجيل دخول آمن

### 🎨 واجهة مستخدم متقدمة
- تصميم عصري ومتجاوب
- دعم اللغة العربية بالكامل
- تأثيرات بصرية وتفاعلية
- تجربة مستخدم محسنة

## متطلبات النظام

### البرمجيات المطلوبة
- Python 3.12.0 أو أحدث
- MySQL 8.0 أو أحدث
- Node.js (للأدوات الإضافية)

### المتطلبات الأساسية
```bash
pip install -r requirements.txt
```

## التثبيت والإعداد

### 1. استنساخ المشروع
```bash
git clone <repository-url>
cd graduate_tracker
```

### 2. إنشاء البيئة الافتراضية
```bash
python -m venv venv
source venv/bin/activate  # على Linux/Mac
# أو
venv\Scripts\activate  # على Windows
```

### 3. تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

### 4. إعداد قاعدة البيانات

#### إنشاء قاعدة البيانات في MySQL
```sql
CREATE DATABASE graduate_tracker CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'graduate_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON graduate_tracker.* TO 'graduate_user'@'localhost';
FLUSH PRIVILEGES;
```

#### تحديث إعدادات قاعدة البيانات
في ملف `graduate_system/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'graduate_tracker',
        'USER': 'graduate_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

### 5. تطبيق الهجرات
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. إنشاء مستخدم إداري
```bash
python manage.py createsuperuser
```

### 7. جمع الملفات الثابتة
```bash
python manage.py collectstatic
```

### 8. تشغيل الخادم
```bash
python manage.py runserver
```

الآن يمكنك الوصول للنظام عبر: `http://localhost:8000`

## هيكل المشروع

```
graduate_tracker/
├── manage.py
├── requirements.txt
├── README.md
├── graduate_system/          # إعدادات المشروع الرئيسية
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── graduates/                # تطبيق إدارة الخريجين
│   ├── models.py            # نماذج البيانات
│   ├── views.py             # العروض
│   ├── forms.py             # النماذج
│   ├── urls.py              # الروابط
│   └── admin.py             # إعدادات الإدارة
├── surveys/                  # تطبيق الاستبيانات
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
├── accounts/                 # تطبيق إدارة المستخدمين
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
├── reports/                  # تطبيق التقارير
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── templates/                # قوالب HTML
│   ├── base.html
│   ├── welcome.html
│   ├── dashboard.html
│   ├── accounts/
│   ├── graduates/
│   ├── surveys/
│   └── reports/
└── static/                   # الملفات الثابتة
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## الاستخدام

### 1. الوصول للوحة الإدارة
- اذهب إلى `http://localhost:8000/admin/`
- سجل دخولك بحساب المدير

### 2. إضافة خريجين
- من لوحة الإدارة أو واجهة النظام
- أدخل البيانات الشخصية والأكاديمية
- حدد حالة التوظيف

### 3. إنشاء استبيان
- اذهب إلى قسم الاستبيانات
- انقر على "إنشاء استبيان جديد"
- أضف الأسئلة والخيارات
- حدد تاريخ البداية والنهاية

### 4. إرسال الاستبيان
- اختر الاستبيان المطلوب
- حدد المستقبلين (جميع الخريجين أو مجموعة محددة)
- اكتب نص الرسالة
- انقر على "إرسال"

### 5. عرض التقارير
- اذهب إلى قسم التقارير
- اختر نوع التقرير المطلوب
- حدد الفترة الزمنية
- اعرض أو صدر التقرير

## التخصيص والتطوير

### إضافة حقول جديدة للخريجين
1. عدل ملف `graduates/models.py`
2. أضف الحقل الجديد
3. قم بإنشاء هجرة جديدة:
```bash
python manage.py makemigrations graduates
python manage.py migrate
```

### تخصيص التصميم
- عدل ملف `static/css/style.css` للتصميم
- عدل ملف `static/js/main.js` للتفاعلية
- عدل القوالب في مجلد `templates/`

### إضافة أنواع أسئلة جديدة
1. عدل ملف `surveys/models.py`
2. أضف النوع الجديد في `QUESTION_TYPES`
3. عدل القوالب لدعم النوع الجديد

## الأمان

### إعدادات الأمان المطبقة
- حماية CSRF
- تشفير كلمات المرور
- تحديد الصلاحيات
- تنظيف البيانات المدخلة
- حماية من SQL Injection

### نصائح أمنية إضافية
- استخدم HTTPS في الإنتاج
- قم بتحديث Django بانتظام
- استخدم كلمات مرور قوية
- فعل النسخ الاحتياطي

## النشر في الإنتاج

### 1. إعدادات الإنتاج
```python
# في settings.py
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
```

### 2. خادم الويب
- استخدم Nginx + Gunicorn
- أو Apache + mod_wsgi

### 3. قاعدة البيانات
- استخدم MySQL أو PostgreSQL
- فعل النسخ الاحتياطي التلقائي

## استكشاف الأخطاء

### مشاكل شائعة وحلولها

#### خطأ في الاتصال بقاعدة البيانات
```bash
# تأكد من تشغيل MySQL
sudo systemctl start mysql

# تأكد من صحة بيانات الاتصال في settings.py
```

#### خطأ في الهجرات
```bash
# إعادة تعيين الهجرات
python manage.py migrate --fake-initial
```

#### مشاكل في الملفات الثابتة
```bash
# جمع الملفات الثابتة مرة أخرى
python manage.py collectstatic --clear
```

## المساهمة

نرحب بالمساهمات! يرجى:
1. عمل Fork للمشروع
2. إنشاء فرع جديد للميزة
3. إجراء التغييرات
4. إرسال Pull Request

## الترخيص

هذا المشروع مرخص تحت رخصة MIT - انظر ملف LICENSE للتفاصيل.

## الدعم

للحصول على الدعم:
- افتح Issue في GitHub
- راسلنا على البريد الإلكتروني
- راجع الوثائق

## الإصدارات

### الإصدار 1.0.0
- إدارة الخريجين الأساسية
- نظام الاستبيانات
- التقارير الأساسية
- واجهة المستخدم

### خطط مستقبلية
- تطبيق الهاتف المحمول
- تكامل مع وسائل التواصل الاجتماعي
- ذكاء اصطناعي للتحليلات
- API متقدم

---

**تم تطوير هذا النظام بواسطة فريق تطوير متخصص لخدمة مؤسسات التعليم العالي**

