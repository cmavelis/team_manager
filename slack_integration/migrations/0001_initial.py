# Generated by Django 2.1.7 on 2019-04-16 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InteractiveMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slack_message_ts', models.CharField(max_length=20)),
                ('player_id', models.IntegerField(blank=True, max_length=3)),
                ('event_id', models.IntegerField(blank=True, max_length=3)),
            ],
        ),
    ]
