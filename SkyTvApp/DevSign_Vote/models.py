from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission


class CustomUserManager(BaseUserManager):
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):

    username = None 
    email = models.EmailField(unique=True)

    ROLE_CHOICES = [
        ('engineer', 'Engineer'),
        ('team_leader', 'Team Leader'),
        ('department_leader', 'Department Leader'),
        ('senior_manager', 'Senior Manager'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='engineer')
    profile_image = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    
    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)

    USERNAME_FIELD = "email" 
    REQUIRED_FIELDS = []

    def is_team_leader(self):
        return self.role == "team_leader"

    def __str__(self):
        return f"{self.first_name} {self.last_name}" if self.first_name else self.email

class Department(models.Model):
    DepartmentID = models.AutoField(primary_key=True)
    DepartmentName = models.CharField(max_length=255)
    Manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="managed_departments")
    DateCreated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.DepartmentName

class Team(models.Model):
    TeamID = models.AutoField(primary_key=True)
    TeamName = models.CharField(max_length=255)
    DepartmentID = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="teams")
    DateCreated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.TeamName

class Session(models.Model):
    SessionID = models.AutoField(primary_key=True)
    UserID = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    StartTime = models.DateTimeField()
    EndTime = models.DateTimeField(null=True, blank=True)
    Status = models.CharField(max_length=50)
    CreatedBy = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_sessions")
    DateCreated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session {self.SessionID} - {self.Status}"

class Vote(models.Model):
    VoteID = models.AutoField(primary_key=True)
    TeamID = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="votes")
    UserID = models.ForeignKey(User, on_delete=models.CASCADE, related_name="votes")
    CardID = models.ForeignKey('HealthCard', on_delete=models.CASCADE, related_name="votes")
    SessionID = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="votes")
    VoteValue = models.IntegerField()
    Progress = models.CharField(max_length=50)
    TimeStamp = models.DateTimeField(auto_now_add=True)
    Comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Vote {self.VoteID} - {self.VoteValue}"

class HealthCard(models.Model):
    CardID = models.AutoField(primary_key=True)
    Description = models.TextField()
    Category = models.CharField(max_length=255)
    CreatedBy = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_health_cards")
    DateCreated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.Description

class AggregateVotes(models.Model):
    ReportID = models.AutoField(primary_key=True)
    TeamID = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="aggregated_votes")
    TotalRedVotes = models.IntegerField(default=0)
    TotalGreenVotes = models.IntegerField(default=0)
    TotalYellowVotes = models.IntegerField(default=0)
    TrendAnalysis = models.TextField()
    GeneratedBy = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="generated_reports")
    DateCreated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report {self.ReportID} - Team {self.TeamID}"

class TrendAnalysis(models.Model):
    TrendID = models.AutoField(primary_key=True)
    TeamID = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="trend_analyses")
    DepartmentID = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="trend_analyses")
    GeneratedBy = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="generated_trends")
    TrendSummary = models.TextField()
    AnalysisType = models.CharField(max_length=255)
    DateGenerated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Trend {self.TrendID} - {self.AnalysisType}"