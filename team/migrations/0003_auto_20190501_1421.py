# Generated by Django 2.1.7 on 2019-05-01 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0002_auto_20190501_1259'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='nickname',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
