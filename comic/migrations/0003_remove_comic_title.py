# Generated by Django 5.0.8 on 2024-08-15 18:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comic', '0002_alter_comic_goal_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comic',
            name='title',
        ),
    ]
