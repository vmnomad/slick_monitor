# Generated by Django 2.2.5 on 2019-11-26 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setup', '0002_auto_20191126_0831'),
    ]

    operations = [
        migrations.CreateModel(
            name='Loggers',
            fields=[
                ('type', models.CharField(max_length=100, primary_key=True, serialize=False, unique=True)),
                ('settings', models.CharField(max_length=1000, unique=True)),
            ],
            options={
                'db_table': 'LOGGERS',
            },
        ),
    ]
