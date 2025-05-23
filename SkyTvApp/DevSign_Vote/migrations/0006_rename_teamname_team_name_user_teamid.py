# Generated by Django 5.1.7 on 2025-04-16 17:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DevSign_Vote', '0005_vote_comment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='team',
            old_name='TeamName',
            new_name='Name',
        ),
        migrations.AddField(
            model_name='user',
            name='TeamID',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='DevSign_Vote.team'),
        ),
    ]
