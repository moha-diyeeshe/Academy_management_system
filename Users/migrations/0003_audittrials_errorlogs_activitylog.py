# Generated by Django 5.1 on 2024-09-07 08:47

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0002_alter_users_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditTrials',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Avatar', models.FileField(upload_to='trials/')),
                ('Username', models.CharField(max_length=20)),
                ('path', models.CharField(blank=True, max_length=60, null=True)),
                ('Name', models.CharField(max_length=200)),
                ('Actions', models.CharField(max_length=400)),
                ('Module', models.CharField(max_length=400)),
                ('date_of_action', models.DateTimeField(auto_now_add=True)),
                ('operating_system', models.CharField(max_length=200)),
                ('browser', models.CharField(max_length=200)),
                ('ip_address', models.CharField(max_length=200)),
                ('user_agent', models.TextField(max_length=200)),
            ],
            options={
                'db_table': 'audittrials',
            },
        ),
        migrations.CreateModel(
            name='ErrorLogs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Username', models.CharField(db_index=True, max_length=20)),
                ('Name', models.CharField(db_index=True, max_length=500)),
                ('Expected_error', models.CharField(db_index=True, max_length=500)),
                ('field_error', models.CharField(db_index=True, max_length=500)),
                ('trace_back', models.TextField(max_length=500)),
                ('line_number', models.IntegerField(db_index=True)),
                ('date_recorded', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('browser', models.CharField(db_index=True, max_length=500)),
                ('ip_address', models.CharField(db_index=True, max_length=500)),
                ('user_agent', models.TextField(max_length=500)),
                ('Avatar', models.FileField(blank=True, null=True, upload_to='errorlogs/')),
            ],
            options={
                'db_table': 'errorlogs',
                'ordering': ['-date_recorded'],
            },
        ),
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=255)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('content_type', models.CharField(max_length=255)),
                ('object_id', models.PositiveIntegerField()),
                ('description', models.TextField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
