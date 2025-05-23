# Generated by Django 5.1.7 on 2025-03-19 21:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DevSign_Vote', '0002_user_profile_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='AggregateVotes',
            fields=[
                ('ReportID', models.AutoField(primary_key=True, serialize=False)),
                ('TotalRedVotes', models.IntegerField(default=0)),
                ('TotalGreenVotes', models.IntegerField(default=0)),
                ('TotalYellowVotes', models.IntegerField(default=0)),
                ('TrendAnalysis', models.TextField()),
                ('DateCreated', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('DepartmentID', models.AutoField(primary_key=True, serialize=False)),
                ('DepartmentName', models.CharField(max_length=255)),
                ('DateCreated', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='HealthCard',
            fields=[
                ('CardID', models.AutoField(primary_key=True, serialize=False)),
                ('Description', models.TextField()),
                ('Category', models.CharField(max_length=255)),
                ('DateCreated', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('SessionID', models.AutoField(primary_key=True, serialize=False)),
                ('StartTime', models.DateTimeField()),
                ('EndTime', models.DateTimeField(blank=True, null=True)),
                ('Status', models.CharField(max_length=50)),
                ('DateCreated', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('TeamID', models.AutoField(primary_key=True, serialize=False)),
                ('TeamName', models.CharField(max_length=255)),
                ('DateCreated', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='TrendAnalysis',
            fields=[
                ('TrendID', models.AutoField(primary_key=True, serialize=False)),
                ('TrendSummary', models.TextField()),
                ('AnalysisType', models.CharField(max_length=255)),
                ('DateGenerated', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('VoteID', models.AutoField(primary_key=True, serialize=False)),
                ('VoteValue', models.IntegerField()),
                ('Progress', models.CharField(max_length=50)),
                ('TimeStamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.DeleteModel(
            name='HealthCheckSession',
        ),
        migrations.AlterField(
            model_name='user',
            name='profile_image',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pics/'),
        ),
        migrations.AddField(
            model_name='aggregatevotes',
            name='GeneratedBy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='generated_reports', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='department',
            name='Manager',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='managed_departments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='healthcard',
            name='CreatedBy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_health_cards', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='session',
            name='CreatedBy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_sessions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='session',
            name='UserID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='team',
            name='DepartmentID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teams', to='DevSign_Vote.department'),
        ),
        migrations.AddField(
            model_name='aggregatevotes',
            name='TeamID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aggregated_votes', to='DevSign_Vote.team'),
        ),
        migrations.AddField(
            model_name='trendanalysis',
            name='DepartmentID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trend_analyses', to='DevSign_Vote.department'),
        ),
        migrations.AddField(
            model_name='trendanalysis',
            name='GeneratedBy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='generated_trends', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='trendanalysis',
            name='TeamID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trend_analyses', to='DevSign_Vote.team'),
        ),
        migrations.AddField(
            model_name='vote',
            name='CardID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='DevSign_Vote.healthcard'),
        ),
        migrations.AddField(
            model_name='vote',
            name='SessionID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='DevSign_Vote.session'),
        ),
        migrations.AddField(
            model_name='vote',
            name='TeamID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='DevSign_Vote.team'),
        ),
        migrations.AddField(
            model_name='vote',
            name='UserID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to=settings.AUTH_USER_MODEL),
        ),
    ]
