# Generated by Django 2.1.9 on 2019-06-16 02:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0005_auto_20190503_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='display_event',
            field=models.BooleanField(default=True),
        ),
    ]
