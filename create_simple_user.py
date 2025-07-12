import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduate_system.settings')
import django
django.setup()

from django.contrib.auth.models import User

if not User.objects.filter(username='test').exists():
    User.objects.create_user('test', password='test1234')
    print('User created: test / test1234')
else:
    print('User already exists: test') 