# Generated by Django 2.1 on 2020-06-29 13:23

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Hospitals', '0004_merge_20200628_1317'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='user_book',
            unique_together={('book', 'user')},
        ),
    ]
