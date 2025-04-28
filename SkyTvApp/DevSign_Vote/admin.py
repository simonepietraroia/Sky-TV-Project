from django.contrib import admin
from django.contrib.auth.admin import UserAdmin  
from .models import User, Team, Department, Session, HealthCard, Vote

class CustomUserAdmin(UserAdmin):
    list_display = ('first_name', 'last_name', 'email', 'role')  
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('first_name',)  

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'role', 'profile_image', 'TeamID', 'DepartmentID')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2')}
        ),
    )
    

admin.site.register(User, CustomUserAdmin)
admin.site.register(Team)
admin.site.register(Department)
admin.site.register(Session)
admin.site.register(HealthCard)
admin.site.register(Vote)
