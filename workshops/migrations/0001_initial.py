# Generated by Django 5.2 on 2025-04-07 08:06

import datetime
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkshopCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Category Name')),
                ('slug', models.SlugField(max_length=100, unique=True, verbose_name='URL Slug')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
            ],
            options={
                'verbose_name': 'Workshop Category',
                'verbose_name_plural': 'Workshop Categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Workshop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Title')),
                ('description', models.TextField(verbose_name='Description')),
                ('start_date', models.DateField(default=django.utils.timezone.now, verbose_name='Start Date')),
                ('start_time', models.TimeField(default=datetime.time(9, 0), verbose_name='Start Time')),
                ('duration', models.DecimalField(decimal_places=2, default=2.0, max_digits=5, validators=[django.core.validators.MinValueValidator(0.5)], verbose_name='Duration (hours)')),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Price')),
                ('capacity', models.PositiveIntegerField(default=15, verbose_name='Capacity')),
                ('location_type', models.CharField(choices=[('online', 'Online'), ('in_person', 'In Person'), ('hybrid', 'Hybrid (Online & In Person)')], default='online', max_length=20, verbose_name='Location Type')),
                ('location_address', models.CharField(blank=True, max_length=255, verbose_name='Location Address')),
                ('location_url', models.URLField(blank=True, help_text='Zoom/Meet link for online workshops', verbose_name='Location URL')),
                ('image', models.ImageField(blank=True, null=True, upload_to='workshops/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])], verbose_name='Cover Image')),
                ('requirements', models.TextField(blank=True, help_text='Equipment, prerequisites, etc.', verbose_name='Requirements')),
                ('agenda', models.TextField(blank=True, verbose_name='Workshop Agenda')),
                ('provides_certificate', models.BooleanField(default=False, verbose_name='Provides Certificate')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('is_published', models.BooleanField(default=True, verbose_name='Published')),
                ('is_featured', models.BooleanField(default=False, verbose_name='Featured')),
                ('instructor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='instructed_workshops', to=settings.AUTH_USER_MODEL, verbose_name='Instructor')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='workshops', to='workshops.workshopcategory', verbose_name='Category')),
            ],
            options={
                'verbose_name': 'Workshop',
                'verbose_name_plural': 'Workshops',
                'ordering': ['start_date', 'start_time'],
            },
        ),
        migrations.CreateModel(
            name='WorkshopRegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registered_at', models.DateTimeField(auto_now_add=True, verbose_name='Registered At')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled'), ('completed', 'Completed')], default='pending', max_length=20, verbose_name='Status')),
                ('payment_status', models.CharField(choices=[('unpaid', 'Unpaid'), ('pending', 'Pending'), ('paid', 'Paid'), ('refunded', 'Refunded')], default='unpaid', max_length=20, verbose_name='Payment Status')),
                ('payment_complete', models.BooleanField(default=False, verbose_name='Payment Complete')),
                ('is_cancelled', models.BooleanField(default=False, verbose_name='Cancelled')),
                ('attendance_confirmed', models.BooleanField(default=False, verbose_name='Attendance Confirmed')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workshop_registrations', to=settings.AUTH_USER_MODEL, verbose_name='User')),
                ('workshop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to='workshops.workshop', verbose_name='Workshop')),
            ],
            options={
                'verbose_name': 'Workshop Registration',
                'verbose_name_plural': 'Workshop Registrations',
                'ordering': ['-registered_at'],
                'unique_together': {('workshop', 'user')},
            },
        ),
    ]
