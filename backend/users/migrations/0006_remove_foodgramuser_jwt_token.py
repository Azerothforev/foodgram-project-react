# Generated by Django 3.2 on 2023-06-22 20:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_foodgramuser_jwt_token'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='foodgramuser',
            name='jwt_token',
        ),
    ]
