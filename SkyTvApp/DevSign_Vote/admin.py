from django.contrib import admin
from django.contrib.auth.admin import UserAdmin  
from .models import User

class CustomUserAdmin(UserAdmin):
    
    model = User
    list_display = ("email", "first_name", "last_name", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "role", "profile_image")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "password1", "password2", "role"),
        }),
    )

    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)  

admin.site.register(User, CustomUserAdmin)