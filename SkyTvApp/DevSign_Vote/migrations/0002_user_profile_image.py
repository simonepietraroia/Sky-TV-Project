# Generated by Django 5.1.7 on 2025-03-14 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DevSign_Vote', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile_image',
            field=models.BinaryField(blank=True, null=True),
        ),
    ]
