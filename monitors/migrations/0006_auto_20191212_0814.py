# Generated by Django 2.2.5 on 2019-12-11 21:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('monitors', '0005_auto_20191212_0809'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='states',
            name='id',
        ),
        migrations.AlterField(
            model_name='states',
            name='monitor_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='monitors.Monitors'),
        ),
    ]