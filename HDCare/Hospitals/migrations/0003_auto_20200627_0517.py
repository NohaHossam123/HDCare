# Generated by Django 3.0.7 on 2020-06-27 05:17

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Hospitals', '0002_auto_20200617_0001'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_book',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='user_book',
            unique_together=set(),
        ),
    ]