import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduate_system.settings')
import django
django.setup()

from django.contrib.auth.models import User

try:
    u = User.objects.get(username='test')
    print('is_active:', u.is_active)
    print('is_superuser:', u.is_superuser)
    print('is_staff:', u.is_staff)
    print('password correct:', u.check_password('test1234'))
except User.DoesNotExist:
    print('User test does not exist') 