from django.db import migrations
from django.contrib.auth.models import User

def create_superuser(apps, schema_editor):
    # Thay thế User bằng custom User model nếu bạn sử dụng
    User = apps.get_model('apartmentapp', 'User')  # Truy cập model User trong migration
    User.objects.create_superuser(
        username='admin1',
        email='admin@example.com',
        password='1234',
        phone='1',
        citizen_card='1'
    )
    User.objects.create_superuser(
        username='admin2',
        email='admin1@example.com',
        password='1234',
        phone='12',
        citizen_card='12323'
    )

class Migration(migrations.Migration):

    dependencies = [
        ('apartmentapp', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]