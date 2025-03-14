from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
    ROLE_CHOICES = [
        ('engineer', 'Engineer'),
        ('team_leader', 'Team Leader'),
        ('department_leader', 'Department Leader'),
        ('senior_manager', 'Senior Manager'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='engineer')

    profile_image = models.BinaryField(null=True, blank=True)

    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)

    def is_team_leader(self):
        return self.role == 'team_leader'

class HealthCheckSession(models.Model):
    name = models.CharField(max_length=100, unique=True, primary_key=True)  
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
