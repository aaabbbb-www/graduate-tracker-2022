#!/usr/bin/env bash
# exit on error
set -o errexit

# تثبيت الاعتماديات
pip install -r requirements.txt

# جمع الملفات الثابتة
python manage.py collectstatic --no-input

# تطبيق تحديثات قاعدة البيانات
python manage.py migrate
