# Generated by Django 2.2.5 on 2019-12-11 21:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('monitors', '0014_delete_states'),
    ]

    operations = [
        migrations.CreateModel(
            name='States',
            fields=[
                ('monitor', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='monitors.Monitors')),
                ('state', models.IntegerField()),
            ],
            options={
                'db_table': 'STATES',
            },
        ),
    ]
