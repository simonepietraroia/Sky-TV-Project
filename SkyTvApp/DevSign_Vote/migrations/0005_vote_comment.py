# Generated by Django 5.1.7 on 2025-04-16 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DevSign_Vote', '0004_remove_user_username_alter_user_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='Comment',
            field=models.TextField(blank=True, null=True),
        ),
    ]
