# Generated by Django 2.2.5 on 2019-12-11 21:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitors', '0010_states'),
    ]

    operations = [
        migrations.RenameField(
            model_name='states',
            old_name='monitor_id',
            new_name='monitor',
        ),
    ]
