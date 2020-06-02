# Generated by Django 2.1 on 2020-06-02 20:31

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20200601_2109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(blank=True, max_length=11, null=True, unique=True, validators=[django.core.validators.RegexValidator(message='Sorry, Only Egyptian Phones are allowed...', regex='^(01)[012][0-9]{8}')]),
        ),
    ]
