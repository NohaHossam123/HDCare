# Generated by Django 2.1 on 2020-06-29 15:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_confirmation_waiting'),
    ]

    operations = [
        migrations.AlterField(
            model_name='confirmation',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
