# Generated by Django 4.2.17 on 2025-01-01 13:53

import apartmentapp.models
import ckeditor.fields
import cloudinary.models
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('full_name', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=15, unique=True)),
                ('date_of_birth', models.DateTimeField(null=True)),
                ('gender', models.BooleanField(default=True)),
                ('citizen_card', models.CharField(max_length=15, unique=True)),
                ('thumbnail', cloudinary.models.CloudinaryField(max_length=255, null=True)),
                ('changed_password', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='CommonNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=100)),
                ('content', ckeditor.fields.RichTextField()),
                ('delivery_method', models.CharField(choices=[('App', 'APP'), ('SMS', 'SMS')], default=apartmentapp.models.DeliveryMethod['APP'], max_length=20)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Fee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MonthlyFee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('amount', models.FloatField(default=0)),
                ('status', models.CharField(choices=[('Pending', 'PENDING'), ('Paid', 'PAID')], default=apartmentapp.models.MonthlyFeeStatus['PENDING'], max_length=20)),
                ('fee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apartmentapp.fee')),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('room_number', models.CharField(max_length=20, unique=True)),
                ('area', models.FloatField(default=0)),
                ('floor', models.IntegerField(default=1)),
                ('status', models.CharField(choices=[('Available', 'AVAILABLE'), ('Occupied', 'OCCUPIED')], default=apartmentapp.models.RoomStatus['AVAILABLE'], max_length=20)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('amount', models.FloatField(default=0)),
                ('description', models.CharField(max_length=100)),
                ('payment_gateway', models.CharField(choices=[('Transfer', 'TRANSFER'), ('Stripe', 'STRIPE'), ('Momo', 'MOMO')], default=apartmentapp.models.PaymentGateway['TRANSFER'], max_length=20)),
                ('thumbnail', cloudinary.models.CloudinaryField(max_length=255, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VehicleCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('full_name', models.CharField(default='', max_length=100)),
                ('expiration_date', models.DateTimeField()),
                ('vehicle_number', models.CharField(max_length=20, unique=True)),
                ('relationship', models.CharField(choices=[('Apartment owner', 'APARTMENT_OWNER'), ('Relative', 'RELATIVE')], default=apartmentapp.models.Relationship['APARTMENT_OWNER'], max_length=30)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TransactionMonthlyFee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('amount', models.FloatField(default=0)),
                ('monthly_fee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apartmentapp.monthlyfee')),
                ('transaction', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apartmentapp.transaction')),
            ],
            options={
                'unique_together': {('monthly_fee', 'transaction')},
            },
        ),
        migrations.AddField(
            model_name='transaction',
            name='monthly_fees',
            field=models.ManyToManyField(related_name='transactions', through='apartmentapp.TransactionMonthlyFee', to='apartmentapp.monthlyfee'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='room',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apartmentapp.room'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='StorageLocker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('number', models.CharField(max_length=50)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Reflection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=100)),
                ('content', ckeditor.fields.RichTextField()),
                ('status', models.CharField(choices=[('Approved', 'APPROVED'), ('Solved', 'SOLVED'), ('Approving', 'APPROVING')], default=apartmentapp.models.ReflectionStatus['APPROVING'], max_length=20)),
                ('resolution', models.CharField(blank=True, max_length=255, null=True)),
                ('resolved_date', models.DateTimeField(null=True)),
                ('admin_resolved', models.CharField(max_length=255)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('sender_name', models.CharField(max_length=50)),
                ('recipient_name', models.CharField(max_length=50)),
                ('status', models.CharField(choices=[('Not received', 'NOT_RECEIVED'), ('Received', 'RECEIVED')], default=apartmentapp.models.PackageStatus['NOT_RECEIVED'], max_length=20)),
                ('pickup_time', models.DateTimeField(null=True)),
                ('quantity_items', models.IntegerField(default=1)),
                ('thumbnail', cloudinary.models.CloudinaryField(max_length=255, null=True)),
                ('description', ckeditor.fields.RichTextField()),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apartmentapp.storagelocker')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='monthlyfee',
            name='room',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apartmentapp.room'),
        ),
        migrations.CreateModel(
            name='PrivateNotification',
            fields=[
                ('commonnotification_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apartmentapp.commonnotification')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=('apartmentapp.commonnotification',),
        ),
        migrations.AlterUniqueTogether(
            name='monthlyfee',
            unique_together={('room', 'fee', 'created_date')},
        ),
    ]
